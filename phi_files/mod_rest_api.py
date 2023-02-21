import orthanc
import json
import re
import pprint
import datetime
import os
import smtplib
import time
from email.message import EmailMessage
from email.headerregistry import Address
try:
    from bs4 import BeautifulSoup
    flag_beautiful_soup = True
except:
    flag_beautiful_soup = False
try:
    import psycopg2
    flag_psycopg2 = True
except:
    flag_psycopg2 = False

# Regular expressions
address_re = re.compile('([^<]+)<([^@]+)@([^>]+)>.*')

# Common variables
website = os.getenv('ORTHANC__NAME', default='UnknownOrthanc')
fqdn = os.getenv('HOST_FQDN', default='Unknown.Host')

# ============================================================================
def anonymize_study(orthanc_study_id):
    """Replaces the lua AnonymizeStudy"""
# ----------------------------------------------------------------------------

    response_system = orthanc.RestApiGet('/system')
    meta_system = json.loads(response_system)
    aet = meta_system['DicomAet']

    response_post = orthanc.RestApiPost('/tools/execute-script', 'gIndent=0')
    response_post = orthanc.RestApiPost('/tools/execute-script', 'gFlagForceAnon=true')
    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    meta_study = json.loads(response_study)
    if ('ModifiedFrom' not in meta_study) and ('AnonymizedFrom' not in meta_study):
        orthanc.LogWarning('Non-anonymized study stable.  Initiating auto anon')
        email_message('%s Triggered Anonymization' % aet, 'Manual anonymization triggered.  Look for an update upon completion.')
        response_post = orthanc.RestApiPost('/tools/execute-script', 'OnStableStudyMain(\'%s\', nil, nil)' % orthanc_study_id)
    else:
        email_message('%s Triggered Anonymization' % aet, 'Manual anonymization triggered on anonymized data.  Skipping further anonymization.')
        orthanc.LogWarning('Already anonymized data.  Skipping reanon')
    response_post = orthanc.RestApiPost('/tools/execute-script', 'gFlagForceAnon=false')

# ============================================================================
def check_xref_modality():
    """Check for environmental variable defining xref modality"""
# ----------------------------------------------------------------------------

    flag_xref_modality=False
    xref_modality=None
    if 'LUA_XREF_MODALITY' in os.environ:
        for modality in json.loads(orthanc.RestApiGet('/modalities')):
            if modality == os.environ['LUA_XREF_MODALITY']:
                flag_xref_modality = True
                xref_modality = modality
                break

    return flag_xref_modality, xref_modality

# ============================================================================
def confirm_or_create_lookup_table_sql(pg_connection=None, pg_cursor=None):
    """Confirm existence of our lookup table in the database and create if necessary"""
# ----------------------------------------------------------------------------

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database()
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            return {'status':1, 'error_text': 'confirm_or_create_lookup_table: Must provide both con and cur'}

    # Check for existence of key table
    sql_query = "SELECT count(*) " + \
                "FROM information_schema.tables " + \
                "WHERE table_name='patientid'"
    try:
        pg_cursor.execute(sql_query)
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':1, 'error_text':'confirm_or_create_lookup_table: Problem querying for patientid table'}

    if pg_cursor.rowcount != 1:
        status = create_lookup_table_sql(pg_connection=pg_connection, 
                                         pg_cursor = pg_cursor)
        if status['status'] != 0:
            if flag_local_db:
                pg_connection.rollback()
                pg_cursor.close()
                pg_connection.close()
            return status

    if flag_local_db:
        pg_cursor.close()
        pg_connection.commit()
        pg_connection.close()
    return {'status': 0}
        
# ============================================================================
def connect_to_database():
    """Make connection to our postgres database"""
# ----------------------------------------------------------------------------

    if 'ORTHANC__POSTGRESQL__USERNAME' not in os.environ or \
        'ORTHANC__POSTGRESQL__PASSWORD' not in os.environ or \
        'ORTHANC__POSTGRESQL__HOST' not in os.environ:
        return {'status': 3, 
                'error_text': 'Environmental variables for postgres not declared'}

    # Get the login parameters
    pg_username = os.environ['ORTHANC__POSTGRESQL__USERNAME']
    pg_password = os.environ['ORTHANC__POSTGRESQL__PASSWORD']
    pg_host = os.environ['ORTHANC__POSTGRESQL__HOST']
    pg_port = 5432
    
    error_status = 1
    # Open a connection
    try:
        pg_connection = psycopg2.connect(host=pg_host,
                                         dbname='philookup',
                                         user=pg_username,
                                         password=pg_password)
    except:
        return {'status':error_status, 
                'error_text':'connect_to_database: Problem connecting to database'}, None, None

    # Setup cursor
    error_status += 1
    try:
        pg_cursor = pg_connection.cursor()
    except:
        if pg_connection is not None:
            pg_connection.close()
        return {'status':error_status, 
                'error_text':'connect_to_database: Something went wrong with cursor creation'}, None, None

    return {'status':0}, pg_connection, pg_cursor

# ============================================================================
def construct_patient_name(internal_number, patient_name_base=None, patient_name_id=None):
# ----------------------------------------------------------------------------
    if patient_name_base is None:
        response_system = orthanc.RestApiGet('/system')
        meta_system = json.loads(response_system)
        local_patient_name_base = meta_system['Name']
    else:
        local_patient_name_base = patient_name_base

    if patient_name_id is None:
        local_patient_name_id = 'ID'
    else:
        local_patient_name_id = patient_name_id

    patient_name = '%s^%s%06d^^^' % (local_patient_name_base, local_patient_name_id, internal_number)

    return patient_name
              
# ============================================================================
def create_lookup_table_sql(pg_connection=None, pg_cursor=None):
    """Create the lookup tables"""
# ----------------------------------------------------------------------------

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database()
        flag_local_db = True 
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            return {'status':1, 'error_text': 'create_lookup_table_sql: Must provide both con and cur'}
    
    table_names = ['patientid', 'patientid_anon', 
                   'studyinstanceuid', 'studyinstanceuid_anon', 'siuid2patientname_anon',
                   'shiftepoch',
                   'internalnumber']
    table_creation = {'patientid'             : 'CREATE TABLE patientid(' + \
                                                    'pid SERIAL PRIMARY KEY, ' + \
                                                    'value text UNIQUE NOT NULL, ' + \
                                                    'parent_pid INTEGER DEFAULT NULL, ' + \
                                                    'FOREIGN KEY (parent_pid) REFERENCES patientid(pid))',
                     'patientid_anon'         : 'CREATE TABLE patientid_anon(' + \
                                                    'pid_a SERIAL PRIMARY KEY, ' + \
                                                    'value text UNIQUE NOT NULL, ' + \
                                                    'pid integer REFERENCES patientid)',
                     'studyinstanceuid'       : 'CREATE TABLE studyinstanceuid(' + \
                                                    'siuid SERIAL PRIMARY KEY, ' + \
                                                    'value text UNIQUE NOT NULL, ' + \
                                                    'pid integer REFERENCES patientid)',
                     'studyinstanceuid_anon'  : 'CREATE TABLE studyinstanceuid_anon(' + \
                                                    'siuid_a SERIAL PRIMARY KEY, ' + \
                                                    'value text UNIQUE NOT NULL, ' + \
                                                    'siuid integer REFERENCES studyinstanceuid (siuid))',
                     'siuid2patientname_anon' : 'CREATE TABLE siuid2patientname_anon(' + \
                                                    'pna_id SERIAL PRIMARY KEY, ' + \
                                                    'patientname_anon text, ' + \
                                                    'timestamp TIMESTAMP, ' + \
                                                    'siuid integer REFERENCES studyinstanceuid (siuid))',
                     'shiftepoch'             : 'CREATE TABLE shiftepoch(' + \
                                                    'se SERIAL PRIMARY KEY, ' + \
                                                    'value integer DEFAULT 0, ' + \
                                                    'pid integer REFERENCES patientid)',
                     'internalnumber'         : 'CREATE TABLE internalnumber(' + \
                                                    'inid SERIAL PRIMARY KEY, ' + \
                                                    'value integer UNIQUE NOT NULL, ' + \
                                                    'pid integer REFERENCES patientid)'}
                   
    code = 2
    for table_name in table_names:
        sql_statement = table_creation[table_name]
        try:
            pg_cursor.execute(sql_statement)
        except:
            pg_connection.rollback()
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            return {'status': code, 'error_text': 'create_lookup_table_sql: Problem creating table %s' % table_name}
        code += 1

    pg_connection.commit()

    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

# =======================================================
def email_message(subject, message_body, subtype='plain', alternates=None, cc=None):
    """
        PURPOSE: Send email to addresses specified in env var PYTHON_MAIL_TO
        INPUT:   subject - string, of email
                 message_body - string text of email body
                 subtype - string, type of email
                     html - html body
                     plain - plain body
                 alternates - string, provide alternate main recipients to
                     those taken from PYTHON_MAIL_TO in the environment
                 cc - string, additional addresses to be CCed
                     "first last <first.last@some.org>"
    """
# -------------------------------------------------------
 
    if alternates is None:
        if 'PYTHON_MAIL_TO' not in os.environ or \
           'PYTHON_MAIL_ORIGIN' not in os.environ or \
           'PYTHON_MAIL_SERVER' not in os.environ:
            return{'status':1, 'error_text': 'Environmental variables for python mail not declared'}
        recipients = os.getenv('PYTHON_MAIL_TO').split(',')
    else:
        if 'PYTHON_MAIL_ORIGIN' not in os.environ or \
           'PYTHON_MAIL_SERVER' not in os.environ:
            return{'status':2, 'error_text': 'Environmental variables for python mail not declared'}
        recipients = alternates

    response_system = orthanc.RestApiGet('/system')
    meta_system = json.loads(response_system)
    aet = meta_system['DicomAet']

    addresses = []
    for address_text in recipients:
        address_trim = address_text.strip()
        address_res = address_re.match(address_trim)
        if address_res is not None:
            addresses += [Address(address_res.group(1),address_res.group(2),address_res.group(3))]
    if cc is not None:
        for address_text in cc.split(','):
            address_trim = address_text.strip()
            address_res = address_re.match(address_trim)
            if address_res is not None:
                addresses += [Address(address_res.group(1),address_res.group(2),address_res.group(3))]
        
    if len(addresses) == 0:
        return {'status':3, 'error_text':'email_message: No addresses to send to'}
    else:
        addresses = tuple(addresses)

    msg = EmailMessage()
    msg.set_content(message_body, subtype=subtype)
    msg['Subject'] = subject
    msg['From'] = Address(aet, os.environ['PYTHON_MAIL_SENDER'], os.environ['PYTHON_MAIL_ORIGIN'])
    msg['To'] = addresses

    smtp_server = os.environ['PYTHON_MAIL_SERVER']
    s = smtplib.SMTP(smtp_server)
    s.send_message(msg)
    s.quit()

    return {'status':0}

# =======================================================
def email_study_report(orthanc_study_id):
    """Generate email of study statistics"""
# -------------------------------------------------------

    response_system = orthanc.RestApiGet('/system')
    meta_system = json.loads(response_system)
    aet = meta_system['DicomAet']

    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    meta_study = json.loads(response_study)
    if 'StudyDescription' in meta_study['MainDicomTags'] and len(meta_study['MainDicomTags']['StudyDescription'].strip()) > 0:
        study_description = meta_study['MainDicomTags']['StudyDescription']
    else:
        study_description = orthanc_study_id

    flag_anonymized = 'AnonymizedFrom' in meta_study

    if flag_anonymized and \
        ('PatientName' in meta_study['PatientMainDicomTags'] and \
         len(meta_study['PatientMainDicomTags']['PatientName'].strip()) > 0):
        patient_name = meta_study['PatientMainDicomTags']['PatientName']
        orthanc_patient_id = meta_study['ParentPatient']
    else:
        patient_name = 'None'

    response_statistics = orthanc.RestApiGet('/studies/%s/statistics' % orthanc_study_id)
    meta_statistics = json.loads(response_statistics)

    message_body = ['<html>', ' '*2 + '<head></head>', ' '*2 + '<body>']
    message_body += [' '*4 + '<h1>Study Report</h1>']
    message_body += [' '*4 + '<h2>Study Info</h2>']
    if flag_anonymized:
        message_body += [' '*4 + '<p style="color:green">This study is the result of an anonymization!</p>']
 
    # Main study info
    message_body += [' '*4 + '<table border=1>']
    message_body += [' '*6 + '<tr><th>Item</th><th>Value</th></tr>']
    message_body += [' '*6 + '<tr><td>Study</td><td><a href="https://%s/%s/app/explorer.html#study?uuid=%s">%s</a></td></tr>' % (fqdn, website, orthanc_study_id,study_description)]
    if flag_anonymized:
        message_body += [' '*6 + '<tr><td>Patient</td><td><a href="https://%s/%s/app/explorer.html#patient?uuid=%s">%s</a></td></tr>' % (fqdn, website, orthanc_patient_id,patient_name)]

    for key in ['InstitutionName', 'ReferringPhysicianName']:
        if key in meta_study['MainDicomTags']:
            value = meta_study['MainDicomTags'][key]
            message_body += [' '*6 + '<tr><td>%s</td><td>%s</td></tr>' % (key, value)]
    for key, value in meta_statistics.items():
        message_body += [' '*6 + '<tr><td>%s</td><td>%s</td></tr>' % (key, value)]
    message_body += [' '*4 + '</table>']

    # Series info
    message_body += [' '*4 + '<h2>Series Info</h2>']
    message_body += [' '*4 + '<table border=1>']
    message_body += [' '*6 + '<tr><th>Series</th><th>Instances</th><th>Station</th><th>Anatomy</th><th>Description</th></tr>']
    series_data = {}
    for orthanc_series_id in meta_study['Series']:
        response_series = orthanc.RestApiGet('/series/%s' % orthanc_series_id)
        meta_series = json.loads(response_series)
        series_number = int(meta_series['MainDicomTags']['SeriesNumber'])
        for key in ['Instances', 'StationName', 'BodyPartExamined', 'SeriesDescription']:
            if series_number not in series_data:
                series_data[series_number] = {'orthanc_series_id':orthanc_series_id}
            if key == 'Instances':
                series_data[series_number][key] = len(meta_series[key])
            else:
                if key in meta_series['MainDicomTags']:
                    series_data[series_number][key] = meta_series['MainDicomTags'][key].strip()
                else:
                    series_data[series_number][key] = ''

    series_numbers = list(series_data.keys())
    series_numbers.sort()

    for series_number in series_numbers:
        line_of_text = ' '*6 + '<tr>'
        line_of_text += '<td align="center">%d</td>' % series_number
        line_of_text += '<td align="center">%d</td>' % series_data[series_number]['Instances']
        for key in ['StationName', 'BodyPartExamined', 'SeriesDescription']:
            if key == 'SeriesDescription' and len(series_data[series_number][key]) > 0:
                line_of_text += '<td><a href="https://%s/%s/app/explorer.html#series?uuid=%s">%s</a></td>' % (fqdn, website, series_data[series_number]['orthanc_series_id'],series_data[series_number][key])
            else:
                line_of_text += '<td>%s</td>' % series_data[series_number][key]
        line_of_text += '</tr>'
        message_body += [line_of_text]

    message_body += [' '*2 + '</body>', '</html>']
    return email_message('PHI Study Report from %s' % aet, '\n'.join( message_body), subtype='html')

# ============================================================================
def find_pacs_in_lookup_table(lookup_table, id_to_match, type_match='siuid'):
    """Search the lookup table dict for matching id"""
# ----------------------------------------------------------------------------

    pacs_data = None
    found = False
    if type_match == 'siuid':
        found, i_row_match = find_pacs_in_lookup_table_from_siuid(lookup_table, id_to_match)
    if type_match == 'patientid':
        found, i_row_match = find_pacs_in_lookup_table_from_patient_id(lookup_table, id_to_match)
    if not found:
        return found, pacs_data

    #orthanc.LogWarning('%d %d' % (found, i_row_match))
    patient_name = None
    if i_row_match in lookup_table['Name']:
        if isinstance(lookup_table['Name'][i_row_match], list):
            patient_name = ','.join(lookup_table['Name'][i_row_match])
        else:
            patient_name = lookup_table['Name'][i_row_match]
        if patient_name is not None:
            if pacs_data is None:
                pacs_data = {}
            pacs_data['0010,0010'] = {'Value': patient_name}

    patient_id = None
    if i_row_match in lookup_table['PatientID']:
        if isinstance(lookup_table['PatientID'][i_row_match], list):
            patient_id = ','.join(lookup_table['PatientID'][i_row_match])
        else:
            patient_id = lookup_table['PatientID'][i_row_match]
        if patient_id is not None:
            if pacs_data is None:
                pacs_data = {}
            pacs_data['0010,0020'] = {'Value': patient_id}

    study_date = None
    if i_row_match in lookup_table['Date']:
        if isinstance(lookup_table['Date'][i_row_match], list):
            study_date = ','.join(lookup_table['Date'][i_row_match])
        else:
            study_date = lookup_table['Date'][i_row_match]
        if study_date is not None:
            anon_date = None
            if 'Anon Date' in lookup_table and i_row_match in lookup_table['Anon Date']:
                if isinstance(lookup_table['Anon Date'][i_row_match], list):
                    anon_date = ','.join(lookup_table['Anon Date'][i_row_match])
                else:
                    anon_date = lookup_table['Anon Date'][i_row_match]
            if pacs_data is None:
                pacs_data = {}
            pacs_data['0008,0020'] = {'Value': study_date}
            if anon_date is not None:
                pacs_data['AnonDate'] = anon_date

    accession_number = None
    if i_row_match in lookup_table['Accession']:
        if isinstance(lookup_table['Accession'][i_row_match], list):
            accession_number = ','.join(lookup_table['Accession'][i_row_match])
        else:
            accession_number = lookup_table['Accession'][i_row_match]
        if accession_number is not None:
            if pacs_data is None:
                pacs_data = {}
            pacs_data['0008,0050'] = {'Value': accession_number}


    if pacs_data is None:
        found = False
    else:
        found = True

    return found, pacs_data

# ============================================================================
def find_pacs_in_lookup_table_from_patient_id(lookup_table, patient_id):
    """Search the lookup table dict for patient matching patient_id"""
# ----------------------------------------------------------------------------

    for i_row_temp, patient_id_list in lookup_table['PatientID'].items():
        i_row_match = i_row_temp
        if isinstance(patient_id_list, list):
            found = patient_id in patient_id_list
        else:
            found = patient_id == patient_id_list
        if found:
            break

    return found, i_row_match

# ============================================================================
def find_pacs_in_lookup_table_from_siuid(lookup_table, study_instance_uid):
    """Search the lookup table dict for study matching study_instance_uid"""
# ----------------------------------------------------------------------------

    for i_row_temp, study_instance_uid_list in lookup_table['StudyInstanceUID'].items():
        i_row_match = i_row_temp
        if isinstance(study_instance_uid_list, list):
            found = study_instance_uid in study_instance_uid_list
            #orthanc.LogWarning('%d %s %s' % (found, study_instance_uid, ' '.join(study_instance_uid_list)))
        else:
            found = study_instance_uid == study_instance_uid_list
            #orthanc.LogWarning('%d %s %s' % (found, study_instance_uid, study_instance_uid_list))
        if found:
            break

    return found, i_row_match

# ============================================================================
def get_internal_number(sql_pid, patient_id_modifier,
                        pg_connection=None, pg_cursor=None):
# ----------------------------------------------------------------------------

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database()
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            return status, None
    else:
        if pg_connection is None or pg_cursor is None:
            return {'status':1, 'error_text': 'get_internal_number: Must provide both con and cur'}, None

    sql_query = "SELECT value FROM internalnumber WHERE pid=%s" 
    try:
        pg_cursor.execute(sql_query, (sql_pid,))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':1, 'error_text':'get_internal_number: Problem querying for patientid table'}, None

    if pg_cursor.rowcount > 0:
       row = pg_cursor.fetchone()
       internal_number = int(row[0])
       return {'status': 0}, internal_number
    else:

        internal_number = None
        internal_number_new = None
        internal_number_type = os.getenv('LUA_INTERNAL_NUMBER_TYPE', default='random')

        while internal_number is None:

            if internal_number_type == 'random':
                internal_number_new = randrange(1,999999)
            elif internal_number_type == 'monotonic':
                if internal_number_new is None:
                    internal_number_new = 1
                else:
                    internal_number_new += 1
            elif internal_number_type == 'winkler':
                internal_number_offset = 1000
                if internal_number_new is None:
                    if patient_id_modifier in ['s','2d']:
                        internal_number_new = 1
                    else:
                        internal_number_new = internal_number_offset+1
                else:
                    internal_number_new += 1
                if internal_number_new % internal_number_offset == 0:
                    internal_number_new += internal_number_offset + 1
            # Default: same as incoming sql_pid
            else:
                internal_number = sql_pid
                break

            if internal_number_new > 999999:
                pg_connection.rollback()
                if flag_local_db:
                    pg_cursor.close()
                    pg_connection.close()
                return {'status': 4, 'error_text': 'get_internal_number: Internal number overrun'}, None

            sql_query = "SELECT count(*) FROM internalnumber WHERE value=%s"
            try:
                pg_cursor.execute(sql_query, (internal_number_new,))
            except:
                pg_connection.rollback()
                if flag_local_db:
                    pg_cursor.close()
                    pg_connection.close()
                return {'status':2, 'error_text':'get_internal_number: querying new internal number'}, None
            row = pg_cursor.fetchone()
            if row is not None and int(row[0]) == 0:
                internal_number = internal_number_new
                break
                    
        # Save the internal number to the database
        sql_statement = "INSERT INTO internalnumber (value,pid) VALUES(%s,%s)"
        try:
            pg_cursor.execute(sql_statement, (internal_number, sql_pid))
        except:
            pg_connection.rollback()
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            return {'status': 3, 'error_text': 'get_internal_number: Problem saving the internal number'}, None
        pg_connection.commit()

    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    return {'status': 0}, internal_number
 
# ============================================================================
def get_remote_user(request_headers):
# ----------------------------------------------------------------------------

    if 'x-remote-user' in request_headers:
        remote_user = request_headers['x-remote-user']
    elif 'user-agent' in request_headers:
        remote_user = request_headers['user-agent']
    else:
        remote_user = ''
        for key,value in request_headers.items():
            remote_user = '%s %s.%s' % (remote_user, key, value)

    return remote_user

# ============================================================================
def load_lookup_table(file_lookup, make_backup=False):
    """Parse the lookup table.  Make backup if directed."""
# ----------------------------------------------------------------------------

    if not os.path.exists(file_lookup):
        return {'status': 0}, None

    if not flag_beautiful_soup:
        return {'status':1, 'error_text':'load_lookup_table: No Beautiful soup'}, None

    try:
        with open(file_lookup, 'r') as lun:
            lookup_text = lun.read()
    except: 
        return {'status':2, 'error_text':'load_lookup_table: Problem reading lookup'}, None

    # Make backup
    if make_backup:
        datetime_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        with open('%s.%s' % (file_lookup, datetime_str), 'w') as lun:
            lun.write(lookup_text)

    # Convert to BeautifulSoup for parsing
    soup = BeautifulSoup(lookup_text, 'html.parser')
    try:
        head = soup.find('head')
    except: 
        return {'status':3, 'error_text':'load_lookup_table: No head found'}, None

    try:
        table = soup.find('table')
    except AttributeError as e:
        print ('No tables found, exiting')
        sys.exit(1)
    
    try:
        rows = table.find_all('tr')
    except AttributeError as e:
        print ('No table rows found, exiting')
        sys.exit(2)
    
    lookup_table = {}
    table_headers = []
    for table_header in rows[0].find_all('th'):
        table_headers += [table_header.get_text().strip()]
        lookup_table[table_headers[-1]] = {}

    i_row = 0
    for row in rows[1:]:

        i_col = 0
        for table_datum in row.find_all('td'):
           
            table_datum_strip = table_datum.get_text().strip()
            entry_data = None
            if table_datum_strip.find(',') >= 0:
                entry_data = []
                for sub_datum in table_datum_strip.split(','):
                    if len(sub_datum.strip().strip('\n')) > 0:
                        entry_data += [sub_datum.strip()]
                if len(entry_data) == 1:
                    entry_data = entry_data[0]
            else:
                if len(table_datum_strip.strip('\n')) > 0:
                    entry_data = table_datum_strip.strip('\n')

            if entry_data is None:
                lookup_table[table_headers[i_col]][i_row] = None
            else:
                lookup_table[table_headers[i_col]][i_row] = entry_data

            i_col += 1

        i_row += 1

    return {'status':0}, lookup_table

# ============================================================================
def load_phi_to_anon_map(pg_connection=None, pg_cursor = None):
    """Query the postgres database for phi to anon maps"""
# ----------------------------------------------------------------------------

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database()
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            return status, None, None, None
    else:
        if pg_connection is None or pg_cursor is None:
            return {'status':1, 'error_text': 'load_phi_to_anon_map: Must provide both con and cur'}, None, None, None

    # Confirm our lookup tables
    status = confirm_or_create_lookup_table_sql(pg_connection=pg_connection,
                                                pg_cursor=pg_cursor)
    if status['status'] != 0:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return status, None, None, None
       
    # Setup
    patient_map = {}
    patient_reverse_map = {'Primary': {}, 
                           'Secondary': {},
                           'Both': {}}

    # Check for siuid2patientname_anon
    sql_query = "SELECT table_name " + \
                "FROM information_schema.tables " + \
                "WHERE table_name='siuid2patientname_anon'"
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return{'status': 1, 'error_text': 'load_phi_to_anon_map: Something went wrong querying for siuid2patientname_anon'}, None, None, None

    flag_siuid_to_anon = pg_cursor.rowcount > 0

    # Get PatientID
    sql_query = "SELECT pid,value FROM patientid WHERE parent_pid is NULL"
    error_status = 1
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status': error_status,
                'error_text':'load_phi_to_anon_map: Something went wrong with the patientid parent_pid query'}, None, None, None
    row = pg_cursor.fetchone()
    while row is not None:
        pid = row[0]
        patient_id = row[1]
        patient_map[pid] = {'PatientID': patient_id,
                            'OtherPatientIDs' : [],
                            'StudyInstanceUIDMap' : {}}
        if flag_siuid_to_anon:
             patient_map[pid]['SIUID2NameAnonMap'] = {}
        patient_reverse_map['Primary'][patient_id] = pid
        patient_reverse_map['Both'][patient_id] = pid
        row = pg_cursor.fetchone()
        
    sql_query = "SELECT parent_pid,value FROM patientid WHERE parent_pid is not NULL"
    error_status += 1
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':error_status, 'error_text':'load_phi_to_anon_map: Problem querying parent_pid'}, None, None, None
    row = pg_cursor.fetchone()
    while row is not None:
        parent_pid = row[0]
        patient_id = row[1]
        if parent_pid in patient_map:
            if patient_id not in patient_map[parent_pid]['OtherPatientIDs']:
                patient_map[parent_pid]['OtherPatientIDs'] += [patient_id]
            patient_reverse_map['Secondary'][patient_id] = parent_pid
            patient_reverse_map['Both'][patient_id] = parent_pid
        row = pg_cursor.fetchone()

    sql_query = "SELECT value, pid FROM patientid_anon"
    error_status += 1
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':error_status, 'error_text':'load_phi_to_anon_map: Problem querying patientid_anon'}, None, None, None
    row = pg_cursor.fetchone()
    while row is not None:
        patient_id_anon = row[0]
        pid = row[1]
        if pid in patient_map:
            patient_map[pid]['PatientIDAnon'] = patient_id_anon
        row = pg_cursor.fetchone()

    # Get the shift epoch
    sql_query = "SELECT value, pid FROM shiftepoch"
    error_status += 1
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':error_status, 'error_text':'load_phi_to_anon_map: Problem querying shiftepoch'}, None, None, None
    row = pg_cursor.fetchone()
    while row is not None:
        shift_epoch = row[0]
        pid = row[1]
        if pid in patient_map:
            patient_map[pid]['ShiftEpoch'] = shift_epoch
        row = pg_cursor.fetchone()
 
    # Get the internal number
    sql_query = "SELECT value, pid FROM internalnumber"
    error_status += 1
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':error_status, 'error_text':'load_phi_to_anon_map: Problem querying internalnumber'}, None, None, None
    row = pg_cursor.fetchone()
    while row is not None:
        internal_number = int(row[0])
        pid = row[1]
        if pid in patient_map:
            patient_map[pid]['InternalNumber'] = internal_number
        row = pg_cursor.fetchone()

    # Gather the study info
    sql_query = "SELECT sphi.pid AS pidvalue, sphi.value AS phivalue, sanon.value AS anonvalue " + \
                "FROM studyinstanceuid sphi " + \
                "   INNER JOIN studyinstanceuid_anon sanon " + \
                "   ON sanon.siuid = sphi.siuid"
    error_status += 1
    try:
        pg_cursor.execute(sql_query)
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return {'status':error_status, 'error_text':'load_phi_to_anon_map: Problem querying study info'}, None, None, None
    row = pg_cursor.fetchone()
    while row is not None:
        pid = row[0]
        siuid_phi = row[1]
        siuid_anon = row[2]
        if pid in patient_map:
            patient_map[pid]['StudyInstanceUIDMap'][siuid_phi] = siuid_anon
        row = pg_cursor.fetchone()

    # Gather patientname_anon info
    if flag_siuid_to_anon:
        sql_query = "SELECT sphi.pid AS pidvalue, sphi.value AS phivalue, sanon.patientname_anon AS anonvalue " + \
                    "FROM studyinstanceuid sphi " + \
                        "INNER JOIN siuid2patientname_anon sanon " + \
                        "ON sanon.siuid = sphi.siuid"
        error_status += 1
        try:
            pg_cursor.execute(sql_query)
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            return {'status':error_status, 'error_text':'load_phi_to_anon_map: Problem querying study info'}, None, None, None
        row = pg_cursor.fetchone()
        while row is not None:
            pid = row[0]
            siuid_phi = row[1]
            patientname_anon = row[2]
            if pid in patient_map:
                if siuid_phi not in patient_map[pid]['SIUID2NameAnonMap']:
                    patient_map[pid]['SIUID2NameAnonMap'][siuid_phi] = []
                if patientname_anon not in patient_map[pid]['SIUID2NameAnonMap'][siuid_phi]:
                    patient_map[pid]['SIUID2NameAnonMap'][siuid_phi] += [patientname_anon]
            row = pg_cursor.fetchone()

    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    return {'status': 0}, patient_map, patient_reverse_map, flag_siuid_to_anon

# ============================================================================
def on_orthanc(pg_connection=None, pg_cursor=None):
    """Create a dict of what is on Orthanc currently"""
# ----------------------------------------------------------------------------

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database()
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            return status, None
    else:
        if pg_connection is None or pg_cursor is None:
            return {'status':1, 'error_text': 'on_orthanc:Must provide both con and cur'}, None

    # Confirm our lookup tables
    status = confirm_or_create_lookup_table_sql(pg_connection=pg_connection,
                                                pg_cursor=pg_cursor)
    if status['status'] != 0:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        return status, None

    # Collect orthanc patientids
    orthanc_patient_ids = json.loads(orthanc.RestApiGet('/patients'))
    n_patients = len(orthanc_patient_ids)

    # Misc parameters
    flag_split_screen_from_diagnostic = os.getenv('LUA_FLAG_SPLIT_SCREEN_DIAG', default='false') == 'true'
    flag_every_accession_a_patient = os.getenv('LUA_FLAG_EVERY_ACCESSION_A_PATIENT', default='false') == 'true'
    meta_system = json.loads(orthanc.RestApiGet('/system'))

    # Assemble dict
    now_on_orthanc = {}
    for dict_str in ['ByPatientID', 'StudyInstanceUID2PatientID', 'PatientID2oPatientID', 'StudyUID2oStudyUID']:
        now_on_orthanc[dict_str] = {}
    for orthanc_patient_id in orthanc_patient_ids:
        row_of_data = {}
        meta_patient = json.loads(orthanc.RestApiGet('/patients/%s' % orthanc_patient_id))
        if 'PatientName' in meta_patient['MainDicomTags'] and len(meta_patient['MainDicomTags']['PatientName'].strip()) > 0:
            row_of_data['PatientName'] = meta_patient['MainDicomTags']['PatientName'].strip()
        else:
            row_of_data['PatientName'] = ''
        patient_id = meta_patient['MainDicomTags']['PatientID']
        patient_id_temp = meta_patient['MainDicomTags']['PatientID']
        sql_query = "SELECT value FROM patientid WHERE pid IN (SELECT parent_pid FROM patientid WHERE value = %s)"
        try:
            pg_cursor.execute(sql_query, (patient_id_temp,))
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            return {'status': 2, 'error_text' : 'on_orthanc:Problem querying pid'}, None
        row = pg_cursor.fetchone()
        while row is not None:
            patient_id = row[0]
        for dict_str in ['StudyDate', 'AccessionNumber', 'StudyInstanceUID']:
            row_of_data[dict_str] = []
        meta_studies = json.loads(orthanc.RestApiGet('/patients/%s/studies' % orthanc_patient_id))
        for meta_study in meta_studies:
            orthanc_study_id = meta_study['ID']
            patient_id_modifier = ''
            if flag_split_screen_from_diagnostic and row_of_data['PatientName'].lower().find(meta_system['Name'].lower()) < 0:
                patient_id_modifier = set_screen_or_diagnostic(orthanc_study_id)
            if flag_every_accession_a_patient and row_of_data['PatientName'].lower().find(meta_system['Name'].lower()) < 0:
                patient_id_modifier = '_' + meta_study['MainDicomTags']['AccessionNumber']
            patient_id_modified = '%s%s' % (patient_id, patient_id_modifier)
            now_on_orthanc['PatientID2oPatientID'][patient_id_modified] = orthanc_patient_id
            row_of_data['StudyDate'] += [meta_study['MainDicomTags']['StudyDate']]
            row_of_data['AccessionNumber'] += [meta_study['MainDicomTags']['AccessionNumber']]
            row_of_data['StudyInstanceUID'] += [meta_study['MainDicomTags']['StudyInstanceUID']]
            now_on_orthanc['StudyInstanceUID2PatientID'][row_of_data['StudyInstanceUID'][-1]] = patient_id_modified
            now_on_orthanc['StudyUID2oStudyUID'][row_of_data['StudyInstanceUID'][-1]] = orthanc_study_id
        now_on_orthanc['ByPatientID'][patient_id_modified] = row_of_data

    return {'status': 0}, now_on_orthanc

# ============================================================================
def recursive_search_dicom_dict_for_group_element(gggg_comma_eeee_tag, value_dict, type_match='gggg-odd', match_list=[]):
    """
    PURPOSE: Assemble lists of matching DICOM tags and addresses from a DICOM 
                 value dict tree.
    INPUT:   gggg_comma_eeee_tag (string) - DICOM tag name commonly returned by 
                 call to Orthanc instances/INSTANCEID/tags
             value_dict (dictionary) - python dict corresponding to json dump
                 of call to /tags
             type_match (string) - default proprietary
                 'gggg-odd' - looks for odd numbered groups gggg
                 'gggg' - match against a list of gggg tags
                 'gggg-eeee' - match against a list of gggg-eeee tags
                 'gggg-regexp' - regexp match against group
             match_list (list) - when type is 'gggg' or 'gggg-eeee' or 'gggg-regexp', 
                 a list of DICOM gggg or gggg-eeee tags against which matches are sought
             
    OUTPUT:  Two lists with one to one correspondence
                 trigger (list) - matching tags found (in gggg-eeee format strings)
                 address (list) - assembled address of the tag with respect to the 
                     top level input parameters
    """
# ----------------------------------------------------------------------------

    group, element = gggg_comma_eeee_tag.split(',')
    gggg_dash_eeee_tag = '%s-%s' % (group, element)
    if type_match == 'gggg-odd':
        if int(group,16) % 2 == 1:
            return [gggg_dash_eeee_tag], [gggg_dash_eeee_tag]
    elif type_match in ['gggg-eeee', 'gggg']:
        if gggg_dash_eeee_tag in match_list:
            return [gggg_dash_eeee_tag], [gggg_dash_eeee_tag]
    elif type_match == 'gggg-regexp':
        for gggg_re in match_list:
            if re.search(gggg_re, group) is not None:
                return [gggg_dash_eeee_tag], [gggg_dash_eeee_tag]
    else: 
        return None, None
    
    if value_dict['Type'] == 'String':
        return None, None
    elif value_dict['Type'] == 'Sequence':
        address = []
        trigger = []
        for index in range(len(value_dict['Value'])):
            for sub_gggg_comma_eeee_tag, sub_value_dict in value_dict['Value'][index].items():
                sub_triggers, sub_addresses = recursive_search_dicom_dict_for_group_element(sub_gggg_comma_eeee_tag, sub_value_dict, type_match=type_match, match_list=match_list)
                if sub_triggers is not None:
                    for i_trigger in range(len(sub_triggers)):
                        if sub_triggers[i_trigger] is None:
                            continue   
                        address += ['%s[%d].%s' % (gggg_dash_eeee_tag,index,sub_addresses[i_trigger])]
                        trigger += [sub_triggers[i_trigger]]
        if len(trigger) > 0:
            return trigger, address
        else:
            return None, None
    else:
        return None, None
    
# ============================================================================
def scan_instance_for_group_element(orthanc_instance_id, trigger_map={}, type_match='gggg-odd', match_list=[]):
    """
    PURPOSE: Retrieve instance tags from Orthanc and return a map (dict) of
                 DICOM tags and their addresses within the DICOM
                 dict hierarchy IF A MATCH is found in match_list
    INPUT:   orthanc_instance_id (string) - The orthanc instance ID to scan
             trigger_map (dict, default empty {}) - an empty or existing dict
                 to which will be added any new findings
             type_match (string) - default proprietary
                 'gggg-odd' - looks for odd numbered groups gggg
                 'gggg' - match against a list of gggg tags
                 'gggg-eeee' - match against a list of gggg-eeee tags
                 'gggg-regexp' - regexp match against group
             match_list (list) - when type is 'gggg' or 'gggg-eeee' or 'gggg-regexp', 
                 a list of DICOM tags against which matches are sought
    OUTPUT:  status (int) - status of result
                 0: success
                 1: problem requesting tags
             trigger_map (dict) - A python dict of the results
                 .keys() (string) the triggering group-element tags 
                 .values() (list) List of addresses into the DICOM dict of 
                     locations where key trigger was found
    """
# ----------------------------------------------------------------------------
    response_instance = orthanc.RestApiGet('/instances/%s/tags' % orthanc_instance_id)
    metadata_instance = json.loads(response_instance)

    for gggg_comma_eeee_tag, value_dict in metadata_instance.items():
        trigger, address = recursive_search_dicom_dict_for_group_element(gggg_comma_eeee_tag, value_dict, type_match=type_match, match_list=match_list)
        if trigger is not None:
            for i_trigger in range(len(trigger)):
                if trigger[i_trigger] not in trigger_map:
                    trigger_map[trigger[i_trigger]] = []
                if address[i_trigger] not in trigger_map[trigger[i_trigger]]:
                    trigger_map[trigger[i_trigger]] += [address[i_trigger]]
        
    return trigger_map

# ============================================================================
def scan_series_for_group_element(orthanc_series_id, trigger_map={}, type_match='gggg-odd', match_list=[]):
    """
    PURPOSE: For all instances of a series, return a map (dict) of matching 
                 DICOM tags and their addresses within the DICOM dict hierarchy.
    INPUT:   orthanc_series_id (string) - The orthanc series ID to scan
             trigger_map (dict, default empty {}) - an empty or existing dict
                 to which will be added any new findings
             type_match (string) - default proprietary
                 'gggg-odd' - looks for odd numbered groups gggg
                 'gggg' - match against a list of gggg tags
                 'gggg-eeee' - match against a list of gggg-eeee tags
                 'gggg-regexp' - regexp match against group
             match_list (list) - when type is 'gggg' or 'gggg-eeee' or 'gggg-regexp', 
                 a list of DICOM tags against which matches are sought
    OUTPUT:  status (int) - status of result
                 0: success
                 1: problem requesting tags
             trigger_map (dict) - A python dict of the results
                 .keys() (string) the triggering group-element tags 
                 .values() (list) List of addresses into the DICOM dict of 
                     locations where key trigger was found
    """
# ----------------------------------------------------------------------------

    response_series = orthanc.RestApiGet('/series/%s' % orthanc_series_id)
    orthanc_instance_ids = json.loads(response_series)['Instances']

    for orthanc_instance_id in orthanc_instance_ids:
        trigger_map = scan_instance_for_group_element(orthanc_instance_id, trigger_map, type_match=type_match, match_list=match_list)

    return trigger_map

# ============================================================================
def scan_study_for_group_element(orthanc_study_id, trigger_map={}, type_match='gggg-odd', match_list=[]):
    """
    PURPOSE: For all instances of a study, return a map (dict) of matching
                 DICOM tags and their addresses within the DICOM dict hierarchy.
    INPUT:   orthanc_study_id (string) - The orthanc study ID to scan
             trigger_map (dict, default empty {}) - an empty or existing dict
                 to which will be added any new findings
             type_match (string) - default proprietary
                 'gggg-odd' - looks for odd numbered groups gggg
                 'gggg' - match against a list of gggg tags
                 'gggg-eeee' - match against a list of gggg-eeee tags
                 'gggg-regexp' - regexp match against group
             match_list (list) - when type is 'gggg' or 'gggg-eeee' or 'gggg-regexp', 
                 a list of DICOM tags against which matches are sought
    OUTPUT:  status (int) - status of result
                 0: success
                 1: problem requesting tags
             trigger_map (dict) - A python dict of the results
                 .keys() (string) the triggering matching tags 
                 .values() (list) List of addresses into the DICOM dict of 
                     locations where key trigger was found
    """
# ----------------------------------------------------------------------------
    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    orthanc_series_ids = json.loads(response_study)['Series']
    
    for orthanc_series_id in orthanc_series_ids: 
        trigger_map = scan_series_for_group_element(orthanc_series_id, trigger_map, type_match=type_match, match_list=match_list)

    return trigger_map

# =======================================================
def set_2d_or_cview_tomo(orthanc_series_id):
# -------------------------------------------------------
    flag_non_2d = False

    meta_series = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id))
    for orthanc_instance_id in meta_series['Instances']:

        meta_instance = json.loads(orthanc.RestApiGet('/instances/%s/simplified-tags' % orthanc_instance_id))
        if 'SeriesDescription' in meta_instance and len(meta_instance['SeriesDescription'].strip()) > 0:
            description_lower = meta_instance['SeriesDescription'].strip().lower()
            flag_non_2d = flag_non_2d or (description_lower.find('c-view') >= 0)
            flag_non_2d = flag_non_2d or (description_lower.find('tomo') >= 0)
        if flag_non_2d:
            break
            

    if flag_non_2d:
        patient_id_modifier = 'n2d'
    else:
        patient_id_modifier = '2d'

    return patient_id_modifier

# =======================================================
def set_screen_or_diagnostic(orthanc_study_id):
    """Used only in very specific Winkler/Hologic studies"""
# -------------------------------------------------------

    flag_screening = False
    meta_instances = json.loads(orthanc.RestApiGet('/studies/%s/instances' % orthanc_study_id))
    dicom_fields = ['Study', 'Series', 'PerformedProcedureStep', 'RequestedProcedure']
    for meta_instance in meta_instances:
        orthanc_instance_id = meta_instance['ID']
        meta_instance = json.loads(orthanc.RestApiGet('/instances/%s/simplified-tags' % orthanc_instance_id))
        for dicom_field in dicom_fields:
            description_field = '%s%s' % (dicom_field, 'Description')
            if description_field in meta_instance:
                description_lower = meta_instance[description_field].lower()
                flag_screening = flag_screening or (description_lower.find('screen') >= 0)
                flag_screening = flag_screening or (description_lower.find('scrn') >= 0)
                if flag_screening:
                    break
        if not flag_screening and \
            ('ProcedureCodeSequence' in meta_instance) and \
            (len(meta_instance['ProcedureCodeSequence']) > 0) and \
            ('CodeMeaning' in meta_instance['ProcedureCodeSequence'][0]):
            description_lower = meta_instance['ProcedureCodeSequence'][0]['CodeMeaning'].lower()
            flag_screening = flag_screening or (description_lower.find('screen') >= 0)
            flag_screening = flag_screening or (description_lower.find('scrn') >= 0)
        if flag_screening:
            break
 
    if flag_screening:
        patient_id_modifier = 's'
    else:
        patient_id_modifier = 'd'
    return patient_id_modifier
           
# =======================================================
def shift_date_time_string(shift_epoch,incoming_yyyymmdd,incoming_hhmmss=None):
    """Shift time stamp and return shifted values"""
# -------------------------------------------------------
   
    flag_time_found = True
    incoming_yyyymmdd = incoming_yyyymmdd.strip()
    if len(incoming_yyyymmdd) == 14:
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd,'%Y%m%d%H%M%S%')
        fraction_str = None
    elif len(incoming_yyyymmdd) > 14 and incoming_yyyymmdd.find('.') == 14:
        fraction_str = incoming_yyyymmdd[14:]
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd[0:14],'%Y%m%d%H%M%S%')
    elif len(incoming_yyyymmdd) > 14 and incoming_yyyymmdd.find('.') < 0:
        fraction_str = None
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd[0:14],'%Y%m%d%H%M%S%')
    else:
        fraction_str = None
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd[0:8],'%Y%m%d')
        flag_time_found = False
     
    if (not flag_time_found) and (incoming_hhmmss is not None):
        incoming_hhmmss = incoming_hhmmss.strip()
        index_dot = incoming_hhmmss.find('.')
        if len(incoming_hhmmss) >= 6 and index_dot == 6:
            fraction_str = incoming_hhmmss[index_dot:]
        else:
            fraction_str = None
        date_local = datetime.datetime.strptime(incoming_hhmmss[0:6],'%H%M%S')
        incoming_datetime.replace(hour=date_local.hour,minute=date_local.minute,second=date_local.second)

    # Shift the dates
    outgoing_datetime = incoming_datetime - datetime.timedelta(seconds=shift_epoch)

    # Preserve the original hour, minute, second
    outgoing_datetime.replace(hour=incoming_datetime.hour, minute=incoming_datetime.minute, second=incoming_datetime.second)

    # Output strings
    if len(incoming_yyyymmdd) == 14:
        outgoing_yyyymmdd = '%s.0' % outgoing_datetime.strftime('%Y%m%d%H%M%S')
    elif len(incoming_yyyymmdd) > 14 and incoming_yyyymmdd.find('.') == 14:
        outgoing_yyyymmdd = '%s%s' % (outgoing_datetime.strftime('%Y%m%d%H%M%S'), fraction_str)
    elif len(incoming_yyyymmdd) > 14 and incoming_yyyymmdd.find('.') < 0:
        outgoing_yyyymmdd = '%s.0' % outgoing_datetime.strftime('%Y%m%d%H%M%S')
    else:
        outgoing_yyyymmdd = outgoing_datetime.strftime('%Y%m%d')
    
    outgoing_hhmmss = None
    # Tack on any fractional seconds
    if incoming_hhmmss is not None:
        if fraction_str is not None:
            outgoing_hhmmss = '%s%s' % (outgoing_datetime.strftime('%H%M%S'), fraction_str)
        else:
            outgoing_hhmmss = '%s.0' % outgoing_datetime.strftime('%H%M%S')

    if outgoing_hhmmss is None:
        return outgoing_yyyymmdd
    else:
        return outgoing_yyyymmdd, outgoing_hhmmss

# =======================================================
def update_lookup_html():
    """ Update the html lookup table  """
# -------------------------------------------------------

    flag_keep_original_dates = os.getenv('LUA_FLAG_KEEP_ORIGINAL_DATES', default='false') == 'true'

    # Load the map from the sql database
    status, patient_map, patient_reverse_map, flag_siuid_to_anon = load_phi_to_anon_map()
    if status['status'] != 0:
        return status
    
    # Map what's on Orthanc now
    status, now_on_orthanc = on_orthanc()
    if status['status'] != 0:
        return status

    # Check for the main modality that could be queried
    flag_xref_modality, xref_modality = check_xref_modality()

    # Check for existing lookup table
    file_lookup = '/media/html/lookup/master/lookuptable_copy.html'
    answer, lookup_table = load_lookup_table(file_lookup, make_backup=True)
    if answer['status'] != 0:
        return answer

    # Prepare to output the new
    with open(file_lookup, 'w') as lun:

        lun.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-us">\n')
        lun.write('<head>\n')
        lun.write('<link rel="stylesheet" href="style.css" type="text/css" id="" media="print, projection, screen" />\n')
        lun.write('<link rel="stylesheet" href="theme.blue.min.css">\n')
        lun.write('<script type="text/javascript" src="../../../app/libs/jquery.min.js"></script>\n')
        lun.write('<script type="text/javascript" src="jquery.tablesorter.combined.min.js"></script>\n')
        lun.write('<script type="text/javascript">\n')
        lun.write('$(document).ready(function() { \n')
        lun.write('    // call the tablesorter plugin \n')
        lun.write('    $("table").tablesorter({\n')
        lun.write('        theme: "blue",\n')
        lun.write('        widgets: ["zebra", "filter"],\n')
        lun.write('        widgetOptions : {\n')
        lun.write('            filter_columnFilters: true,\n')
        lun.write('            filter_reset: ".reset",\n')
        lun.write('            zebra : [ "normal-row", "alt-row" ]\n')
        lun.write('        },\n')
        lun.write('        sortList : [[2,0]]\n')
        lun.write('    }); \n')
        lun.write('}); \n')
        lun.write('</script>\n')
        lun.write('</head>\n')
        
        lun.write('<body>\n')
        lun.write('<a href="../../../app/explorer.html">Return to Orthanc home page</a></br>')
        lun.write('Click a column heading to sort.</br>')
        lun.write('Click <a href="updatelookup.html">here</a> to force an update of this table.</br>\n')
        lun.write('<!-- targeted by the "filter_reset" option -->\n')
        lun.write('<button type="button" class="reset">Reset Search</button>\n')
        lun.write('<table class="tablesorter-blue" border=1>\n')
        lun.write('<thead>\n')
        lun.write('<tr>\n')
        lun.write('<th>Name</th>\n')
        lun.write('<th>PatientID</th>\n')
        lun.write('<th>ID</th>\n')
        if flag_siuid_to_anon:
            lun.write('<th>Name Anon</th>\n')
        lun.write('<th>Date</th>\n')
        lun.write('<th>Anon Date</th>\n')
        lun.write('<th>Accession</th>\n')
        lun.write('<th>Alt PatientID</th>\n')
        lun.write('<th>Anon PatientID</th>\n')
        lun.write('<th>StudyInstanceUID</th>\n')
        lun.write('<th>Anon StudyInstanceUID</th>\n')
        lun.write('</tr>\n')
        lun.write('</thead>\n')
        lun.write('<tbody>\n')
        
        #compute_times = {}
        for patient_id, pid in patient_reverse_map['Primary'].items():

            #time0 = time.time()
            #if 1 not in compute_times:
                #compute_times[1] = {'count': 0, 'value': 0.0}
            if flag_keep_original_dates:
               shift_epoch = 0
            else:
               if 'ShiftEpoch' in patient_map[pid]:
                   shift_epoch = patient_map[pid]['ShiftEpoch']
               else:
                   shift_epoch = 0
            if patient_id[-3:] == 'n2d':
                patient_id_short = patient_id[:-3]
            elif patient_id[-2:] == '2d':
                patient_id_short = patient_id[:-2]
            else:
                patient_id_short = patient_id
            if 'PatientIDAnon' in patient_map[pid]:
                patient_id_anon = patient_map[pid]['PatientIDAnon']
            else:
                patient_id_anon = None
            study_instance_uid_printed = {}
            #compute_times[1]['count'] += 1
            #compute_times[1]['value'] += time.time() - time0
            if patient_id in now_on_orthanc['ByPatientID']:

                for j, date_str in enumerate(now_on_orthanc['ByPatientID'][patient_id]['StudyDate']):
                    #if 20 not in compute_times:
                        #compute_times[20] = {'count':0, 'value': 0.0}
                    #time0 = time.time()
                    study_instance_uid = now_on_orthanc['ByPatientID'][patient_id]['StudyInstanceUID'][j]
                    accession_number = now_on_orthanc['ByPatientID'][patient_id]['AccessionNumber'][j]
                    if study_instance_uid in patient_map[pid]['StudyInstanceUIDMap']:
                        study_instance_uid_anon = patient_map[pid]['StudyInstanceUIDMap'][study_instance_uid]
                    else:
                        study_instance_uid_anon = None
                    study_instance_uid_printed[study_instance_uid] = True
                    lun.write('<tr>\n')
                    lun.write('<td>\n')
                    lun.write('<a href="../../../app/explorer.html#patient?uuid=' + now_on_orthanc['PatientID2oPatientID'][patient_id] + '">\n')
                    lun.write(now_on_orthanc['ByPatientID'][patient_id]['PatientName'])
                    lun.write('</a>\n')
                    lun.write('</td>\n')
                    lun.write('<td align="right">' + patient_id_short + '</td>\n')
                    lun.write('<td align="right">\n')
                    if patient_id_anon is not None and patient_id_anon in now_on_orthanc['ByPatientID']:
                        lun.write('<a href="../../../app/explorer.html#patient?uuid=' + now_on_orthanc['PatientID2oPatientID'][patient_id_anon] + '">\n')
                        lun.write('%d' % patient_map[pid]['InternalNumber'])
                        lun.write('</a>\n')
                    else:
                        lun.write('%d' % patient_map[pid]['InternalNumber'])
                    lun.write('</td>\n')
                    if flag_siuid_to_anon:
                        if study_instance_uid in patient_map[pid]['SIUID2NameAnonMap']:
                            lun.write('<td>\n')
                            for patientname_anon in patient_map[pid]['SIUID2NameAnonMap'][study_instance_uid]:
                                lun.write('%s, ' % patientname_anon)
                            lun.write('</td>\n')
                        else:
                            lun.write('<td>&nbsp</td>\n')
                    lun.write('<td align="center">' + date_str + '</td>\n')
                    if flag_keep_original_dates:
                        lun.write('<td align="center">' + date_str + '</td>\n')
                    elif shift_epoch == 0:
                        lun.write('<td align="center">&nbsp</td>\n')
                    else:
                        new_date_string = shift_date_time_string(shift_epoch, date_str)
                        lun.write('<td align="center">' + new_date_string + '</td>\n')
                    lun.write('<td align="right">' + accession_number + '</td>\n')
                    lun.write('<td>\n')
                    for alt_pid in patient_map[pid]['OtherPatientIDs']:
                        lun.write('%s, \n' % alt_pid)
                    lun.write('</td>\n')
                    lun.write('<td align="center">\n')
                    #compute_times[20]['count'] += 1
                    #compute_times[20]['value'] += time.time() - time0
                    #if 30 not in compute_times:
                        #compute_times[30] = {'count':0, 'value':0.0}
                    #time0 = time.time()
                    if patient_id_anon is not None:
                        if patient_id_anon in now_on_orthanc['ByPatientID']:
                            lun.write('<a href="../../../app/explorer.html#patient?uuid=' + now_on_orthanc['PatientID2oPatientID'][patient_id_anon] + '">\n')
                            lun.write(patient_id_anon)
                            lun.write('</a>\n')
                        else:
                            lun.write(patient_id_anon)
                    else:
                        lun.write('&nbsp')
                    #compute_times[30]['count'] += 1
                    #compute_times[30]['value'] += time.time() - time0
                    #if 40 not in compute_times:
                        #compute_times[40] = {'count':0, 'value': 0.0}
                    #time0 = time.time()
                    lun.write('</td>\n')
                    lun.write('<td align="right">\n')
                    lun.write('<a href="../../../app/explorer.html#study?uuid=' + now_on_orthanc['StudyUID2oStudyUID'][study_instance_uid] + '">\n')
                    lun.write(study_instance_uid)
                    lun.write('</a>\n')
                    lun.write('</td>\n')
                    lun.write('<td align="right">\n')
                    if study_instance_uid_anon is not None:
                        if study_instance_uid_anon in now_on_orthanc['StudyUID2oStudyUID']:
                            lun.write('<a href="../../../app/explorer.html#study?uuid=' + now_on_orthanc['StudyUID2oStudyUID'][study_instance_uid_anon] + '">\n')
                        lun.write(study_instance_uid_anon)
                        if study_instance_uid_anon in now_on_orthanc['StudyUID2oStudyUID']:
                            lun.write('</a>\n')
                    else:
                        lun.write('')
                    lun.write('</td>\n')
                    lun.write('</tr>\n')
                    #compute_times[40]['count'] += 1
                    #compute_times[40]['value'] += time.time() - time0
            for study_instance_uid, study_instance_uid_anon in patient_map[pid]['StudyInstanceUIDMap'].items():
                if study_instance_uid not in study_instance_uid_printed:
                    #if 50 not in compute_times:
                        #compute_times[50] = {'count':0, 'value':0.0}
                    #time0 = time.time()
                    pacs_data_local = None
                    lookup_match = False
                    if lookup_table is not None:
                        lookup_match, pacs_data_local  = find_pacs_in_lookup_table(lookup_table,study_instance_uid,type_match='siuid')
                        if pacs_data_local is None:
                            #orthanc.LogWarning(study_instance_uid)
                            orthanc.LogWarning('Not found in lookup: ' + study_instance_uid)
                            #return {'status': 1, 'error_text':'update_lookup_table: Not found in lookup %s' % study_instance_uid }
                    #compute_times[50]['count'] += 1
                    #compute_times[50]['value'] += time.time() - time0
                    if flag_xref_modality and (pacs_data_local is None) and (re.match('[0-9]*[^0-9]+[0-9]*',patient_id) is None):
                        #if 60 not in compute_times:
                            #compute_times[60] = {'count':0, 'value':0.0}
                        #time0 = time.time()
                        patient_id_list = []
                        patient_id_list += [patient_id]
                        if 'OtherPatientIDs' in patient_map[pid]:
                            for patient_id_other in patient_map[pid]['OtherPatientIDs']:
                                if re.match('[0-9]*[^0-9]+[0-9]*',patient_id_other) is None:
                                    if patient_id_other not in patient_id_list:
                                        patient_id_list += [patient_id_other]
                        for patient_id_other in patient_id_list:
                            pacs_query = {}
                            pacs_query['Level'] = 'Study'
                            pacs_query['Query'] = {}
                            pacs_query['Query']['StudyInstanceUID'] = study_instance_uid
                            pacs_query['Query']['PatientID'] = patient_id_other
                            result_query = json.loads(orthanc.RestApiPost('/modalities/' + xref_modality + '/query', json.dumps(pacs_query)))
                            if 'ID' in result_query:
                                local_query = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID']))
                                if len(local_query) > 0 and local_query[0] == "answers":
                                    local_query = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID'] + '/answers'))
                                    if len(local_query) > 0 and local_query[0] == "0":
                                        local_query = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID'] + '/answers/0'))
                                        if len(local_query) > 0 and local_query[0] == "content":
                                            pacs_data_local = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID'] + '/answers/0/content'))
                                            if len(pacs_data_local) > 0:
                                                break
                                            else:
                                                pacs_data_local = None
                        #compute_times[60]['count'] += 1
                        #compute_times[60]['value'] += time.time() - time0
                        #if 70 not in compute_times:
                            #compute_times[70] = {'count':0, 'value':0.0}
                        #time0 = time.time()
                        if pacs_data_local is None:
                            for patient_id_other in patient_id_list:
                                pacs_query = {}
                                pacs_query['Level'] = 'Patient'
                                pacs_query['Query'] = {}
                                pacs_query['Query']['PatientID'] = patient_id_other
                                result_query = json.loads(orthanc.RestApiPost('/modalities/' + xref_modality + '/query', json.dumps(pacs_query)))
                                if 'ID' in result_query:
                                    local_query = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID']))
                                    if len(local_query) > 0 and local_query[0] == "answers":
                                        local_query = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID'] + '/answers'))
                                        if len(local_query) > 0 and local_query[0] == "0":
                                            local_query = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID'] + '/answers/0'))
                                            if len(local_query) > 0 and local_query[0] == "content":
                                                pacs_data_local = json.loads(orthanc.RestApiGet('/queries/' + result_query['ID'] + '/answers/0/content'))
                                                if len(pacs_data_local) > 0:
                                                    break
                                                else:
                                                    pacs_data_local = None
                        #compute_times[70]['count'] += 1
                        #compute_times[70]['value'] += time.time() - time0
                    lun.write('<tr>\n')
                    #if 80 not in compute_times:
                        #compute_times[80] = {'count':0, 'value':0.0}
                    #time0 = time.time()
                    if pacs_data_local is not None:
                        if '0010,0010' in pacs_data_local:
                            lun.write('<td>' + pacs_data_local['0010,0010']['Value'] + '</td>\n')
                        else:
                            lun.write('<td>&nbsp</td>\n')
                    else:
                        lun.write('<td>&nbsp</td>\n')
                    if pacs_data_local is not None:
                        if '0010,0020' in pacs_data_local:
                            lun.write('<td>' + pacs_data_local['0010,0020']['Value'] + '</td>\n')
                        else:
                            lun.write('<td>&nbsp</td>\n')
                    else:
                        lun.write('<td align="right">' + patient_id_short + '</td>\n')
                    lun.write('<td align="right">\n')
                    if patient_id_anon in now_on_orthanc['ByPatientID']:
                        lun.write('<a href="../../../app/explorer.html#patient?uuid=' + now_on_orthanc['PatientID2oPatientID'][patient_id_anon] + '">\n')
                    if 'InternalNumber' in patient_map[pid]:
                        lun.write('%d' % patient_map[pid]['InternalNumber'])
                    else:
                        lun.write('')
                    if patient_id_anon in now_on_orthanc['ByPatientID']:
                        lun.write('</a>\n')
                    lun.write('</td>\n')
                    #compute_times[80]['count'] += 1
                    #compute_times[80]['value'] += time.time() - time0
                    #if 90 not in compute_times:
                        #compute_times[90] = {'count':0, 'value':0.0}
                    #time0 = time.time()
                    if flag_siuid_to_anon:
                        if study_instance_uid in patient_map[pid]['SIUID2NameAnonMap']:
                            lun.write('<td>\n')
                            for patient_name_anon_local in patient_map[pid]['SIUID2NameAnonMap'][study_instance_uid]:
                                lun.write(patient_name_anon_local + ', ')
                            lun.write('</td>\n')
                        else:
                            lun.write('<td>&nbsp</td>\n')
                    #compute_times[90]['count'] += 1
                    #compute_times[90]['value'] += time.time() - time0
                    #if 100 not in compute_times:
                        #compute_times[100] = {'count':0, 'value':0.0}
                    #time0 = time.time()
                    if pacs_data_local is not None:
                        if '0008,0020' in pacs_data_local:
                            lun.write('<td>' + pacs_data_local['0008,0020']['Value'] + '</td>\n')
                            if flag_keep_original_dates:
                                lun.write('<td>' + pacs_data_local['0008,0020']['Value'] + '</td>\n')
                            elif shift_epoch == 0:
                                lun.write('<td>' + pacs_data_local['0008,0020']['Value'] + '</td>\n')
                            else:
                                if (not lookup_match) or \
                                  ((lookup_table is not None) and \
                                   ('AnonDate' not in pacs_data_local) and \
                                   (('0008,0020' in pacs_data_local) and (pacs_data_local['0008,0020']['Value'] != 'NotInPACS'))):
                                    new_date_string = shift_date_time_string(shift_epoch,pacs_data_local['0008,0020']['Value'])
                                else:
                                    if 'AnonDate' in pacs_data_local:
                                        new_date_string = pacs_data_local['AnonDate']
                                    else:
                                        new_date_string = 'BLANK'
                                lun.write('<td>' + new_date_string + '</td>\n')
                        else:
                            lun.write('<td>NotInPACS</td>\n')
                            lun.write('<td>&nbsp</td>\n')
                    else:
                        lun.write('<td>NotInPACS</td>\n')
                        lun.write('<td>&nbsp</td>\n')
                    #compute_times[100]['count'] += 1
                    #compute_times[100]['value'] += time.time() - time0
                    #if 110 not in compute_times:
                        #compute_times[110] = {'count':0, 'value':0.0}
                    #time0 = time.time()
                    if pacs_data_local is not None:
                        if '0008,0050' in pacs_data_local:
                            lun.write('<td>' + pacs_data_local['0008,0050']['Value'] + '</td>\n')
                        else:
                            lun.write('<td>NotInPACS</td>\n')
                    else:
                        lun.write('<td>NotInPACS</td>\n')
                    lun.write('<td>\n')
                    for patient_id_other in patient_map[pid]['OtherPatientIDs']:
                        lun.write(patient_id_other + ', \n')
                    if pacs_data_local is not None:
                        if '0010,0020' in pacs_data_local:
                            if pacs_data_local['0010,0020']['Value'] != patient_id_short:
                                lun.write(patient_id_short)
                    lun.write('</td>\n')
                    if patient_id_anon is not None:
                        lun.write('<td align="center">' + patient_id_anon + '</td>\n')
                    else:
                        lun.write('<td align="center">&nbsp</td>\n')
                    lun.write('<td align="right">' + study_instance_uid + '</td>\n')
                    lun.write('<td align="right">\n')
                    if study_instance_uid_anon in now_on_orthanc['StudyUID2oStudyUID']:
                        lun.write('<a href="../../../app/explorer.html#study?uuid=' + now_on_orthanc['StudyUID2oStudyUID'][study_instance_uid_anon] + '">\n')
                        lun.write(study_instance_uid_anon)
                        lun.write('</a>\n')
                    else:
                        lun.write(study_instance_uid_anon)
                    lun.write('</td>\n')
                    lun.write('</tr>\n')
                    study_instance_uid_printed[study_instance_uid] = True
                    #compute_times[110]['count'] += 1
                    #compute_times[110]['value'] += time.time() - time0
            lun.flush()
            #for c_id, compute_time in compute_times.items():
            #    if compute_time['value'] == 0 or compute_time['count'] == 0:
            #        continue
            #    orthanc.LogWarning('Compute time %d %f' % (c_id, compute_time['value'] / compute_time['count']))
        lun.write('</tbody>\n')
        lun.write('</table>\n')
        lun.write('</body>\n')
        lun.write('</html>\n')

    return {'status': 0}

# =======================================================
def user_permitted(uri, remote_user):
    """ Check remote user against list of permitted users """
# -------------------------------------------------------

    orthanc.LogWarning('Checking whether remote user (%s) is permitted to \n%s' % (remote_user,uri))
    permissions = os.getenv('PYTHON_X_REMOTE_USER_ALLOWED_TO_TRIGGER')
    if permissions is None:
        orthanc.LogWarning('Rejecting anon due to missing permissions')
        return False
    allowed_to_trigger = []
    for permitted in permissions.split('.'):
        if permitted.strip() not in allowed_to_trigger:
            allowed_to_trigger += [permitted.strip()]
    orthanc.LogWarning('Allowed users: %s' % ' '.join(allowed_to_trigger))
    if remote_user not in allowed_to_trigger:
        orthanc.LogWarning('Operation not permitted to user: %s %s' % (uri, remote_user))
        return False
    orthanc.LogWarning('Remote user is permitted (%s)' % remote_user)

    return True

# ============================================================================
def ConfirmOrCreateLookupTableSQL(output, uri, **request):
    """API interface to check for existence of sql lookup table and create if necessary"""
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        if 'x-remote-user' not in request['headers'] or request['headers']['x-remote-user'] != 'lua-ConfirmOrCreate': 
            output.AnswerBuffer(json.dumps({'status': 1, 'error_text' :'ConfirmOrCreateLookupTable:missing or invalid user'}), 'application/json')
            return
        status = confirm_or_create_lookup_table_sql()
        output.AnswerBuffer(json.dumps(status, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def ConstructPatientName(output, uri, **request):
    """API interface to construct the patients name"""
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        incoming_data = json.loads(request['body'])
        internal_number = int(float(incoming_data['internal_number']))
        if 'patient_name_base' in incoming_data:
            patient_name_base = incoming_data['patient_name_base']
        else:
            patient_name_base = None
        if 'patient_name_id' in incoming_data:
            patient_name_id = incoming_data['patient_name_id']
        else:
            patient_name_id = None
        patient_name = construct_patient_name(internal_number,
                                              patient_name_base=patient_name_base, 
                                              patient_name_id=patient_name_id)
        output.AnswerBuffer(patient_name, 'text/plain')
    else:
        output.SendMethodNotAllowed('POST')

# ============================================================================
def GetInternalNumber(output, uri, **request):
    """API interface to retrieve the internal number"""
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        if 'x-remote-user' not in request['headers'] or request['headers']['x-remote-user'] != 'lua-GetInternalNumber': 
            result = {'status' : {'status': 1, 'error_text' : 'GetInternalNumber: missing or invalid user'}}
            output.AnswerBuffer(json.dumps(result), 'application/json')
            return
        incoming_data = json.loads(request['body'])
        sql_pid = int(incoming_data['sql_pid'])
        patient_id_modifier = incoming_data['patient_id_modifier']
        status, internal_number = get_internal_number(sql_pid, patient_id_modifier)
        result = {}
        result['status'] = status
        if internal_number is not None:
            result['internal_number'] = int(float(internal_number))
        output.AnswerBuffer(json.dumps(result,indent=3), 'application/json')
    else:
        output.SendMethodNotAllowed('POST')

# =======================================================
def EmailStudyReport(output, uri, **request):
    """API interface to generate and send email report on study"""
# -------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_study_id = request['groups'][0]
        status = email_study_report(orthanc_study_id)
        if status['status'] != 0:
            output.AnswerBuffer(status['error_text'], 'text/plain')
        else:
            output.AnswerBuffer('Email sent.', 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

# =======================================================
def EmailSubjectMessage(output, uri, **request):
    """API interface to send particular subject a message"""
# -------------------------------------------------------
    if request['method'] == 'POST':
        if 'x-remote-user' not in request['headers'] or request['headers']['x-remote-user'] != 'lua-SendEmailUpdate': 
            output.AnswerBuffer(json.dumps({'status': 1, 'error_text' : 'EmailSubjectMessage: missing or invalid user'}), 'application/json')
            return
        incoming_data = json.loads(request['body'])
        if 'subject' not in incoming_data or 'message' not in incoming_data:
            output.AnswerBuffer(json.dumps({'status': 2, 'error_text':'EmailSubjectMessage: Missing subject or message'}), 'application/json')
            return
        subject = incoming_data['subject']
        message = incoming_data['message']
        status = email_message(subject, message)
        if status['status'] != 0:
            output.AnswerBuffer(json.dumps(status), 'application/json')
        else:
            output.AnswerBuffer(json.dumps(status), 'application/json')
    else:
        output.SendMethodNotAllowed('POST')

# ============================================================================
def IncomingFilter(uri, **request):
    """Set up rights based actions"""
# ----------------------------------------------------------------------------

    headers_str = ''
    for key,value in request['headers'].items():
        headers_str = '%s %s.%s' % (headers_str, key, value)
    if not('x-remote-user' in request['headers'] and 'x-forwarded-for' in request['headers']):
        orthanc.LogWarning('Rejecting incoming access: %s' % headers_str)
        return False

    remote_user = get_remote_user(request['headers'])
    if 'x-forwarded-for' in request['headers']:
        remote_ip = request['headers']['x-forwarded-for']
    elif 'host' in request['headers']:
        remote_ip = request['headers']['host']
    else:
        remote_ip = ''
        for key,value in request['headers'].items():
            remote_ip = '%s %s.%s' % (remote_ip, key, value)

    methods = {1: 'GET', 2: 'POST', 3: 'PUT', 4: 'DELETE'}
    if 'method' in request and request['method'] in methods:
        method = methods[request['method']]
    elif 'method' in request:
        method = 'Unknown method %s' % request['method']
    else:
        method = 'Unknown method'

    if uri.find('images') < 0:
        orthanc.LogWarning('%s %s %s %s' % (remote_user, remote_ip, method, uri))

    if method in ['DELETE', 'PUT']:
        return user_permitted(uri, remote_user)
        
    if method == 'POST' and \
        (uri.find('/anonymize') >= 0 or \
         uri.find('/jsanon') >= 0 or \
         uri.find('/execute-script') >= 0):

        if not user_permitted(uri, remote_user):
            orthanc.LogWarning('User not permitted to anonymize: %s' % remote_user)
            return False
        else: 
            orthanc.LogWarning('User permitted to anonymize: %s' % remote_user)

        # Note that we have to capture anonymize this way as opposed to registering a callback
        # That's because registering a callback would proceed with both OUR anonymization and the standard Orthanc anon
        study_res = None
        if uri.find('/anonymize') >= 0:
            study_res = re.match('.*studies/([^/]+)/anonymize', uri)
            if study_res is None:
                orthanc.LogWarning('User does not appear to be anonymizing at the series level:\n%s' % uri)
                return False
            flag_js = False
            orthanc.LogWarning('User triggered web anonymize')
        if uri.find('/jsanon') >= 0:
            study_res = re.match('.*studies/([^/]+)/jsanon', uri)
            if study_res is None:
                orthanc.LogWarning('User does not appear to be anonymizing at the series level:\n%s' % uri)
                return False
            flag_js = True
            orthanc.LogWarning('User triggered form based anonymize')

        if study_res is not None:
            orthanc.LogWarning('Starting anon')
            orthanc_study_id = study_res.group(1)
            anonymize_study(orthanc_study_id)
            orthanc.LogWarning('Anon returned.')
            if flag_js:
                return True
            else:
                return False

        if uri.find('/execute-script') >= 0:
            return True

    if uri.find('/extra/lookup/master/updatelookup.html') >= 0:
        if user_permitted(uri, remote_user):
            response_post = orthanc.RestApiPost('/tools/execute-script', 'UpdateLookupHTML()')
        else:
            return False

    if uri.find('update_lookup_table') >= 0:
        if not user_permitted(uri, remote_user):
            return False

    return True

# ============================================================================
def JSAnonymizeStudy(output, uri, **request):
    """
    PURPOSE: Replaces the original Lua AnonymizeStudy which was just a feed
        to OnStableStudyMean that bypassed the IncomingHTTP filter.
    """
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        output.AnswerBuffer(json.dumps({}, indent=3), 'application/json')
    else:
        output.SendMethodNotAllowed('POST')

# ============================================================================
def OnChange(change_type, level, resource_id):
    """
    PURPOSE: Manage incoming DICOM when a state change is detected
    INPUT:   structures routed by way of the python plugin
    OUTPUT:  Designated action
    """
# ----------------------------------------------------------------------------

    # ------------------------------
    # Stable Study
    # ------------------------------
    if change_type == orthanc.ChangeType.STABLE_STUDY:

        # Auto anonymization
        response_post = orthanc.RestApiPost('/tools/execute-script', 'gFlagForceAnon=false')
        response_post = orthanc.RestApiPost('/tools/execute-script', 'gIndent=0')
        flag_anonymize_upon_stable = os.getenv('LUA_FLAG_AUTO_ANON_WHEN_STABLE', default='false') == 'true'
        if flag_anonymize_upon_stable:
            response_study = orthanc.RestApiGet('/studies/%s' % resource_id)
            meta_study = json.loads(response_study)
            if ('ModifiedFrom' not in meta_study) and ('AnonymizedFrom' not in meta_study):
                orthanc.LogWarning('Non-anonymized study stable.  Initiating auto anon')
                response_post = orthanc.RestApiPost('/tools/execute-script', 'OnStableStudyMain(\'%s\', nil, nil)' % resource_id)

        # Email updates
        if os.getenv('PYTHON_MAIL_AUTO', default='false') == 'true':
            status = email_study_report(resource_id)
            if status['status'] != 0:
                orthanc.LogWarning(status['error_text'])
            else:
                orthanc.LogWarning('Sent onstable study report')

# ============================================================================
def PrepareDataForAnonymizeGUI(output, uri, **request):
    """Setup data for javascript anonymizer."""
# ----------------------------------------------------------------------------

    if request['method'] == 'GET':

        answer = {'status': 0}

        # Check inputs
        if not flag_beautiful_soup:
            answer['status'] = 1
            answer['error_text'] = 'PrepareDataForAnonymize: No beautiful soup.  Needed to parse lookup.'
            output.AnswerBuffer(json.dumps(answer, indent=3), 'application/json')

        if not flag_psycopg2:
            answer['status'] = 2
            answer['error_text'] = 'No psycopg2'
            output.AnswerBuffer(json.dumps(answer, indent=3), 'application/json')
    
        file_lookup = '/media/html/lookup/master/lookuptable.html'
        if not os.path.exists(file_lookup):
            answer['status'] = 3
            answer['error_text'] = 'Missing lookup table at expected location'
            output.AnswerBuffer(json.dumps(answer, indent=3), 'application/json')

        flag_query_pacs = False
        if 'pacs' in request['get']:
            flag_query_pacs = int(request['get']['pacs']) != 0

        # Check to see if UUHSCQ is registered for PACS queries
        response_modalities = orthanc.RestApiGet('/modalities')
        name_uuhscq = None
        flag_uuhscq = True
        for modality_name in json.loads(response_modalities):
            meta_config = json.loads(orthanc.RestApiGet('/modalities/%s/configuration' % modality_name))
            if meta_config['AET'] == 'STENTOR_QCP':
                name_uuhscq = modality_name
                flag_uuhscq = True
            if flag_uuhscq:
                break

        # Load the lookup table
        answer, lookup_table = load_lookup_table(file_lookup)
        if answer['status'] != 0:
            output.AnswerBuffer(json.dumps(answer, indent=3), 'application/json')

        # Query the SQL database maps
        status, patient_map, patient_reverse_map, flag_siuid_to_anon = load_phi_to_anon_map()
        if status['status'] != 0:
            output.AnswerBuffer(json.dumps(status, indent=3), 'application/json')

        # Initialize output
        data_for_anonymize_gui = {'StudyMeta' : {},
                                  'SeriesMeta' : {},
                                  'DB' : {},
                                  'PACS' : {},
                                  'Lookup' : {}}
        study_date = {}

        # DICOM now on Orthanc
        response_studies = orthanc.RestApiGet('/studies')
        for ostudyid in json.loads(response_studies):

            flag_first_image = True
            meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % ostudyid))
            patient_id_modifier = ''
            study_instance_uid_modifier = ''
            if not ('AnonymizedFrom' in meta_study or 'ModifiedFrom' in meta_study):
        
                study_instance_uid = meta_study['MainDicomTags']['StudyInstanceUID'] + study_instance_uid_modifier
                patient_id = meta_study['PatientMainDicomTags']['PatientID'] + patient_id_modifier
                other_patient_ids = None
                if 'OtherPatientIDs' in meta_study['PatientMainDicomTags']:
                    other_patient_ids = meta_study['PatientMainDicomTags']['OtherPatientIDs'] + patient_id_modifier
                else:
                    if 'RETIRED_OtherPatientIDs' in meta_study['PatientMainDicomTags']:
                        other_patient_ids = meta_study['PatientMainDicomTags']['RETIRED_OtherPatientIDs'] + patient_id_modifier

                # Store the study meta
                data_for_anonymize_gui['StudyMeta'][ostudyid] = meta_study
                study_date[ostudyid] = meta_study['MainDicomTags']['StudyDate'] + 'T' + meta_study['MainDicomTags']['StudyTime']

                # Check the lookup table
                if len(lookup_table) > 0:
                    data_for_anonymize_gui['Lookup'][ostudyid] = {'Found': 0}
                    found, pacs_data = find_pacs_in_lookup_table(lookup_table, study_instance_uid, type_match='siuid')
                    if not found:
                        found, pacs_data = find_pacs_in_lookup_table(lookup_table, patient_id, type_match='patientid')
                    if pacs_data is not None:
                        data_for_anonymize_gui['Lookup'][ostudyid]['Found'] = 1
                        data_for_anonymize_gui['Lookup'][ostudyid]['Data'] = {}
                        for name, address in {'PatientName':'0010,0010',
                                              'PatientID':'0010,0020',
                                              'StudyDate':'0008,0020',
                                              'AccessionNumber':'0008,0050',
                                              'PatientBirthDate':'0010,0030'}.items():
                            if address in pacs_data:
                                data_for_anonymize_gui['Lookup'][ostudyid]['Data'][name] = pacs_data[address]['Value']

                # Check PACS
                if flag_uuhscq and flag_query_pacs:
                    pacs_data = None
                    data_for_anonymize_gui['PACS'][ostudyid] = {'Found': 0}
                    post_data = {'Level': 'Study',
                                 'Query' : {'StudyInstanceUID' : study_instance_uid, 
                                            'PatientID' : patient_id}}
                    meta_post = json.loads(orthanc.RestApiPost('/modalities/%s/query' % name_uuhscq, json.dumps(post_data)))
                    if 'ID' in meta_post:
                        meta_id = json.loads(orthanc.RestApiGet('/queries/%s' % meta_post['ID']))
                        if meta_id[0] == 'answers':
                            meta_answers = json.loads(orthanc.RestApiGet('/queries/%s/answers' % meta_post['ID']))
                            if len(meta_answers) > 0 and meta_answers[0] == '0':
                                meta_zero = json.loads(orthanc.RestApiGet('/queries/%s/answers/0' % meta_post['ID']))
                                if meta_zero[0] == 'content':
                                    pacs_data = json.loads(orthanc.RestApiGet('/queries/%s/answers/0/content' % meta_post['ID']))
                    
                    if pacs_data is not None:
                        data_for_anonymize_gui['PACS'][ostudyid]['Found'] = 1
                        data_for_anonymize_gui['PACS'][ostudyid]['Data'] = {}
                        for name, address in {'PatientName':'0010,0010',
                                              'PatientID':'0010,0020',
                                              'StudyDate':'0008,0020',
                                              'AccessionNumber':'0008,0050',
                                              'PatientBirthDate':'0010,0030'}.items():
                            if address in pacs_data:
                                data_for_anonymize_gui['PACS'][ostudyid]['Data'][name] = pacs_data[address]['Value']

                # First image
                if flag_first_image:
                
                    db = {'FoundPatientID': 0,
                          'FoundStudyInstanceUID': 0,
                          'FoundOtherStudyInstanceUID': 0,
                          'FoundNameAnon': 0}
                    pid = None
                    if patient_id in patient_reverse_map['Both']:
                        pid = patient_reverse_map['Both'][patient_id]
                    if pid is not None:
                        db['FoundPatientID'] = 1
                    else:
                        if other_patient_ids is not None and other_patient_ids in patient_reverse_map['Both']:
                            pid = patient_reverse_map['Both'][other_patient_ids]
                        if pid is not None:
                            db['FoundPatientID'] = 2
                    if pid is not None:
                        db['pid'] = pid
                        if 'InternalNumber' in patient_map[pid]:
                            db['InternalNumber'] = patient_map[pid]['InternalNumber']
                        else:
                            db['InternalNumber'] = 'NotYetAssigned'
                        if 'StudyInstanceUIDMap' in patient_map[pid] and len(patient_map[pid]['StudyInstanceUIDMap']) > 0:
                            other_study_instance_uids = []
                            for other_study_instance_uid, anon_study_instance_uid in patient_map[pid]['StudyInstanceUIDMap'].items():
                                if other_study_instance_uid not in other_study_instance_uids:
                                    other_study_instance_uids += [other_study_instance_uid]
                            if len(other_study_instance_uids) > 0:
                                db['FoundOtherStudyInstanceUID'] = 1
                                if len(other_study_instance_uids) == 1:
                                    db['OtherStudyInstanceUID'] = other_study_instance_uids[0]
                                else:
                                    db['OtherStudyInstanceUID'] = ','.join(other_study_instance_uids)
                        if flag_siuid_to_anon and 'SIUID2NameAnonMap' in patient_map[pid]:
                            if study_instance_uid in patient_map[pid]['SIUID2NameAnonMap']:
                                db['FoundStudyInstanceUID'] = 1
                                names = []
                                for name_anon in patient_map[pid]['SIUID2NameAnonMap'][study_instance_uid]:
                                    if name_anon not in names:
                                        names += [name_anon]
                                if len(names) > 0:
                                    db['FoundNameAnon'] = 1
                                    if len(names) == 1:
                                        db['NameAnon'] = names[0]
                                    else:
                                        db['NameAnon'] = ','.join(names)
                                
                    data_for_anonymize_gui['DB'][ostudyid] = db

                    # Store the series meta
                    for oseriesid in meta_study['Series']:
                        meta_series = json.loads(orthanc.RestApiGet('/series/%s' % oseriesid))
                        if 'Instances' in meta_series and len(meta_series['Instances']) > 0:
                            series_meta_table = {}
                            for tag in ['Manufacturer', 'Modality', 'StationName']:
                                if tag in meta_series:
                                    series_meta_table[tag] = meta_series[tag]
                            for oinstanceid in meta_series['Instances']:
                                meta_instance = json.loads(orthanc.RestApiGet('/instances/%s/simplified-tags' % oinstanceid))
                                if len(meta_instance) > 0:
                                    for tag in ['InstitutionAddress', 'InstitutionName', 'PatientAge', 'OtherPatientNames', 'Modality', 'IssuerOfPatientID']:
                                        series_meta_table[tag] = 'Unknown %s' % tag
                                        if tag in meta_instance:
                                            series_meta_table[tag] = meta_instance[tag]
                                    flag_first_image = False
                                    break
                            data_for_anonymize_gui['SeriesMeta'][ostudyid] = series_meta_table
                        if not flag_first_image:
                            break
                                            
        data_for_anonymize_gui['StudyDate'] = study_date
        output.AnswerBuffer(json.dumps(data_for_anonymize_gui, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def ScanInstanceForGroupElement(output, uri, **request):
    """API interface to scan_instance_for_group_element."""
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        orthanc_instance_id = request['groups'][0]
        if request['groups'][1] == '_':
            type_match='gggg'
        elif request['groups'][1] == '_regexp_':
            type_match='gggg-regexp'
        else:
            type_match='gggg-eeee'
        match_list = json.loads(request['body'])
        trigger_map = {}
        trigger_map = scan_instance_for_group_element(orthanc_instance_id, trigger_map, type_match=type_match, match_list=match_list)
        output.AnswerBuffer(json.dumps(trigger_map, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('POST')

# ============================================================================
def ScanInstanceForOddGroups(output, uri, **request):
    """API interface to scan_instance_for_group_element."""
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_instance_id = request['groups'][0]
        trigger_map = {}
        trigger_map = scan_instance_for_group_element(orthanc_instance_id, trigger_map, type_match='gggg-odd')
        output.AnswerBuffer(json.dumps(trigger_map, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def ScanSeriesForGroupElement(output, uri, **request):
    """API interface to scan_series_for_group_element."""
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        orthanc_series_id = request['groups'][0]
        if request['groups'][1] == '_':
            type_match='gggg'
        elif request['groups'][1] == '_regexp_':
            type_match='gggg-regexp'
        else:
            type_match='gggg-eeee'
        match_list = json.loads(request['body'])
        trigger_map = {}
        trigger_map = scan_series_for_group_element(orthanc_series_id, trigger_map, type_match=type_match, match_list=match_list)
        output.AnswerBuffer(json.dumps(trigger_map, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('POST')

# ============================================================================
def ScanSeriesForOddGroups(output, uri, **request):
    """API interface to scan_series_for_group_element."""
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_series_id = request['groups'][0]
        trigger_map = {}
        trigger_map = scan_series_for_group_element(orthanc_series_id, trigger_map, type_match='gggg-odd')
        output.AnswerBuffer(json.dumps(trigger_map, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def ScanStudyForGroupElement(output, uri, **request):
    """API interface to scan_series_for_group_element."""
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        orthanc_study_id = request['groups'][0]
        match_list = json.loads(request['body'])
        if request['groups'][1] == '_':
            type_match='gggg'
        elif request['groups'][1] == '_regexp_':
            type_match='gggg-regexp'
        else:
            type_match='gggg-eeee'
        trigger_map = {}
        trigger_map = scan_study_for_group_element(orthanc_study_id, trigger_map, type_match=type_match, match_list=match_list)
        output.AnswerBuffer(json.dumps(trigger_map, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('POST')

# ============================================================================
def ScanStudyForOddGroups(output, uri, **request):
    """API interface to scan_series_for_group_element."""
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_study_id = request['groups'][0]
        trigger_map = {}
        trigger_map = scan_study_for_group_element(orthanc_study_id, trigger_map, type_match='gggg-odd')
        output.AnswerBuffer(json.dumps(trigger_map, indent = 3), 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def Set2DOrCViewTomo(output, uri, **request):
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_series_id = request['groups'][0]
        patient_id_modifier = set_2d_or_cview_tomo(orthanc_study_id)
        output.AnswerBuffer(patient_id_modifier, 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def SetScreenOrDiagnostic(output, uri, **request):
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_study_id = request['groups'][0]
        patient_id_modifier = set_screen_or_diagnostic(orthanc_study_id)
        output.AnswerBuffer(patient_id_modifier, 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def ToggleLuaVerbose(output, uri, **request):
    """API to trigger setting gVerbose in Lua scripts"""
# ----------------------------------------------------------------------------

    if user_permitted(uri, get_remote_user(request['headers'])):
        try:
            response_post = orthanc.RestApiPost('/tools/execute-script', 'if gVerbose then print(1) else print(0) end')
            state = json.loads(response_post)
            if state == 1:
                orthanc.LogWarning('gVerbose is ON, turning OFF...')
                orthanc.RestApiPost('/tools/execute-script', 'gVerbose=nil')
                output.AnswerBuffer('gVerbose was ON, now OFF', 'text/plain')
            else:
                orthanc.LogWarning('gVerbose is OFF, turning ON...')
                orthanc.RestApiPost('/tools/execute-script', 'gVerbose=1')
                output.AnswerBuffer('gVerbose was OFF, now ON', 'text/plain')
        except:
            orthanc.LogWarning('Problem getting gVerbose state')
            output.AnswerBuffer('Problem getting gVerbose state', 'text/plain')
        
# ============================================================================
def TogglePythonMailAuto(output, uri, **request):
    """API to toggle the state of the PYTHON_MAIL_AUTO env variable"""
# ----------------------------------------------------------------------------

    if user_permitted(uri, get_remote_user(request['headers'])) and \
        'PYTHON_MAIL_AUTO' in os.environ:
        python_mail_auto_prev = os.environ['PYTHON_MAIL_AUTO']
        orthanc.LogWarning('Previous PYTHON_MAIL_AUTO: %s' % python_mail_auto_prev)
        if python_mail_auto_prev == 'true':
            os.environ['PYTHON_MAIL_AUTO'] = 'false'
        else:
            os.environ['PYTHON_MAIL_AUTO'] = 'true'
        python_mail_auto = os.environ['PYTHON_MAIL_AUTO']
        orthanc.LogWarning('Current PYTHON_MAIL_AUTO: %s' % python_mail_auto)
        if python_mail_auto == 'true':
            output.AnswerBuffer('Previous PYTHON_MAIL_AUTO: %s\nCurrent PYTHON_MAIL_AUTO: %s\nYou WILL receive email updates until this setting is reversed.' % (python_mail_auto_prev, python_mail_auto), 'text/plain')
        else:
            output.AnswerBuffer('Previous PYTHON_MAIL_AUTO: %s\nCurrent PYTHON_MAIL_AUTO: %s\nYou will NOT receive email updates until this setting is reversed.' % (python_mail_auto_prev, python_mail_auto), 'text/plain')

 # ============================================================================
def UpdateLookupTable(output, uri, **request):
    """ API to trigger update_lookup_table """
# ----------------------------------------------------------------------------
    status = update_lookup_html()
    if status['status'] != 0:
        output.AnswerBuffer(json.dumps(status, indent=3), 'application/json')
    else:
        output.AnswerBuffer('UpdateLookupTable: Success', 'text/plain')

# ============================================================================
# Main
orthanc.RegisterIncomingHttpRequestFilter(IncomingFilter)
orthanc.RegisterOnChangeCallback(OnChange)
orthanc.RegisterRestCallback('/confirm_or_create_lookup_table_sql', ConfirmOrCreateLookupTableSQL)
orthanc.RegisterRestCallback('/construct_patient_name', ConstructPatientName)
orthanc.RegisterRestCallback('/email_message', EmailSubjectMessage)
orthanc.RegisterRestCallback('/studies/(.*)/email_report', EmailStudyReport)
orthanc.RegisterRestCallback('/get_internal_number', GetInternalNumber)
orthanc.RegisterRestCallback('/studies/(.*)/jsanon', JSAnonymizeStudy)
orthanc.RegisterRestCallback('/prepare_data_for_anonymize', PrepareDataForAnonymizeGUI)
orthanc.RegisterRestCallback('/instances/(.*)/group(.*)recursive_search', ScanInstanceForGroupElement)
orthanc.RegisterRestCallback('/instances/(.*)/odd_group_recursive_search', ScanInstanceForOddGroups)
orthanc.RegisterRestCallback('/series/(.*)/group(.*)recursive_search', ScanSeriesForGroupElement)
orthanc.RegisterRestCallback('/series/(.*)/odd_group_recursive_search', ScanSeriesForOddGroups)
orthanc.RegisterRestCallback('/studies/(.*)/group(.*)recursive_search', ScanStudyForGroupElement)
orthanc.RegisterRestCallback('/studies/(.*)/odd_group_recursive_search', ScanStudyForOddGroups)
orthanc.RegisterRestCallback('/series/(.*)/set_2d_or_cview_tomo', Set2DOrCViewTomo)
orthanc.RegisterRestCallback('/studies/(.*)/set_screen_or_diagnostic', SetScreenOrDiagnostic)
orthanc.RegisterRestCallback('/toggle_lua_verbose', ToggleLuaVerbose)
orthanc.RegisterRestCallback('/toggle_python_mail_auto', TogglePythonMailAuto)
orthanc.RegisterRestCallback('/update_lookup_table', UpdateLookupTable)

