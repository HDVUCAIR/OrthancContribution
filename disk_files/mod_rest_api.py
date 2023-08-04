import orthanc
import json
import datetime
import os
import stat
import pydicom
import io
import smtplib
import re
from email.message import EmailMessage
from email.headerregistry import Address

global_var = {'flag' : {}, 'privileged' : {}, 'regexp': {}}

# Regular expressions
global_var['regexp']['address'] = re.compile('([^<]+)<([^@]+)@([^>]+)>.*')

# Global variables
python_verbose_logwarning = os.getenv('PYTHON_VERBOSE_LOGWARNING', default='false') == 'true' or \
                            os.getenv('ORTHANC__PYTHON_VERBOSE', default='false') == 'true'

global_var['flag']['auto_anon'] = os.getenv('PYTHON_FLAG_AUTO_ANON_WHEN_STABLE', default='false') == 'true'
global_var['flag']['write_dicom'] = os.getenv('PYTHON_WRITE_DICOM_DEFAULT', default='false') == 'true'
global_var['fqdn'] = os.getenv('HOST_FQDN', default='Unknown.Host')
global_var['privileged']['ip'] = os.getenv('PYTHON_X_REMOTE_IP_ALLOWED_TO_TRIGGER')
global_var['privileged']['user'] = os.getenv('PYTHON_X_REMOTE_USER_ALLOWED_TO_TRIGGER')
global_var['log_indent_level'] = 0
global_var['website'] = os.getenv('ORTHANC__NAME', default='UnknownOrthanc')

# Set the umask to u=+rwx,g=+rx,o= (octal 0o027)
os.umask(0o027)

# ============================================================================
# Modify the GUI
# ============================================================================
# Buttons on patient page
# ----------------------------------------------------------------------------
# Same as API patients/uid
button_js_patient_meta = "$('#patient').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Patient Metadata');" + \
                       " b.insertBefore($('#patient-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/patients/' + uuid);" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# Same as API patients/uid/statistics
button_js_patient_stats = "$('#patient').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Patient Stats');" + \
                       " b.insertBefore($('#patient-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/patients/' + uuid + '/statistics');" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# ----------------------------------------------------------------------------
# Buttons on study page
# ----------------------------------------------------------------------------
# Same as API studies/uid
button_js_study_meta = "$('#study').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Study Metadata');" + \
                       " b.insertBefore($('#study-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/studies/' + uuid);" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# Same as API studies/uid/statistics
button_js_study_stats = "$('#study').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Study Stats');" + \
                       " b.insertBefore($('#study-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/studies/' + uuid + '/statistics');" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# Trigger a dump to disk for the study
button_js_study_to_disk = "$('#study').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Send Study To Disk');" + \
                       " b.insertBefore($('#study-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/studies/' + uuid + '/send_to_disk');" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# ----------------------------------------------------------------------------
# Buttons on series page
# ----------------------------------------------------------------------------
# Same as API series/uid
button_js_series_meta = "$('#series').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Series Metadata');" + \
                       " b.insertBefore($('#series-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/series/' + uuid);" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# Same as API series/uid/statistics
button_js_series_stats = "$('#series').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Series Stats');" + \
                       " b.insertBefore($('#series-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/series/' + uuid + '/statistics');" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# Dump the series to disk
button_js_series_to_disk = "$('#series').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-icon', 'action')" + \
                         " .attr('data-theme', 'e')" + \
                         " .text('Send Series To Disk');" + \
                       " b.insertBefore($('#series-delete').parent().parent());" + \
                       " b.click(function() {" + \
                         " var uuid='none'; " + \
                         " if ($.mobile.pageData) {" + \
                         "   uuid = $.mobile.pageData.uuid" + \
                         " };" + \
                         " window.open('/%s/series/' + uuid + '/send_to_disk');" % global_var['website'] + \
                         "}" + \
                       ");" + \
                     "});"

# ----------------------------------------------------------------------------
# Inserting the above button definitions into the explorer
# ----------------------------------------------------------------------------
orthanc.ExtendOrthancExplorer(' '.join([button_js_patient_meta, button_js_patient_stats, \
                                        button_js_study_meta, button_js_study_stats, button_js_study_to_disk, \
                                        button_js_series_meta, button_js_series_stats, button_js_series_to_disk]))


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
        address_res = global_var['regexp']['address'].match(address_trim)
        if address_res is not None:
            addresses += [Address(address_res.group(1),address_res.group(2),address_res.group(3))]
    if cc is not None:
        for address_text in cc.split(','):
            address_trim = address_text.strip()
            address_res = global_var['regexp']['address'].match(address_trim)
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
    try:
        s = smtplib.SMTP(smtp_server)
    except:
        return {'status':3, 'error_text':'email_message: Is the smtp down?'}
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
    if 'PatientName' in meta_study['PatientMainDicomTags'] and len(meta_study['PatientMainDicomTags']['PatientName'].strip()) > 0:
        patient_name = meta_study['PatientMainDicomTags']['PatientName']
    else:
        patient_name = 'None'
    orthanc_patient_id = meta_study['ParentPatient']

    response_statistics = orthanc.RestApiGet('/studies/%s/statistics' % orthanc_study_id)
    meta_statistics = json.loads(response_statistics)

    msg = EmailMessage()
    message_body = ['<html>', ' '*2 + '<head></head>', ' '*2 + '<body>']
    message_body += [' '*4 + '<h1>Study Report</h1>']
    message_body += [' '*4 + '<h2>Study Info</h2>']

    # Main study info
    message_body += [' '*4 + '<table border=1>']
    message_body += [' '*6 + '<tr><th>Item</th><th>Value</th></tr>']
    message_body += [' '*6 + '<tr><td>Study</td><td><a href="https://%s/%s/app/explorer.html#study?uuid=%s">%s</a></td></tr>' % (global_var['fqdn'], global_var['website'], orthanc_study_id,study_description)]
    message_body += [' '*6 + '<tr><td>Patient</td><td><a href="https://%s/%s/app/explorer.html#patient?uuid=%s">%s</a></td></tr>' % (global_var['fqdn'], global_var['website'], orthanc_patient_id,patient_name)]
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
                line_of_text += '<td><a href="https://%s/%s/app/explorer.html#series?uuid=%s">%s</a></td>' % (global_var['fqdn'], global_var['website'], series_data[series_number]['orthanc_series_id'],series_data[series_number][key])
            else:
                line_of_text += '<td>%s</td>' % series_data[series_number][key]
        line_of_text += '</tr>'
        message_body += [line_of_text]

    message_body += [' '*2 + '</body>', '</html>']
    return email_message('PHI Study Report from %s' % aet, '\n'.join( message_body), subtype='html')

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
def series_to_disk(orthanc_series_id, study_data=None, flag_write_dicom=global_var['flag']['write_dicom']):
    """
    PURPOSE:  Write selected series to disk
    INPUT:    Orthanc ID for series
    OUTPUT:  Writes to the directory at /dicomout
    """
# ----------------------------------------------------------------------------

    try:
        response_series = orthanc.RestApiGet('/series/%s' % orthanc_series_id)
    except ValueError as e:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem querying series: %s' % orthanc_series_id)
        return {'status' : 1, 'error_text' : 'Problem querying series'}
    except orthanc.OrthancException as e:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem querying series: %s' % orthanc_series_id)
        orthanc.LogWarning(e)
        if e.args[0] == orthanc.ErrorCode.UNKNOWN_RESOURCE:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Unknown resource')
        return {'status' : 2, 'error_text' : 'Unknown resource'}
    meta_series = json.loads(response_series)

    # Pull study specific info if we don't have it
    if study_data is None:
        status, study_data = useful_study_data(meta_series['ParentStudy'])
        if status['status'] != 0:
            return {'status' : status['status']+100, 'error_text' : status['error_text']}
        if 'Modality' in meta_series['MainDicomTags']:
            study_data['modality'] = meta_series['MainDicomTags']['Modality'].strip()
        else:
            study_data['modality'] = ''

    # Grab series specific information
    series_number = meta_series['MainDicomTags']['SeriesNumber'].strip()
    series_description = ''
    if 'SeriesDescription' in meta_series['MainDicomTags']:
        series_description = meta_series['MainDicomTags']['SeriesDescription'].strip().replace('/',':')
    series_description = series_description.replace('*','_star')
    series_time = meta_series['MainDicomTags']['SeriesTime'].strip()

    # Construct the output paths
    dir_path = '/dicomout' 
    dir_path = '%s/%06d_%06d' % (dir_path,study_data['internal_number_lo'], study_data['internal_number_hi'])
    dir_path = '%s/%s' % (dir_path, study_data['internal_number_str'])
    dir_path = '%s/%s' % (dir_path, study_data['base'])
    dir_path = '%s/%s%s%s' % (dir_path, study_data['StudyDate'], study_data['StudyTime'][0:6], study_data['modality'])

    dir_path_dicom = '%s/DicomData' % dir_path
    dir_path_raw = '%s/RawData' % dir_path
    dir_path_analysis = '%s/Analysis' % dir_path
    if len(series_number) > 0:
        if len(series_description) > 0:
            dir_path_dicom = '%s/s%06d %s' % (dir_path_dicom, int(series_number), series_description)
        else:
            dir_path_dicom = '%s/s%06d' % (dir_path_dicom, int(series_number))
    else:
        if len(series_description) > 0:
            dir_path_dicom = '%s/%s' % (dir_path_dicom, series_description)

    # Create the directories
    try:
        os.makedirs(dir_path_dicom, exist_ok=True)
        os.makedirs(dir_path_raw, exist_ok=True)
        os.makedirs(dir_path_analysis, exist_ok=True)
        os.chmod(dir_path_analysis, stat.S_IRWXU | stat.S_IRWXG | stat.S_ISGID)
    except:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem creating directories')
        return {'status' : 4, 'error_text' : 'Problem creating directories'}

    # Dump the instances to disk
    if flag_write_dicom:

        for orthanc_instance_id in meta_series['Instances']:

            meta_instance = json.loads(orthanc.RestApiGet('/instances/%s' % orthanc_instance_id))
            instance_number = meta_instance['MainDicomTags']['InstanceNumber'].strip()
            sop_instance_uid = meta_instance['MainDicomTags']['SOPInstanceUID']
            if len(instance_number) > 0:
                file_dicom = '%s/i%06d_%s.dcm' % (dir_path_dicom, int(instance_number), sop_instance_uid)
            else:
                file_dicom = '%s/%s.dcm' % (dir_path_dicom, sop_instance_uid)
            if os.path.exists(file_dicom):
                if python_verbose_logwarning:
                    orthanc.LogWarning(' ' * global_var['log_indent_level'] + '%s exists.  Skipping' % file_dicom)
            else:
                if python_verbose_logwarning:
                    orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Writing %s' % file_dicom)
                file_blob = orthanc.RestApiGet('/instances/%s/file' % orthanc_instance_id)
                dicom_struct = pydicom.dcmread(io.BytesIO(file_blob))
                dicom_struct.save_as(file_dicom)

    return {'status' : 0, 'error_text' : ''}

# ============================================================================
def study_to_disk(orthanc_study_id, flag_write_dicom=global_var['flag']['write_dicom']):
    """
    PURPOSE:  Write selected study to disk
    INPUT:    Orthanc ID for study
    RETURNS:  integer status code
    OUTPUT:   Writes to the directory at /dicomout
    """
# ----------------------------------------------------------------------------

    if flag_write_dicom:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Triggered anon:\n   Directories will be created.\n   DICOM will be written.')
    else:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Stable anon:\n   Directories will be created.\n   DICOM will NOT be written.')

    # Extract data used in directory names
    status, study_data, meta_study = useful_study_data(orthanc_study_id, return_meta=True)
    if status['status'] != 0:
        return {'status' : status['status']+100, 'error_text' : status['error_text']}

    # Determine dominent modality
    modalities = {}
    modality_max = 0
    modality_winner = None
    for orthanc_series_id in meta_study['Series']:
        meta_series = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id))
        if 'Modality' not in meta_series['MainDicomTags']:
            continue
        modality = meta_series['MainDicomTags']['Modality']
        if modality not in modalities:
            modalities[modality] = 0
        modalities[modality] += 1
        if modalities[modality] > modality_max:
            modality_max = modalities[modality]
            modality_winner = modality

    if modality_winner is None:
        study_data['modality'] = ''
    else:
        study_data['modality'] = modality_winner

    # Now dump the series
    for orthanc_series_id in meta_study['Series']:
        status = series_to_disk(orthanc_series_id, study_data=study_data, flag_write_dicom=flag_write_dicom)
        if status['status'] != 0:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem dumping series to disk')
            return {'status' : status['status']+1000, 'error_text' : 'Problem dumping to disk %s' % status['error_text']}

    return {'status' : 0, 'error_text' : ''}

# ============================================================================
def useful_study_data(orthanc_study_id, return_meta=False):
    """
    PURPOSE:  Extract some useful study data for constructing output
                 directories
    INPUT:    Orthanc ID for study
    OUTPUT:   Pulls data later used for constructing directories
    """
# ----------------------------------------------------------------------------

    try:
        response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    except:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem querying study: %s' % orthanc_study_id)
        return {'status' : 1, 'error_text': 'Problem getting study meta'}, {}

    meta_study = json.loads(response_study)
    study_data = {}
    for value in ['StudyDate', 'StudyTime']:
        if value not in meta_study['MainDicomTags']:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'No %s found in meta data, skipping' % value)
            return {'status' : 1, 'error_text': 'Missing %s in meta data' % value}, {}
        study_data[value] = meta_study['MainDicomTags'][value]
    for value in ['PatientName', 'PatientID']:
        if value not in meta_study['PatientMainDicomTags']:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'No %s foudn in meta data, skipping' % value)
            return {'status' : 1, 'error_text': 'Missing %s in meta data' % value}, {}
        study_data[value] = meta_study['PatientMainDicomTags'][value]
    for value in ['StudyDescription', 'AccessionNumber']:
        if value in meta_study['MainDicomTags'] and len(meta_study['MainDicomTags'][value].strip()) > 0:
            study_data[value] = meta_study['MainDicomTags'][value].strip()
        else:
            study_data[value] = None

    patient_name_parts = study_data['PatientName'].split('^')
    study_data['base'] = patient_name_parts[0]
    study_data['internal_number_str'] = patient_name_parts[1][2:]
    study_data['internal_number'] = int(study_data['internal_number_str'])
    study_data['internal_number_lo'] = (study_data['internal_number'] // 50) * 50
    study_data['internal_number_hi'] = study_data['internal_number_lo'] + 49

    if return_meta:
        return {'status' : 0, 'error_text': ''}, study_data, meta_study
    else:
        return {'status' : 0, 'error_text': ''}, study_data

# =======================================================
def user_permitted(uri, remote_user):
    """ Check remote user against list of permitted users """
# -------------------------------------------------------

    if python_verbose_logwarning:
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Checking whether remote user (%s) is permitted to \n%s' % (remote_user,uri))
    permissions = global_var['privileged']['user']
    if permissions is None:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Rejecting anon due to missing permissions')
        return False
    allowed_to_trigger = []
    for permitted in permissions.split(','):
        if permitted.strip() not in allowed_to_trigger:
            allowed_to_trigger += [permitted.strip()]
    if python_verbose_logwarning:
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Allowed users: %s' % ' '.join(allowed_to_trigger))
    if remote_user not in allowed_to_trigger:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Operation not permitted to user: %s %s' % (uri, remote_user))
        return False
    if python_verbose_logwarning:
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Remote user is permitted (%s)' % remote_user)

    return True

# =======================================================
def EmailStudyReport(output, uri, **request):
    """API interface to generate and send email report on study"""
# -------------------------------------------------------
    if request['method'] == 'GET':
        orthanc_study_id = request['groups'][0]
        status = email_study_report(orthanc_study_id)
        if status['status'] != 0:
            output.AnswerBuffer('Problem generating email report: %s' % status['error_text'], 'text/plain')
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
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Rejecting incoming access: %s' % headers_str)
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
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + '%s %s %s %s' % (remote_user, remote_ip, method, uri))

    if method in ['DELETE', 'PUT']:
        return user_permitted(uri, remote_user)
        
    if method == 'POST' and (uri.find('/execute-script') >= 0):
        return user_permitted(uri, remote_user)

    if uri.find('anonymize') >= 0:
        return False

    return True

# ============================================================================
def ManualSendToDisk(output, uri, **request):
    """
    PURPOSE:   Allow users to manually trigger writing a study/series to disk
    """
# ----------------------------------------------------------------------------

    if request['method'] == 'GET':

        orthanc_id = request['groups'][1]
        remote_user = get_remote_user(request['headers'])
        if 'x-forwarded-for' in request['headers']:
            remote_ip = request['headers']['x-forwarded-for']
        elif 'host' in request['headers']:
            remote_ip = request['headers']['host']
        else:
            remote_ip = ''

        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Send to disk triggered for %s' % orthanc_id)
        status_email = email_message('Initiated send to disk', '<a href="https://%s/%s/app/explorer.html#study?uuid=%s">Study</a> send to disk initiated by %s from %s' % (global_var['fqdn'], global_var['website'], orthanc_id,remote_user,remote_ip), subtype='html')
        if status_email['status'] != 0:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem sending email prior to send to disk')
            output.AnswerBuffer('Problem sending email prior to send to disk\n%s' % status_email['error_text'], 'text/plain')
            return
        status = {'status' : 1, 'error_text' : 'Invalid send to disk option'}
        if request['groups'][0] == 'studies':
            status = study_to_disk(orthanc_id, flag_write_dicom=True)
        if request['groups'][0] == 'series':
            status = series_to_disk(orthanc_id, flag_write_dicom=True)

        if status['status'] != 0:
            status_email = email_message('Failed to send to disk', '<a href="https://%s/%s/app/explorer.html#study?uuid=%s">Study</a> failed to send to disk for %s from %s: %s' % (global_var['fqdn'], global_var['website'], orthanc_id, remote_user, remote_ip, status['error_text']), subtype='html')
            output.LogWarning('Failed to send to disk')
            output.AnswerBuffer('Failed to send to disk', 'text/plain')
            return
        status_email = email_message('Completed send to disk', '<a href="https://%s/%s/app/explorer.html#study?uuid=%s">Study</a> send to disk completed for %s from %s' % (global_var['fqdn'], global_var['website'], orthanc_id, remote_user, remote_ip), subtype='html')
        if status_email['status'] != 0:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem sending email after to send to disk')
            output.AnswerBuffer('Problem sending email after send to disk', 'text/plain')
            return
        output.AnswerBuffer('Successfully wrote study to disk', 'text/plain')
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Send to disk complete for %s' % orthanc_id)

    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def OnChange(change_type, level, resource_id):
    """
    PURPOSE: Manage incoming DICOM when a state change is detected
    INPUT:   structures routed by way of the python plugin
    OUTPUT:  Designated action
    """
# ----------------------------------------------------------------------------

    if change_type == orthanc.ChangeType.STABLE_STUDY:

        # Email updates
        if os.getenv('PYTHON_MAIL_AUTO') == 'true':
            status = email_study_report(resource_id)
            if status['status'] != 0:
                orthanc.LogWarning(status['error_text'])
            else:
                orthanc.LogWarning("Sent onstable study report")

        # Save to disk
        if global_var['flag']['auto_anon']:
            status = study_to_disk(resource_id)
            if status['status'] != 0:
                if python_verbose_logwarning:
                    orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem sending stable study to disk: %s %s' % (resource_id, status['error_text']))

# ============================================================================
def ToggleLuaVerbose(output, uri, **request):
    """API to trigger setting gVerbose in Lua scripts"""
# ----------------------------------------------------------------------------

    if user_permitted(uri, get_remote_user(request['headers'])):
        try:
            response_post = orthanc.RestApiPost('/tools/execute-script', 'if gVerbose then print(1) else print(0) end')
            state = json.loads(response_post)
            if state == 1:
                if python_verbose_logwarning:
                    orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'gVerbose is ON, turning OFF...')
                orthanc.RestApiPost('/tools/execute-script', 'gVerbose=nil')
                output.AnswerBuffer('gVerbose was ON, now OFF', 'text/plain')
            else:
                if python_verbose_logwarning:
                    orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'gVerbose is OFF, turning ON...')
                orthanc.RestApiPost('/tools/execute-script', 'gVerbose=1')
                output.AnswerBuffer('gVerbose was OFF, now ON', 'text/plain')
        except:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Problem getting gVerbose state')
            output.AnswerBuffer('Problem getting gVerbose state', 'text/plain')

# ============================================================================
# Main
orthanc.RegisterIncomingHttpRequestFilter(IncomingFilter)
orthanc.RegisterOnChangeCallback(OnChange)
orthanc.RegisterRestCallback('/email_message', EmailSubjectMessage)
orthanc.RegisterRestCallback('/studies/(.*)/email_report', EmailStudyReport)
orthanc.RegisterRestCallback('/(studies|series)/(.*)/send_to_disk', ManualSendToDisk)
orthanc.RegisterRestCallback('/toggle_lua_verbose', ToggleLuaVerbose)
