import json
import orthanc
import os
import re
import smtplib
import time
from email.message import EmailMessage
from email.headerregistry import Address

global_var = {'flag' : {}, 'regexp': {}}

# Regular expressions
global_var['regexp']['address'] = re.compile('([^<]+)<([^@]+)@([^>]+)>.*')

# Global variables
python_verbose_logwarning = os.getenv('PYTHON_VERBOSE_LOGWARNING', default='false') == 'true' or \
                            os.getenv('ORTHANC__PYTHON_VERBOSE', default='false') == 'true'
global_var['orthanc_configuration'] = json.loads(orthanc.GetConfiguration())
global_var['website'] = global_var['orthanc_configuration']['Name']
global_var['fqdn'] = os.getenv('HOST_FQDN', default='Unknown.Host')
global_var['log_indent_level'] = 0

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

# ----------------------------------------------------------------------------
# Inserting the above button definitions into the explorer
# ----------------------------------------------------------------------------
orthanc.ExtendOrthancExplorer(' '.join([button_js_patient_meta, button_js_patient_stats, \
                                        button_js_study_meta, button_js_study_stats, \
                                        button_js_series_meta, button_js_series_stats]))



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

    global global_var
    if python_verbose_logwarning:
        time_0 = time.time()
        frame = inspect.currentframe()
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3
 
    if alternates is None:
        if 'PYTHON_MAIL_TO' not in os.environ or \
           'PYTHON_MAIL_ORIGIN' not in os.environ or \
           'PYTHON_MAIL_SERVER' not in os.environ:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
                global_var['log_indent_level'] -= 3
            return{'status':1, 'error_text': 'Environmental variables for python mail not declared'}
        recipients = os.getenv('PYTHON_MAIL_TO').split(',')
    else:
        if 'PYTHON_MAIL_ORIGIN' not in os.environ or \
           'PYTHON_MAIL_SERVER' not in os.environ:
            if python_verbose_logwarning:
                orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
                global_var['log_indent_level'] -= 3
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
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
            global_var['log_indent_level'] -= 3
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
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
            global_var['log_indent_level'] -= 3
        return {'status':4, 'error_text':'email_message: Is the smtp down?'}
    s.send_message(msg)
    s.quit()

    if python_verbose_logwarning:
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] -= 3

    return {'status':0}

# =======================================================
def email_study_report(orthanc_study_id):
    """Generate email of study statistics"""
# -------------------------------------------------------

    global global_var
    if python_verbose_logwarning:
        time_0 = time.time()
        frame = inspect.currentframe()
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3

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

    if python_verbose_logwarning:
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] -= 3

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

# =======================================================
def user_permitted(uri, remote_user):
    """ Check remote user against list of permitted users """
# -------------------------------------------------------

    global global_var
    if python_verbose_logwarning:
        orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Checking whether remote user (%s) is permitted to act on %s' % (remote_user,uri))
    permissions = os.getenv('PYTHON_X_REMOTE_USER_ALLOWED_TO_TRIGGER')
    if permissions is None:
        if python_verbose_logwarning:
            orthanc.LogWarning(' ' * global_var['log_indent_level'] + 'Rejecting anon due to missing permissions')
        return False
    allowed_to_trigger = []
    for permitted in permissions.split('.'):
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

    global global_var
    global_var['log_indent_level'] = 0

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
def OnChange(change_type, level, resource_id):
    """
    PURPOSE: Manage incoming DICOM when a state change is detected
    INPUT:   structures routed by way of the python plugin
    OUTPUT:  Designated action
    """
# ----------------------------------------------------------------------------

    if change_type == orthanc.ChangeType.STABLE_STUDY:

        # Email updates
        if os.getenv('PYTHON_MAIL_AUTO', default='false') == 'true':
            status = email_study_report(resource_id)
            if status['status'] != 0:
                if python_verbose_logwarning:
                    orthanc.LogWarning(status['error_text'])
            else:
                if python_verbose_logwarning:
                    orthanc.LogWarning("Sent onstable study report")

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
orthanc.RegisterRestCallback('/toggle_lua_verbose', ToggleLuaVerbose)
