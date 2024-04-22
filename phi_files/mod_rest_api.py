import copy
import datetime
import inspect
import json
import numbers
import orthanc
import os
import pprint
import random
import re
import smtplib
import threading
import time
import string
from email.message import EmailMessage
from email.headerregistry import Address

global_var = {'flag' : {}, 'regexp': {}}
try:
    from bs4 import BeautifulSoup
    global_var['flag']['beautiful_soup'] = True
except:
    global_var['flag']['beautiful_soup'] = False
try:
    import psycopg2
    global_var['flag']['psycopg2'] = True
except:
    global_var['flag']['psycopg2'] = False

# Regular expressions
global_var['regexp']['address'] = re.compile('([^<]+)<([^@]+)@([^>]+)>.*')

# Global variables
python_verbose_logwarning = 1 if os.getenv('PYTHON_VERBOSE_LOGWARNING', default='false') == 'true' or os.getenv('ORTHANC__PYTHON_VERBOSE', default='false') == 'true' else 0
global_var['orthanc_configuration'] = json.loads(orthanc.GetConfiguration())
global_var['website'] = global_var['orthanc_configuration']['Name']
global_var['fqdn'] = os.getenv('HOST_FQDN', default='Unknown.Host')

global_var['address_constructor'] = []
global_var['address_list'] = {}
global_var['anonymization_queue'] = {}
global_var['flag_force_anon'] = False
global_var['irb_label_regex_map'] = json.loads(os.getenv('PYTHON_IRB_LABEL_REGEXP_MAP', default='{}'))
global_var['irb_re'] = re.compile('^irb.*', re.IGNORECASE)
global_var['kept_uid'] = {}
global_var['log_indent_level'] = 0
global_var['max_recurse_depth'] = 20
global_var['patient_name_base'] = None
global_var['patient_name_id_char'] = 'ID'
global_var['top_level_tag_to_keep'] = {}
global_var['uid_map'] = None
global_var['log_user'] = {}

# ============================================================================
# Modify the GUI
# ============================================================================
# Buttons on the main landing page
# ----------------------------------------------------------------------------
button_js_system_meta = "$('#lookup').live('pagebeforecreate', function() {" + \
                           " var b = $('<a>')" + \
                             " .attr('data-role', 'button')" + \
                             " .attr('href', '#')" + \
                             " .attr('data-theme', 'b')" + \
                             " .text('System Settings');" + \
                           " b.insertAfter($('#content').parent());" + \
                           " b.click(function() {" + \
                             " var uuid='none'; " + \
                             " if ($.mobile.pageData) {" + \
                             "   uuid = $.mobile.pageData.uuid" + \
                             " };" + \
                             " window.open('/%s/system');" % global_var['website'] + \
                             "}" + \
                           ");" + \
                         "});"

button_js_system_stats = "$('#lookup').live('pagebeforecreate', function() {" + \
                           " var b = $('<a>')" + \
                             " .attr('data-role', 'button')" + \
                             " .attr('href', '#')" + \
                             " .attr('data-theme', 'b')" + \
                             " .text('System Stats');" + \
                           " b.insertAfter($('#content').parent());" + \
                           " b.click(function() {" + \
                             " var uuid='none'; " + \
                             " if ($.mobile.pageData) {" + \
                             "   uuid = $.mobile.pageData.uuid" + \
                             " };" + \
                             " window.open('/%s/statistics');" % global_var['website'] + \
                             "}" + \
                           ");" + \
                         "});"

button_js_anonymize_by_label = "$('#lookup').live('pagebeforecreate', function() {" + \
                           " var b = $('<a>')" + \
                             " .attr('data-role', 'button')" + \
                             " .attr('href', '#')" + \
                             " .attr('data-theme', 'b')" + \
                             " .text('Anonymize By Label');" + \
                           " b.insertAfter($('#content').parent());" + \
                           " b.click(function() {" + \
                             " var uuid='none'; " + \
                             " if ($.mobile.pageData) {" + \
                             "   uuid = $.mobile.pageData.uuid" + \
                             " };" + \
                             " window.open('/%s/anonymize_by_label');" % global_var['website'] + \
                             "}" + \
                           ");" + \
                         "});"

# ----------------------------------------------------------------------------
# Buttons on patient page
# ----------------------------------------------------------------------------
# Same as API patients/uid
button_js_patient_meta = "$('#patient').live('pagebeforecreate', function() {" + \
                       " var b = $('<a>')" + \
                         " .attr('data-role', 'button')" + \
                         " .attr('href', '#')" + \
                         " .attr('data-theme', 'b')" + \
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
                         " .attr('data-theme', 'b')" + \
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
                         " .attr('data-theme', 'b')" + \
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
                         " .attr('data-theme', 'b')" + \
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
                         " .attr('data-theme', 'b')" + \
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
                         " .attr('data-theme', 'b')" + \
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
orthanc.ExtendOrthancExplorer(' '.join([button_js_system_meta, button_js_system_stats, button_js_anonymize_by_label, \
                                        button_js_patient_meta, button_js_patient_stats, \
                                        button_js_study_meta, button_js_study_stats, \
                                        button_js_series_meta, button_js_series_stats]))

# ============================================================================
def anonymize_by_label_init():
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning
    if log_message_bitflag:
        global_var['log_indent_level'] = 0
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3

    global_var['anonymization_queue'] = {} 
    meta_system = json.loads(orthanc.RestApiGet('/system'))

    # Propagate any irb labels from patient level
    anonymize_by_label_inherit_from_patient()

    # Construct html headers
    answer_buffer = []
    answer_buffer += ['<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-us">\n']
    answer_buffer += ['<head>\n']
    answer_buffer += ['<link rel="stylesheet" href="./extra/lookup/master/style.css" type="text/css" id="" media="print, projection, screen" />\n']
    answer_buffer += ['<link rel="stylesheet" href="./extra/lookup/master/theme.blue.min.css">\n']
    answer_buffer += ['<style>th,td { white-space: nowrap; }</style>']
    answer_buffer += ['<script type="text/javascript" src="./app/libs/jquery.min.js"></script>\n']
    answer_buffer += ['<script type="text/javascript" src="./extra/lookup/master/jquery.tablesorter.combined.min.js"></script>\n']
    answer_buffer += ['<script type="text/javascript">\n']
    answer_buffer += ['$(document).ready(function() { \n']
    answer_buffer += ['    // call the tablesorter plugin \n']
    answer_buffer += ['    $("table").tablesorter({\n']
    answer_buffer += ['        theme: "blue",\n']
    answer_buffer += ['        widgets: ["zebra", "filter"],\n']
    answer_buffer += ['        widgetOptions : {\n']
    answer_buffer += ['            filter_columnFilters: true,\n']
    answer_buffer += ['            filter_reset: ".reset",\n']
    answer_buffer += ['            zebra : [ "normal-row", "alt-row" ]\n']
    answer_buffer += ['        },\n']
    answer_buffer += ['        sortList : [[2,0]]\n']
    answer_buffer += ['    }); \n']
    answer_buffer += ['}); \n']
    answer_buffer += ['</script>\n']

    # Find labeled studies
    studies_with_labels = {}
    orthanc_study_ids = json.loads(orthanc.RestApiGet('/studies'))
    for orthanc_study_id in orthanc_study_ids:
        labels = json.loads(orthanc.RestApiGet('/studies/%s/labels' % orthanc_study_id))
        irb_label = None
        for label in labels:
            if global_var['irb_re'].match(label) is not None:
                irb_label = label
                break
        if irb_label is not None:
            studies_with_labels[orthanc_study_id] = {'label' : irb_label}

    # Determine if previously anonymized
    if len(studies_with_labels) == 0:
        answer_buffer += ['</head>\n']
        answer_buffer += ['<body>\n']
        answer_buffer += ['<a href="./app/explorer.html">Return to Orthanc home page</a></br>\n']
        answer_buffer += ['No labeled studies to report.']
    else:
        for orthanc_study_id, orthanc_study_dict in studies_with_labels.items():
            anonymization_history = anonymization_history_get(orthanc_study_id)
            if len(anonymization_history) > 0:
                if 'AnonymizedTo' in anonymization_history:
                    for orthanc_study_id_anon, anonymization_atoms in anonymization_history['AnonymizedTo'].items():
                        if orthanc_study_id_anon in orthanc_study_ids:
                            if 'AnonymizedTo' not in studies_with_labels[orthanc_study_id]:
                                studies_with_labels[orthanc_study_id]['AnonymizedTo'] = {}
                            if orthanc_study_id_anon not in studies_with_labels[orthanc_study_id]['AnonymizedTo']:
                                studies_with_labels[orthanc_study_id]['AnonymizedTo'][orthanc_study_id_anon] = []
                            studies_with_labels[orthanc_study_id]['AnonymizedTo'][orthanc_study_id_anon] += anonymization_atoms
            for orthanc_study_id_anon in orthanc_study_ids:
                anonymization_history_anon = anonymization_history_get(orthanc_study_id_anon)
                if len(anonymization_history_anon) > 0:
                    if 'AnonymizedFrom' in anonymization_history_anon:
                        for orthanc_study_id_parent, anonymization_atoms in anonymization_history_anon['AnonymizedFrom'].items():
                            if orthanc_study_id_parent == orthanc_study_id:
                                if 'AnonymizedTo' not in studies_with_labels[orthanc_study_id]:
                                    studies_with_labels[orthanc_study_id]['AnonymizedTo'] = {}
                                if orthanc_study_id_anon not in studies_with_labels[orthanc_study_id]['AnonymizedTo']:
                                    studies_with_labels[orthanc_study_id]['AnonymizedTo'][orthanc_study_id_anon] = []
                                studies_with_labels[orthanc_study_id]['AnonymizedTo'][orthanc_study_id_anon] += anonymization_atoms

        # Set up the queue and normalize the labels
        for orthanc_study_id, orthanc_study_dict in studies_with_labels.items():
            if 'AnonymizedTo' not in orthanc_study_dict:
                parameters_irb = irb_label_regex_map(orthanc_study_dict['label'])
                global_var['anonymization_queue'][orthanc_study_id] = parameters_irb
                if parameters_irb['irb_standard'] != orthanc_study_dict['label']:
                    orthanc.RestApiDelete('/studies/%s/labels/%s' % (orthanc_study_id, orthanc_study_dict['label']))
                    orthanc.RestApiPut('/studies/%s/labels/%s' % (orthanc_study_id, parameters_irb['irb_standard']), json.dumps({}))
                    studies_with_labels[orthanc_study_id]['label'] = parameters_irb['irb_standard']
 
        # Finish the HTML header
        if len(global_var['anonymization_queue']) > 0:
            answer_buffer += ['<script type="text/javascript">\n']
            answer_buffer += ['var irb_label_map = {\n']
            for irb_standard, irb_dict in global_var['irb_label_regex_map'].items():
                answer_buffer += ['%s: "%s",\n' % (irb_standard, irb_dict['name_base'])]
            for irb_standard, irb_dict in {'irbdefault' : {'name_base' : meta_system['Name']}}.items():
                answer_buffer += ['%s: "%s"\n' % (irb_standard, irb_dict['name_base'])]
            answer_buffer += ['};\n']
            answer_buffer_oid = []
            for orthanc_study_id, orthanc_study_dict in studies_with_labels.items():
                if 'AnonymizedTo' not in orthanc_study_dict:
                    answer_buffer_oid += ['"%s"' % orthanc_study_id]
            answer_buffer += ['var orthanc_study_ids = [%s];\n' % ','.join(answer_buffer_oid)]
            answer_buffer += ["$( window ).on( 'load', function() {\n"]
            answer_buffer += ["   $( '#abl_initiate_anon' ).click( function() {\n"]
            answer_buffer += ['      var text = "Anonymizations to perform:\\n\\n";\n']
            answer_buffer += ['      for (let i = 0; i < orthanc_study_ids.length; i++) {\n']
            answer_buffer += ['         text += "(Accession " + $( "#accession_" + orthanc_study_ids[i] ).text()+ ", Date " + $( "#date_" + orthanc_study_ids[i] ).text() + ") : " + $( "#name_base_" + orthanc_study_ids[i] ).text() + $( "#extra_" + orthanc_study_ids[i] ).val() + "^ID######^^^\\n\\n";\n']
            answer_buffer += ['      }\n']
            answer_buffer += ['      text += "Proceed with anonymization?"\n']
            answer_buffer += ["      var proceed = confirm(text);\n"]
            answer_buffer += ['      if (proceed == false) {\n']
            answer_buffer += ['         return;\n']
            answer_buffer += ['      } \n']
            answer_buffer += ['      $.post("./anonymize_by_label_run", \n']
            answer_buffer += ['             {data : ""},\n']
            answer_buffer += ['             function(result,status){\n']
            answer_buffer += ['                stop_prog = 1;\n']
            answer_buffer += ['                if (status == "success") {\n']
            answer_buffer += ["                   alert('Reload the following page to see progress.');\n"]
            answer_buffer += ['                   window.location.href = result;\n']
#            answer_buffer += ['                   location.reload();\n']
            answer_buffer += ['                } else {\n']
            answer_buffer += ['                   alert("Problem with anon: " + status);\n']
            answer_buffer += ['                }\n']
            answer_buffer += ['             }\n']
            answer_buffer += ['         );\n']
            answer_buffer += ['     });\n']
            answer_buffer += ['});\n']
            for orthanc_study_id, orthanc_study_dict in studies_with_labels.items():
                if 'AnonymizedTo' in orthanc_study_dict:
                    continue
                answer_buffer += ['$( document ).ready(function() {\n']
                answer_buffer += ['   $("#extra_%s").on(\'keyup\', function (e) {\n' % orthanc_study_id]
                answer_buffer += ['       if (e.keyCode == 13) {\n']
                answer_buffer += ['            $.post("./studies/%s/update_anonymization_queue", \n' % orthanc_study_id]
                answer_buffer += ['                   JSON.stringify({ irb_standard : $( "#label_%s" ).text(), extra : $( "#extra_%s" ).val() })\n' % (orthanc_study_id, orthanc_study_id)]
                answer_buffer += ['                  );\n']
                answer_buffer += ['       }\n']
                answer_buffer += ['   });\n']
                answer_buffer += ['});\n']

                answer_buffer += ['$( document ).ready(\n']
                answer_buffer += ['   function() {\n']
                answer_buffer += ['      $( "#select_%s" ).change(\n' % orthanc_study_id]
                answer_buffer += ['         function() {\n']
                answer_buffer += ['            $( "#label_%s" ).text(this.value);\n' % orthanc_study_id]
                answer_buffer += ['            if (this.value == "irbdefault") {\n']
                answer_buffer += ['               $( "#extra_%s" ).val(irb_label_map[this.value]);\n' % orthanc_study_id]
                answer_buffer += ['               $( "#name_base_%s" ).text("");\n' % orthanc_study_id]
                answer_buffer += ['            } else {\n']
                answer_buffer += ['               $( "#extra_%s" ).val("");\n' % orthanc_study_id]
                answer_buffer += ['               $( "#name_base_%s" ).text(irb_label_map[this.value]);\n' % orthanc_study_id]
                answer_buffer += ['            }\n']
                answer_buffer += ['            $.post("./studies/%s/update_anonymization_queue", \n' % orthanc_study_id]
                answer_buffer += ['                   JSON.stringify({ irb_standard : $( "#label_%s" ).text(), extra : $( "#extra_%s" ).val() })\n' % (orthanc_study_id, orthanc_study_id)]
                answer_buffer += ['                  );\n']
                answer_buffer += ['         }\n']
                answer_buffer += ['       );\n']
                answer_buffer += ['     }\n']
                answer_buffer += [');\n']

            answer_buffer += ['</script>\n']
            #answer_buffer += ['<script type="text/javascript">\n']
            #answer_buffer += ['</script>\n']

        answer_buffer += ['</head>\n']
        answer_buffer += ['<body>\n']
        answer_buffer += ['<a href="./app/explorer.html">Return to Orthanc home page</a></br>\n']
        answer_buffer += ['Click a column heading to sort.</br>\n']
        answer_buffer += ['<!-- targeted by the "filter_reset" option -->\n']
        answer_buffer += ['<button type="button" class="reset">Reset Search</button>\n']
        answer_buffer += ['<table class="tablesorter-blue" border=1>\n']
        answer_buffer += ['<thead>\n']
        answer_buffer += ['<tr>\n']
        answer_buffer += ['<th>IRB Label</th>\n']
        answer_buffer += ['<th>IRB Last Name</th>\n']
        answer_buffer += ['<th>Anonymization Status</th>\n']
        answer_buffer += ['<th>IRB Extra</th>\n']
        answer_buffer += ['<th>IRB Description</th>\n']
        answer_buffer += ['<th>PatientID</th>\n']
        answer_buffer += ['<th>Name</th>\n']
        answer_buffer += ['<th>Anon ID</th>\n']
        answer_buffer += ['<th>StudyDate</th>\n']
        answer_buffer += ['<th>Accession</th>\n']
        answer_buffer += ['<th>StudyDescription</th>\n']
        answer_buffer += ['<th>StudyInstanceUID</th>\n']
        answer_buffer += ['</tr>\n']
        answer_buffer += ['</thead>\n']
        answer_buffer += ['<tbody>\n']

        # Create the output table
        for orthanc_study_id, orthanc_study_dict in studies_with_labels.items():
            parameters_irb = irb_label_regex_map(orthanc_study_dict['label'])
            meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))
            orthanc_patient_id = meta_study['ParentPatient']
            study_description = meta_study['MainDicomTags']['StudyDescription'] if 'StudyDescription' in meta_study['MainDicomTags'] else '&nbsp'
            study_date = meta_study['MainDicomTags']['StudyDate'] if 'StudyDate' in meta_study['MainDicomTags'] else 'NO DATE'
            patient_name = meta_study['PatientMainDicomTags']['PatientName'] if 'PatientName' in meta_study['PatientMainDicomTags'] else '&nbsp'
            patient_id = meta_study['PatientMainDicomTags']['PatientID']
            status, internal_numbers = get_internal_numbers_by_patient_id(patient_id)
            if status['status'] != 0 and log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Error retrieving internal numbers: %d %s' % (status['status'], status['error_text']))
            accession_number = meta_study['MainDicomTags']['AccessionNumber'] if 'AccessionNumber' in meta_study['MainDicomTags'] and len(meta_study['MainDicomTags']['AccessionNumber'].strip()) > 0 else 'BLANK'
            study_instance_uid = meta_study['MainDicomTags']['StudyInstanceUID']
            answer_buffer += ['<tr>']
            answer_buffer += ['<td><span id="label_%s">%s</span></td>' % (orthanc_study_id,parameters_irb['irb_standard'])]
               
            if 'AnonymizedTo' in orthanc_study_dict:
                answer_buffer += ['<td>']
                patient_name_bases = []
                for orthanc_study_id_anon, atom_list in orthanc_study_dict['AnonymizedTo'].items():
                    for atom in atom_list:
                        if 'patient_name_base' in atom:
                            patient_name_bases += [atom['patient_name_base']]
                patient_name_bases.sort()
                patient_name_bases = list(set(patient_name_bases))
                if len(patient_name_bases) > 0:
                    answer_buffer += ['<br>'.join(patient_name_bases)]
                else:
                    answer_buffer += [parameters_irb['patient_name_base']]
                answer_buffer += ['</td>']
                answer_buffer += ['<td>complete</td>']
                if len(patient_name_bases) > 0:
                    answer_buffer += ['<td>&nbsp</td>']
                else:
                    answer_buffer += ['<td>%s</td>' % parameters_irb['extra']]
                answer_buffer += ['<td>%s</td>' % parameters_irb['description']]
            else:
                answer_buffer += ['<td><span id="name_base_%s">%s</span></td>' % (orthanc_study_id,parameters_irb['patient_name_base'])]
                answer_buffer += ['<td>queued</td>']
                answer_buffer += ['<td><input id="extra_%s" type="text" name="extra_%s", value="%s"></td>' % (orthanc_study_id,orthanc_study_id,parameters_irb['extra'])]
                answer_buffer += ['<td><select id="select_%s">' % orthanc_study_id]
                for irb_standard, irb_dict in global_var['irb_label_regex_map'].items():
                    if irb_dict['description'] == parameters_irb['description']:
                        answer_buffer += ['<option value="%s"  selected="selected">%s</option>' % (irb_standard, irb_dict['description'])]
                    else:
                        answer_buffer += ['<option value="%s">%s</option>' % (irb_standard, irb_dict['description'])]
                for irb_standard, irb_dict in {'irbdefault' : {'description' : 'Default Orthanc name base'}}.items():
                    if irb_dict['description'] == parameters_irb['description']:
                        answer_buffer += ['<option value="%s"  selected="selected">%s</option>' % (irb_standard, irb_dict['description'])]
                    else:
                        answer_buffer += ['<option value="%s">%s</option>' % (irb_standard, irb_dict['description'])]
                answer_buffer += ['</select></td>']
            answer_buffer += ['<td><a href="./app/explorer.html#patient?uuid=%s">%s</a></td>' % (orthanc_patient_id, patient_id)]
            answer_buffer += ['<td><a href="./app/explorer.html#patient?uuid=%s">%s</a></td>' % (orthanc_patient_id, patient_name)]
            orthanc_study_id_anon = None
            if 'AnonymizedTo' in orthanc_study_dict:
                for orthanc_study_id_anon_temp, anon_atoms in orthanc_study_dict['AnonymizedTo'].items():
                    if orthanc_study_id_anon_temp in orthanc_study_ids:
                        orthanc_study_id_anon = orthanc_study_id_anon_temp
                        break
            if orthanc_study_id_anon is None:
                if len(internal_numbers) > 0:
                    answer_buffer += ['<td>%s</td>' % ','.join([str(item) for item in internal_numbers])]
                else:
                    answer_buffer += ['<td>&nbsp</td>']
            else:
                if len(internal_numbers) > 0:
                    answer_buffer += ['<td><a href="./app/explorer.html#study?uuid=%s">%s</a></td>' % (orthanc_study_id_anon, ','.join([str(item) for item in internal_numbers]))]
                else:
                    answer_buffer += ['<td><a href="./app/explorer.html#study?uuid=%s">anon</a></td>' % orthanc_study_id_anon]
            answer_buffer += ['<td><span id="date_%s">%s</span></td>' % (orthanc_study_id, study_date)]
            answer_buffer += ['<td><span id="accession_%s">%s</span></td>' % (orthanc_study_id, accession_number)]
            answer_buffer += ['<td>%s</td>' % study_description]
            answer_buffer += ['<td><a href="./app/explorer.html#study?uuid=%s">%s</a></td>' % (orthanc_study_id,study_instance_uid)]
            answer_buffer += ['</tr>\n']
        answer_buffer += ['</tbody>\n']
        answer_buffer += ['</table>\n']
        if len(global_var['anonymization_queue']) > 0:
            answer_buffer += ['<button type="button" id="abl_initiate_anon">Initiate Anonymization</button>\n']
    answer_buffer += ['</body>\n']
    answer_buffer += ['</html>']

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] = log_indent_level_prev

    return ''.join(answer_buffer)

# ============================================================================
def anonymize_by_label_inherit_from_patient():
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning
    if log_message_bitflag:
        global_var['log_indent_level'] = 0
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3

    # Find patients with irb labels
    patients_with_labels = {}
    orthanc_patient_ids = json.loads(orthanc.RestApiGet('/patients'))
    for orthanc_patient_id in orthanc_patient_ids:
        labels = json.loads(orthanc.RestApiGet('/patients/%s/labels' % orthanc_patient_id))
        irb_label = None
        for label in labels:
            if global_var['irb_re'].match(label) is not None:
                irb_label = label
                break
        if irb_label is not None:
            patients_with_labels[orthanc_patient_id] = irb_label

    # Propagate labels to child studies
    for orthanc_patient_id, irb_label in patients_with_labels.items():
        meta_patient = json.loads(orthanc.RestApiGet('/patients/%s' % orthanc_patient_id))
        for orthanc_study_id in meta_patient['Studies']:
            labels = json.loads(orthanc.RestApiGet('/studies/%s/labels' % orthanc_study_id))
            if len(labels) == 0:
                orthanc.RestApiPut('/studies/%s/labels/%s' % (orthanc_study_id, irb_label), json.dumps({}))

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] = log_indent_level_prev

# ============================================================================
def anonymize_by_label_run(remote_user='None', **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        global_var['log_indent_level'] = 0
        log_indent_level_prev = 0
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)

    i_study = 0
    n_study = len(global_var['anonymization_queue'])
    for orthanc_study_id, anon_dict in global_var['anonymization_queue'].items():
        i_study += 1
        kwargs['log_message_prefix'] = 'Anonymizing study %d of %d' % (i_study, n_study)
        if log_message_bitflag:
            global_var['log_indent_level'] = 3
        set_patient_name_base('%s%s' % (anon_dict['patient_name_base'].strip(),anon_dict['extra'].strip()), **kwargs)
        status = anonymize_study_init(orthanc_study_id, flag_force_anon=True, trigger_type='anonbylabel', remote_user=remote_user, **kwargs)
        reset_patient_name_base()
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
                return status

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev
    
    return {'status' : 0}

# ============================================================================
def anonymization_history_get(orthanc_study_id):
# ----------------------------------------------------------------------------

    meta_list = json.loads(orthanc.RestApiGet('/studies/%s/metadata' % orthanc_study_id))
    if 'AnonymizationHistory' in meta_list:
        try:
            anonymization_history = json.loads(orthanc.RestApiGet('/studies/%s/metadata/AnonymizationHistory' % orthanc_study_id))
            if anonymization_history is None:
                anonymization_history = {}
        except:
            anonymization_history = {}
    else:
        anonymization_history = {}

    return anonymization_history

 # ============================================================================
def anonymization_history_modify(anonymization_history={}, type_insert=None, orthanc_study_id=None, atom=None, store_in=None):
# ----------------------------------------------------------------------------
    if type_insert is not None:
        if type_insert not in anonymization_history:
            anonymization_history[type_insert] = {}
        if orthanc_study_id is not None:
            if orthanc_study_id not in anonymization_history[type_insert]:
                anonymization_history[type_insert][orthanc_study_id] = []
            if atom is not None:
                anonymization_history[type_insert][orthanc_study_id] += [atom]

    if store_in is not None:
        response_store = orthanc.RestApiPut('/studies/%s/metadata/AnonymizationHistory' % store_in, json.dumps(anonymization_history))

    return anonymization_history

# ============================================================================
def anonymization_history_atom_modify(atom = None, status=None, error_text=None, make_date_time=None, trigger_type=None, remote_user=None, patient_name_base=None):
# ----------------------------------------------------------------------------

    if atom is None:
        atom = {}
    if status is not None:
        atom['status'] = status
    if error_text is not None:
        atom['error_text'] = error_text
    if trigger_type is not None:
        atom['trigger_type'] = trigger_type
    if remote_user is not None:
        atom['remote_user'] = remote_user
    if make_date_time is not None:
        atom[make_date_time] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if patient_name_base is not None:
        atom['patient_name_base'] = patient_name_base

    return atom

# ============================================================================
def anonymize_instances_at_level(anon_at_level, orthanc_level_id, flag_first_call,
                                 sql_pid, patient_id_anon, 
                                 sql_siuid, study_instance_uid_anon,
                                 patient_id_modifier='', **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    flag_anon_at_study_level = anon_at_level.find('Study') >= 0

    # Load tag keep/remove info
    status, tag_handling, tag_handling_list = base_tag_handling(**kwargs)
    if status['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status, None, None, None
 
    # Capture all UID values for all instances and collect keep/remove data
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Capturing UID for all instances', **kwargs)
        global_var['log_indent_level'] += 3
    tags_encountered = {}
    tags_to_keep = {}
    tags_to_remove = {}
    if flag_first_call:
        global_var['top_level_tag_to_keep'] = {}
        global_var['kept_uid'] = {}
    recurse_proprietary = {}
    recurse_remove = {}
    recurse_group_keep = {}
    recurse_group_removere = {}
    if flag_anon_at_study_level:
        meta_instances = json.loads(orthanc.RestApiGet('/studies/%s/instances' % orthanc_level_id))
        recurse_proprietary = scan_study_for_group_element(orthanc_level_id, recurse_proprietary, type_match='gggg-odd')
        recurse_remove = scan_study_for_group_element(orthanc_level_id, recurse_remove, type_match='gggg-eeee', match_list = tag_handling_list['remove'])
        if 'groupkeep' in tag_handling:
            recurse_group_keep = scan_study_for_group_element(orthanc_level_id, recurse_group_keep, type_match='gggg', match_list=tag_handling_list['groupkeep'])
        if 'groupremovere' in tag_handling:
            recurse_group_removere = scan_study_for_group_element(orthanc_level_id, recurse_group_removere, type_match='gggg-regexp', match_list=tag_handling_list['groupremovere'])
    else:
        meta_instances = json.loads(orthanc.RestApiGet('/series/%s/instances' % orthanc_level_id))
        recurse_proprietary = scan_series_for_group_element(orthanc_level_id, recurse_proprietary, type_match='gggg-odd')
        recurse_remove = scan_series_for_group_element(orthanc_level_id, recurse_remove, type_match='gggg-eeee', match_list = tag_handling_list['remove'])
        if 'groupkeep' in tag_handling:
            recurse_group_keep = scan_series_for_group_element(orthanc_level_id, recurse_group_keep, type_match='gggg', match_list=tag_handling_list['groupkeep'])
        if 'groupremovere' in tag_handling:
            recurse_group_removere = scan_series_for_group_element(orthanc_level_id, recurse_group_removere, type_match='gggg-regexp', match_list=tag_handling_list['groupremovere'])
    
    # Study the tags to determine keep/remove/replace
    i_instance = 0
    n_instance = len(meta_instances)
    m_instance = max(n_instance // 10,5)
    for meta_instance in meta_instances:
        i_instance += 1
        if log_message_bitflag and (i_instance % m_instance == 0):
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Scanning instances %d of %d' % (i_instance, n_instance), **kwargs)
        orthanc_instance_id = meta_instance['ID']
        tags_instance = json.loads(orthanc.RestApiGet('/instances/%s/tags' % orthanc_instance_id))
        try:
            level_out, kept_uid, top_level_tag_to_keep, parent_key = recursive_find_uid_to_keep(tags_instance)
        except:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status' : 1, 'error_text' : 'Problem recursing instance tags'}, None, None, None
        for kk, vv in top_level_tag_to_keep.items():
            global_var['top_level_tag_to_keep'][kk] = vv
        for kk, vv in kept_uid.items():
            global_var['kept_uid'][kk] = vv
        for tag_key, tag_val in tags_instance.items():
            address_group_element = tag_key.replace(',','-')
            tags_encountered[address_group_element] = True
        if 'groupkeep' in tag_handling:
            for tag_key, tag_val in tags_instance.items():
                address_group, address_element = tag_key.split(',')
                if address_group in tag_handling['groupkeep']:
                    address_group_element = tag_key.replace(',','-')
                    tags_to_keep[address_group_element] = True
            for address_group_element, tag_list in recurse_group_keep.items():
                tags_to_keep[address_group_element] = True
        if 'groupremovere' in tag_handling:
            for tag_key, tag_val in tags_instance.items():
                address_group, address_element = tag_key.split(',')
                for address_groupre, value in tag_handling['groupremovere'].items():
                    if address_group.find(address_groupre) >= 0:
                        address_group_element = tag_key.replace(',','-')
                        tags_to_remove[address_group_element] = True
            for address_group_element, value_list in recurse_group_removere.items():
                tags_to_remove[address_group_element] = True
    
    # Remove any private tags not already explicity kept
    if 'KeepSomePrivate' in tag_handling:
        for meta_instance in meta_instances:
            orthanc_instance_id = meta_instance['ID']
            tags_instance = json.loads(orthanc.RestApiGet('/instances/%s/tags' % orthanc_instance_id))
            for tag_key, tag_val in tags_instance.items():
                address_group, address_element = tag_key.split(',')
                if int(address_group,16) % 2 == 1:
                    address_group_element = tag_key.replace(',','-')
                    if not (address_group_element in tag_handling['keep'] or 
                            address_group_element in tags_to_keep):
                        tags_to_remove[address_group_element] = True
        for address_group_element, value_prop in recurse_proprietary.items():
            if not (address_group_element in tag_handling['keep'] or 
                    address_group_element in tags_to_keep):
                tags_to_remove[address_group_element] = True
    else:
        for address_group_element, value_prop in recurse_proprietary.items():
            tags_to_remove[address_group_element] = True

    if log_message_bitflag:
        global_var['log_indent_level'] -= 3
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time so far (1) in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)

    # Find the internal number if it exists
    status, internal_number = get_internal_number(int(sql_pid), patient_id_modifier, **kwargs)
    if status['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], status['error_text'], **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 2, 'error_text' : json.dumps(status)}, None, None, None

    # Construct the patient name
    patient_name_anon = construct_patient_name(internal_number, **kwargs)

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time so far (2) in %s: %d ' % (frame.f_code.co_name, time.time()-time_0), **kwargs)

    # Tags to be replaced
    tag_replace = {}
    tag_replace['PatientName'] = patient_name_anon
    if patient_id_anon is not None:
        tag_replace['PatientID'] = patient_id_anon
    if study_instance_uid_anon is not None:
        tag_replace['StudyInstanceUID'] = study_instance_uid_anon
    if 'empty' in tag_handling:
        for address_group_element, value in tag_handling['empty'].items():
            tag_replace[address_group_element] = ''
    if 'emptyseq' in tag_handling:
        for address_group_element, value in tag_handling['emptyseq'].items():
            tag_replace[address_group_element] = []
    if 'emptyx' in tag_handling:
        for address_group_element, value in tag_handling['emptyx'].items():
            tag_replace[address_group_element] = 'xxxxxx'

    # Top level tags to remove
    tag_remove = []
    for address_element, value_list in recurse_remove.items():
        for value in value_list:
            if value not in tag_remove:
                tag_remove += [value]
    for address_element, value in tags_to_remove.items():
        if address_element not in tag_handling['remove']:
            if address_element not in tag_remove:
                tag_remove += [address_element]
        if address_element in recurse_proprietary:
            for value in recurse_proprietary[address_element]:
                if value not in tag_remove:
                    tag_remove += [value]
        if 'groupremovere' in tag_handling and \
            address_element in recurse_group_removere:
            for value in recurse_group_removere[address_element]:
                if value not in tag_remove:
                    tag_remove += [value]

    # Top level tags to keep
    tag_keep = []
    for address_element, value in tag_handling['keep'].items():
        if address_element in tags_encountered and address_element not in tag_keep:
            tag_keep += [address_element]
    for address_element, flag_keep in tags_to_keep.items():
        if address_element not in tag_handling['keep'] and address_element not in tag_keep:
            tag_keep += [address_element]
    for tag_key, tag_val in global_var['top_level_tag_to_keep'].items():
        if tag_key.find('Unknown') < 0 and tag_key not in tag_keep:
            tag_keep += [tag_key]

    # Modify the study: It seems remove clashes with keep and I need to run them separate
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Starting the study modification call', **kwargs)
    modify_post_data = {}
    modify_post_data['Remove'] = tag_remove
    flag_remove_private_tags = os.getenv('PYTHON_FLAG_REMOVE_PRIVATE_TAGS', default='true') == 'true'
    if flag_remove_private_tags and not tag_handling['KeepSomePrivate']:
        modify_post_data['RemovePrivateTags'] = flag_remove_private_tags
    modify_post_data['Force'] = True
    modify_post_data['DicomVersion'] = '2008'
    if flag_anon_at_study_level:
        try:
            meta_study_mod = json.loads(orthanc.RestApiPost('/studies/%s/modify' % orthanc_level_id,
                                        json.dumps(modify_post_data)))
        except:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status' : 3, 'error_text' : json.dumps(modify_post_data,indent=3)}, None, None, None
        orthanc_study_id_mod = meta_study_mod['ID']
    else:
        try:
            meta_series_mod = json.loads(orthanc.RestApiPost('/series/%s/modify' % orthanc_level_id,
                                         json.dumps(modify_post_data)))
        except:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status' : 4, 'error_text' : json.dumps(modify_post_data,indent=3)}, None, None, None
        orthanc_series_id_mod = meta_series_mod['ID']
        meta_series_mod_full = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id_mod))
        orthanc_study_id_mod = meta_series_mod_full['ParentStudy']
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time so far (3) in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)

    # Anonymize the study
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Starting the study anonymization call', **kwargs)
    post_data_anon = {}
    if len(tag_replace) > 0:
        post_data_anon['Replace'] = tag_replace
    post_data_anon['Keep'] = tag_keep
    post_data_anon['Force'] = True
    post_data_anon['DicomVersion'] = '2008'
    if flag_anon_at_study_level:
        try:
            response_study_anon = orthanc.RestApiPost('/studies/%s/anonymize' % orthanc_study_id_mod, 
                                                      json.dumps(post_data_anon))
        except:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 5, 'error_text' : 'Problem calling anonymize study'}, None, None, None
        meta_study_anon = json.loads(response_study_anon)
        orthanc_study_id_anon = meta_study_anon['ID']
        meta_instances_anon = json.loads(orthanc.RestApiGet('/studies/%s/instances' % orthanc_study_id_anon))
    else:
        try:
            response_series_anon = orthanc.RestApiPost('/series/%s/anonymize' % orthanc_series_id_mod, 
                                                       json.dumps(post_data_anon))
        except:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 6, 'error_text' : 'Problem calling anonymize series'}, None, None, None
        meta_series_anon = json.loads(response_series_anon)
        orthanc_series_id_anon = meta_series_anon['ID']
        meta_series_anon = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id_anon))
        orthanc_study_id_anon = meta_series_anon['ParentStudy']
        meta_instances_anon = json.loads(orthanc.RestApiGet('/series/%s/instances' % meta_series_anon['ID']))
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'N instances anon: %d' % len(meta_instances_anon), **kwargs)
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time so far (4) in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)

    meta_study_anon = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_anon))
    if patient_id_anon is None:
        status = save_patient_ids_anon_to_db(sql_pid, orthanc_study_id=meta_study_anon['ID'],**kwargs)
        if status['status'] > 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None
    if study_instance_uid_anon is None:
        status = save_study_instance_uid_anon_to_db(meta_study_anon['ID'], sql_siuid, **kwargs)
        if status['status'] > 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None
    flag_save_patient_name_anon = os.getenv('PYTHON_FLAG_SAVE_PATIENTNAME_ANON',default='true') == 'true'
    if flag_save_patient_name_anon:
        status = save_patient_name_anon_to_db(patient_name_anon, sql_siuid, **kwargs)
        if status['status'] > 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev
    if flag_save_patient_name_anon:
        return {'status' : 0}, meta_instances_anon, orthanc_study_id_anon, patient_name_anon
    else:
        return {'status' : 0}, meta_instances_anon, orthanc_study_id_anon, None

# ============================================================================
def anonymize_study(orthanc_study_id_parent, trigger_type, remote_user, **kwargs):
    """
    PURPOSE:  Main function for processing the anonymization.
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Anonymizing %s' % orthanc_study_id_parent, **kwargs)
    if log_message_bitflag and global_var['flag_force_anon']:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Forcing anonymization', **kwargs)
    meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_parent))
    anonymization_history = anonymization_history_get(orthanc_study_id_parent)
    flag_images_sent = False
    orthanc_study_id_anon = 'Aborted'
    anonymization_history_atom = anonymization_history_atom_modify(make_date_time='initiated', 
                                                                   trigger_type=trigger_type, 
                                                                   remote_user=remote_user, 
                                                                   patient_name_base=get_patient_name_base(**kwargs))

    #  Filter by original/primary and other status
    flag_prescreen_send_to_remote = os.getenv('PYTHON_FLAG_PRESCREEN_ORIGINAL_PRIMARY', default='true') == 'true'
    if flag_prescreen_send_to_remote:
        counts, flag_deleted = filter_and_delete_instances(orthanc_study_id_parent, **kwargs)
        n_series_start = counts['series']['start']
        n_series_deleted = counts['series']['deleted']
        if flag_deleted:
            meta_study = None
            for orthanc_study_id_other in json.loads(orthanc.RestApiGet('/studies')):
                if orthanc_study_id_other == orthanc_study_id_parent:
                    meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_parent))
        if meta_study is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'All series deleted by prefilter. Aborting anonymization.', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Deleted by op prefilter')
            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
            return {'status' : 0}

    # Filter by modality
    flag_prescreen_by_modality = os.getenv('PYTHON_FLAG_PRESCREEN_BY_MODALITY', default='true') == 'true'
    if flag_prescreen_by_modality:
        # flag_deleted, n_series_start, n_series_deleted = PreScreenSeriesByModality(orthanc_study_id_parent)
        counts, flag_deleted = filter_and_delete_series_by_modality(orthanc_study_id_parent, **kwargs)
        #flag_deleted = lResults['FlagDeleted']
        n_series_start = counts['start']
        n_series_deleted = counts['deleted']
        if flag_deleted:
            meta_study = None
            for orthanc_study_id_other in json.loads(orthanc.RestApiGet('/studies')):
                if (orthanc_study_id_other == orthanc_study_id_parent):
                    meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_parent))
        if meta_study is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'All series deleted by modality. Aborting anonymization.', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Deleted by mod prefilter')
            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
            return {'status' : 0}

    flag_anonymize_by_series = os.getenv('PYTHON_FLAG_ANON_BY_SERIES', default='false') == 'true'
    if flag_anonymize_by_series:
        flag_split_2d_from_cview_tomo = os.getenv('PYTHON_FLAG_SPLIT_2D_FROM_CVIEW_TOMO', default='false') == 'true'
        if flag_split_2d_from_cview_tomo:
            flag_complete = check_split_2d_from_cview_tomo(orthanc_study_id_parent)
            if not flag_complete:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Incomplete set of 2d or tomo. Aborting.', **kwargs)
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Incomplete 2d or tomo')
                anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
                return {'status' : 0}

        status = anonymize_study_by_series(orthanc_study_id_parent, anonymization_history, anonymization_history_atom, meta_study=meta_study, trigger_type=trigger_type, remote_user=remote_user, **kwargs)
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem anonymizing by series. Aborting.', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Problem anonymizing by series')
            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
            return status
        
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 0}

    # We modify the incoming patientIDs based on descriptions
    # If "screen" appears in the description, the modifier is 's' else 'd' for diagnostic
    # This has the effect of generating possibly to anonymous subjects for each incoming subject
    # Comment out the call to the routine if you want normal use of PatientIDs
    patient_id_modifier = ''
    flag_split_screen_from_diagnostic = os.getenv('PYTHON_FLAG_SPLIT_SCREEN_DIAG', default='true') == 'true'
    if flag_split_screen_from_diagnostic:
        patient_id_modifier = set_screen_or_diagnostic(orthanc_study_id_parent, **kwargs)
    flag_every_accession_a_patient = os.getenv('PYTHON_FLAG_EVERY_ACCESSION_A_PATIENT', default='false') == 'true'
    if flag_every_accession_a_patient:
        patient_id_modifier = '_%s' % str(meta_study['MainDicomTags']['AccessionNumber']) if 'AccessionNumber' in meta_study['MainDicomTags'] else 'other'

    # Check to see if this subject was previously anonymized
    # StudyInstanceUID is only modified when anonymizing at the series level
    study_instance_uid_modifier = ''
    status, flag_new_patient_id, sql_pid, patient_id_anon = \
        save_patient_ids_to_db(orthanc_study_id=orthanc_study_id_parent, patient_id_modifier=patient_id_modifier, **kwargs)
        #save_patient_ids_to_db(orthanc_study_id=orthanc_study_id_parent, patient_id_modifier=patient_id_modifier)
    if status['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem saving patient ids to db. Aborting.', **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
        return status
    status, flag_new_study_instance_uid, sql_siuid, study_instance_uid_anon = \
        save_study_instance_uid_to_db(orthanc_study_id_parent, sql_pid, study_instance_uid_modifier=study_instance_uid_modifier, **kwargs)
    if status['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem saving study uid to db. Aborting.', **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
        return status

    # We're not going to bother anonymizing unless either a new patient or study
    flag_non_original_detected = False
    flag_force_anon = global_var['flag_force_anon']
    if flag_force_anon or (flag_new_patient_id or flag_new_study_instance_uid):

        # First pass anonymization
        flag_first_call = True
        status, meta_instances_anon, orthanc_study_id_anon, patient_name_anon = \
            anonymize_instances_at_level('Study', orthanc_study_id_parent, flag_first_call,
                                sql_pid, patient_id_anon, sql_siuid, study_instance_uid_anon,
                                patient_id_modifier, **kwargs)
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem anonymizing instances. Aborting.', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
            return status

        # Update the parent history
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating child anonymization history.', **kwargs)
        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, make_date_time='completed')
            
        # Set up old-->new UID map
        flag_remap_sop_instance_uid = True
        flag_remap_kept_uid = True
        uid_map, uid_type = map_uid_old_to_new(orthanc_study_id_anon, flag_remap_sop_instance_uid, flag_remap_kept_uid, **kwargs)
        global_var['uid_map'] = uid_map

        # Set up replacements for AccessionNumber and StudyID
        replace_root = {}
        replace_root['AccessionNumber'] = orthanc_study_id_anon[0:8] + orthanc_study_id_anon[9:17]
        replace_root['StudyID'] = orthanc_study_id_anon[18:26] + orthanc_study_id_anon[27:35]
    
        # Check for existing lShiftEpoch
        status, shift_epoch = load_shift_epoch_from_db(sql_pid, **kwargs)
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem loading shift epoch. Aborting.', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
            return status
        
        # Compute lShiftEpoch
        flag_keep_original_dates = os.getenv('PYTHON_FLAG_KEEP_ORIGINAL_DATES', default='false') == 'true'
        if shift_epoch is None:
            # Compute random shift up to one year
            random.seed()
            max_date_shift_in_years = float(os.getenv('PYTHON_MAX_DATE_SHIFT_IN_YEARS', default=1.0))
            shift_epoch = random.randint(0,int(max_date_shift_in_years*365*24*3600))
            flag_save_shift_epoch = True
            status = save_shift_epoch_to_db(sql_pid, shift_epoch, **kwargs)
            if status['status'] != 0:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem saving shift epoch. Aborting.', **kwargs)
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
                anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
                return status

        # For some cases, we keep the dates, so shift_epoch=0
        if flag_keep_original_dates:
            shift_epoch = 0

        # Second pass anonymization creates files modified by shift_epoch
        # Deletes First pass anonymized files following shift_epoch modification
        status, orthanc_instances_id_new = shift_date_time_patage_of_instances(meta_instances_anon, shift_epoch, replace_root, **kwargs)
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem shifting times. Aborting.', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
            return status
    
        # Delete the original instance
        for meta_instance_anon in meta_instances_anon:
            orthanc_instance_id = meta_instance_anon['ID']
            orthanc.RestApiDelete('/instances/%s' % orthanc_instance_id)

        # Set up the child history       
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating child anonymization history.', **kwargs)
        anonymization_history_anon = anonymization_history_get(orthanc_study_id_anon)
        anonymization_history_atom_anon = anonymization_history_atom_modify(None, 0, 'Success', make_date_time='completed', trigger_type=trigger_type, remote_user=remote_user)
        anonymization_history_anon = anonymization_history_modify(anonymization_history_anon, 'AnonymizedFrom', orthanc_study_id_parent, anonymization_history_atom_anon, orthanc_study_id_anon)
    
        # Send to receiving modality
        flag_by_instance = filter_what_instances_to_keep(orthanc_instance_ids=orthanc_instances_id_new, **kwargs)
        n_to_send = len(flag_by_instance)
        ten_percent_to_send = n_to_send // 10
        i_to_send = 0
        for orthanc_instance_id, flag_send_to_remote in flag_by_instance.items():
            if flag_send_to_remote:
                if not flag_force_anon:
                    if not flag_images_sent and log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Sending to remote.', **kwargs)
                    if (i_to_send % 10) == 0 and log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level']+3,'Sending %d of %d' % (i_to_send+1, n_to_send), **kwargs)
                i_try = 0
                flag_images_sent = False
                while i_try < 5 and not flag_images_sent:
                    try:
                       # orthanc.RestApiPost('/modalities/%s/store' % os.getenv('PYTHON_ANON_ORTHANC'), orthanc_instance_id)
                        flag_images_sent = True
                    except:
                        i_try += 1
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Failed sending image on attempt %d' % i_try, **kwargs)
                        time.sleep(5)
            else:
                orthanc.RestApiDelete('/instances/%s' % orthanc_instance_id)
                flag_non_original_detected = True
            i_to_send += 1

        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating lookup table', **kwargs)

        status = update_lookup_html(**kwargs)
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem updating lookup table.', **kwargs)

        if patient_name_anon is not None:
            status = auto_email(os.getenv('ORTHANC__NAME') + ' Anon Complete', 'Anonymization complete:' + patient_name_anon, **kwargs)
        else:
            status = auto_email(os.getenv('ORTHANC__NAME') + ' Anon Complete', 'Anonymization complete.', **kwargs)
        if status['status'] != 0:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem sending emails..', **kwargs)

    else: # existing patient/study combo

        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Skipping re-anon of existing patient/study', **kwargs)
        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Skipping re-anon of existing patient/study', make_date_time='completed')
        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)
        return {'status' : 0}

    if flag_non_original_detected:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Some non-original images were not sent', **kwargs)

    if flag_images_sent and log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Images sent to remote modalities', **kwargs)

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Success')
    anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id_parent)

    return {'status' : 0}

# ============================================================================
def anonymize_study_by_series(orthanc_study_id, anonymization_history, anonymization_history_atom, meta_study = None, trigger_type='unknown', remote_user='None', **kwargs):
# Assume we've already pre-screened for modality
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    if meta_study is None:
        meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))

    # Get the Orthanc series ID associated with this study
    patient_id_modifier_by_series = {}
    sql_pid_by_series = {}
    patient_id_anon_by_series = {}
    sql_siuid_by_series = {}
    study_instance_uid_anon_by_series = {}
    flag_new_patient_id_by_series = {}
    flag_new_study_instance_uid_by_series = {}
    for orthanc_series_id in meta_study['Series']:

        # Get series meta
        meta_series = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id))

        # We modify the incoming patientIDs based on descriptions
        # Currently, we modify by 2D vs non-2D
        patient_id_modifier = ''
        flag_split_2d_from_cview_tomo = os.getenv('PYTHON_FLAG_SPLIT_2D_FROM_CVIEW_TOMO', default='false') == 'true'
        if flag_split_2d_from_cview_tomo:
            patient_id_modifier = set_2d_or_cview_tomo(orthanc_series_id)

        flag_every_accession_a_patient = os.getenv('PYTHON_FLAG_EVERY_ACCESSION_A_PATIENT', default='false') == 'true'
        if flag_every_accession_a_patient:
            patient_id_modifier = '_%s' % meta_study['MainDicomTags']['AccessionNumber']
        patient_id_modifier_by_series[orthanc_series_id] = patient_id_modifier

        # Check to see if this subject was previously anonymized
        # StudyInstanceUID is only modified when anonymizing at the series level
        study_instance_uid_modifier = patient_id_modifier
        status, flag_new_patient_id, sql_pid, patient_id_anon = save_patient_ids_to_db(orthanc_study_id=meta_study['ID'],
                                                                                       patient_id_modifier=patient_id_modifier, **kwargs)
        #status, flag_new_patient_id, sql_pid, patient_id_anon = save_patient_ids_to_db(orthanc_study_id=meta_study['ID'],
        #                                                                               patient_id_modifier=patient_id_modifier)
        if status['status'] != 0:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Error saving patient ids: %s' % status['error_text'], **kwargs)
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status

        status, flag_new_study_instance_uid, sql_siuid, study_instance_uid = \
            save_study_instance_uid_to_db(orthanc_study_id, sql_pid, study_instance_uid_modifier=study_instance_uid_modifier, **kwargs)

        if status['status'] != 0:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Error saving study iuid: %s' % status['error_text'], **kwargs)
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status
        
        flag_new_patient_id_by_series[orthanc_series_id] = flag_new_patient_id
        sql_pid_by_series[orthanc_series_id] = sql_pid
        patient_id_anon_by_series[orthanc_series_id] = patient_id_anon
        flag_new_study_instance_uid_by_series[orthanc_series_id] = flag_new_study_instance_uid
        sql_siuid_by_series[orthanc_series_id] = sql_siuid
        study_instance_uid_anon_by_series[orthanc_series_id] = study_instance_uid

    # Compute unique set of identifiers
    patient_id_modifier_unique = {}
    flag_new_patient_id = {}
    flag_new_study_instance_uid = {}
    sql_pid = {}
    patient_id_anon = {}
    sql_siuid = {}
    study_instance_uid = {}
    for orthanc_series_id,patient_id_modifier in patient_id_modifier_by_series.items():
        if patient_id_modifier not in patient_id_modifier_unique:
            patient_id_modifier_unique[patient_id_modifier] = [orthanc_series_id]
            flag_new_patient_id[patient_id_modifier] = flag_new_patient_id_by_series[orthanc_series_id]
            flag_new_study_instance_uid[patient_id_modifier] = flag_new_study_instance_uid_by_series[orthanc_series_id]
            sql_pid[patient_id_modifier] = sql_pid_by_series[orthanc_series_id]
            patient_id_anon[patient_id_modifier] = patient_id_anon_by_series[orthanc_series_id]
            sql_siuid[patient_id_modifier] = sql_siuid_by_series[orthanc_series_id]
            study_instance_uid[patient_id_modifier] = study_instance_uid_anon_by_series[orthanc_series_id]
        else:
            patient_id_modifier_unique[patient_id_modifier] += [orthanc_series_id]
            flag_new_patient_id[patient_id_modifier] = flag_new_patient_id[patient_id_modifier] or flag_new_patient_id_by_series[orthanc_series_id]
            flag_new_study_instance_uid[patient_id_modifier] = flag_new_study_instance_uid[patient_id_modifier] or flag_new_study_instance_uid_by_series[orthanc_series_id]
            if sql_pid[patient_id_modifier] != sql_pid_by_series[orthanc_series_id]:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status' : 1, 'error_text' : 'Mismatch in SQLpid assigned to series with same patient modifier'}

            if patient_id_anon[patient_id_modifier] != patient_id_anon_by_series[orthanc_series_id]:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status' : 1, 'error_text' : 'Mismatch in dPatientIDAnon assigned to series with same patient modifier'}

            if sql_siuid[patient_id_modifier] != sql_siuid_by_series[orthanc_series_id]:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status' : 1, 'error_text' : 'Mismatch in SQLsiuid assigned to series with same patient modifier'}

            if study_instance_uid[patient_id_modifier] != study_instance_uid_anon_by_series[orthanc_series_id]:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status' : 1, 'error_text' : 'Mismatch in dStudyInstanceUIDAnon assigned to series with same patient modifier'}

    # Now loop over sets of series by their modifier
    flag_images_sent = False
    for patient_id_modifier, orthanc_series_ids in patient_id_modifier_unique.items():

        # We're not going to bother anonymizing unless either a new patient or study
        flag_non_original_detected = False
        flag_force_anon = False or global_var['flag_force_anon']
        patient_name_anon_dict = {}
        if flag_force_anon or (flag_new_patient_id[patient_id_modifier] or flag_new_study_instance_uid[patient_id_modifier]):

            # First pass anonymization
            flag_first_call = True
            for orthanc_series_id in orthanc_series_ids:
                
                status, meta_instances_anon_temp, orthanc_study_id_anon_temp, patient_name_anon_temp = \
                    anonymize_instances_at_level('Series', orthanc_series_id, flag_first_call,
                                        sql_pid[patient_id_modifier], patient_id_anon[patient_id_modifier],
                                        sql_siuid[patient_id_modifier], study_instance_uid[patient_id_modifier],
                                        patient_id_modifier, **kwargs)
                if status['status'] != 0:
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                        global_var['log_indent_level'] = log_indent_level_prev
                    return status

                if patient_name_anon_temp is not None:
                    patient_name_anon_dict[patient_name_anon_temp] = True

                # Update the parent history
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating child anonymization history.', **kwargs)
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, make_date_time='completed')

                if flag_first_call:
                    meta_instances_anon = meta_instances_anon_temp
                    orthanc_study_id_anon = orthanc_study_id_anon_temp
                    # We call "Save" again just to read in the newly saved IDs (they were saved inside the anonymize routine)
                    study_instance_uid_modifier = patient_id_modifier

                    status, flag_new_patient_id_temp, sql_pid_temp, patient_id_anon_temp = save_patient_ids_to_db(orthanc_study_id=meta_study['ID'],
                                                                                                                  patient_id_modifier=patient_id_modifier, **kwargs)
                    #status, flag_new_patient_id_temp, sql_pid_temp, patient_id_anon_temp = save_patient_ids_to_db(orthanc_study_id=meta_study['ID'],
                    #                                                                                              patient_id_modifier=patient_id_modifier)
                    if status['status'] != 0:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Error saving patient ids: %s' % status['error_text'], **kwargs)
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                            global_var['log_indent_level'] = log_indent_level_prev
                        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
                        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                        return status

                    if sql_pid[patient_id_modifier] != sql_pid_temp:
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                            global_var['log_indent_level'] = log_indent_level_prev
                        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=1, error_text = 'Mismatch reading sqlpid')
                        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                        return {'status' : 1, 'error_text' : 'Unexpected mismatch when reading SQLpid'}

                    if patient_id_modifier not in patient_id_anon:
                        patient_id_anon[patient_id_modifier] = patient_id_anon_temp
                    else:
                        if flag_new_patient_id_temp or (patient_id_anon[patient_id_modifier] != patient_id_anon_temp):
                            if log_message_bitflag:
                                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                                global_var['log_indent_level'] = log_indent_level_prev
                            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=1, error_text = 'Mismatch reading patientidanon')
                            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                            return {'status' : 1, 'error_text' : 'Unexpected mismatch when reading dPatientIDAnon'}

                    status, flag_new_study_instance_uid_temp, sql_siuid_temp, study_instance_uid_temp = \
                        save_study_instance_uid_to_db(meta_study['ID'], sql_pid_temp, study_instance_uid_modifier=study_instance_uid_modifier, **kwargs)
            
                    if status['status'] != 0:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Error saving study iuid: %s' % status['error_text'], **kwargs)
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                            global_var['log_indent_level'] = log_indent_level_prev
                        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
                        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                        return status

                    if sql_siuid[patient_id_modifier] != sql_siuid_temp:
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                            global_var['log_indent_level'] = log_indent_level_prev
                        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=1, error_text = 'Unexpected mismatch when reading sqlsiuid')
                        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                        return {'status' : 1, 'error_text' : 'Unexpected mismatch when reading SQLsiuid'}

                    if patient_id_modifier not in study_instance_uid:
                        study_instance_uid[patient_id_modifier] = study_instance_uid_temp
                    else:
                        if flag_new_study_instance_uid_temp or (study_instance_uid[patient_id_modifier] != study_instance_uid_temp):
                            if log_message_bitflag:
                                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                                global_var['log_indent_level'] = log_indent_level_prev
                            anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=1, error_text = 'Unexpected mismatch when reading studyinstanceuidanon')
                            anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                            return {'status' : 1, 'error_text' : 'Unexpected mismatch when reading dStudyInstanceUIDAnon'}

                else:
                    # Add instances to list of instances already anonymized
                    meta_instances_anon += meta_instances_anon_temp

                    # StudyIDAnon should not have changed
                    if orthanc_study_id_anon != orthanc_study_id_anon_temp:
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                            global_var['log_indent_level'] = log_indent_level_prev
                        anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=1, error_text = 'Unexpected change in idanon for same modifier')
                        anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                        return {'status' : 1, 'error_text' : 'Unexpected change in IDAnon for same modifier'}

                flag_first_call = False
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text = 'Success')
            
            # Set up old-->new UID map
            flag_remap_sop_instance_uid = True
            flag_remap_kept_uid = True
            uid_map, uid_type = map_uid_old_to_new(orthanc_study_id_anon, flag_remap_sop_instance_uid, flag_remap_kept_uid, **kwargs)

            # Set up replacements for AccessionNumber and StudyID
            replace_root = {}
            replace_root['AccessionNumber'] = string.sub(orthanc_study_id_anon,1,8) + string.sub(orthanc_study_id_anon,10,17)
            replace_root['StudyID'] = string.sub(orthanc_study_id_anon,19,26) + string.sub(orthanc_study_id_anon,28,35)
    
            # Check for existing shift_epoch
            status, shift_epoch = load_shift_epoch_from_db(sql_pid[patient_id_modifier], **kwargs)
            if status['status'] != 0:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
                anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                return status
            
            # ------------------------------------------------
            # Compute shift_epoch
            flag_save_shift_epoch = False
            if shift_epoch is None:
                # Compute random shift up to one year
                random.seed()
                max_date_shift_in_years = float(os.getenv('PYTHON_MAX_DATE_SHIFT_IN_YEARS', default=1.0))
                shift_epoch = random.randint(0,int(max_date_shift_in_years*365*24*3600))
                flag_save_shift_epoch = True

            # For some cases, we keep the dates, so shift_epoch=0
            flag_keep_original_dates = os.getenv('PYTHON_FLAG_KEEP_ORIGINAL_DATES', default='false') == 'true'
            if flag_keep_original_dates:
                shift_epoch = 0

            if flag_save_shift_epoch:
                status = save_shift_epoch_to_db(sql_pid[patient_id_modifier], shift_epoch, **kwargs)
                if status['status'] != 0:
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                        global_var['log_indent_level'] = log_indent_level_prev
                    anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
                    anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                    return status

            # ------------------------------------------------
            # Second pass anonymization creates files modified by shift_epoch
            # Deletes First pass anonymized files following shift_epoch modification
            status, orthanc_instance_ids_new = shift_date_time_patage_of_instances(meta_instances_anon, shift_epoch, replace_root, **kwargs)
            if status['status'] != 0:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=status['status'], error_text = status['error_text'])
                anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                return status

            # Delete the original instance
            for meta_instance_anon in meta_instances_anon:
                orthanc_instance_id = (meta_instance_anon['ID'])
                orthanc.RestApiDelete('/instances/%s' % orthanc_instance_id)
    
            # Set up the child history       
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating child anonymization history.', **kwargs)
            anonymization_history_anon = anonymization_history_get(orthanc_study_id_anon)
            anonymization_history_atom_from = anonymization_history_atom_modify(None, status=0, error_text='Success', make_date_time='completed', trigger_type=trigger_type, remote_user=remote_user)
            anonymization_history_anon = anonymization_history_modify(anonymization_history_anon, 'AnonymizedFrom', orthanc_study_id, anonymization_history_atom_from, orthanc_study_id_anon)

            # Send to receiving modality
            flag_by_instance = filter_what_instances_to_keep(orthanc_instance_ids=orthanc_instance_ids_new, **kwargs)
            if flag_by_instance is None:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=1, error_text = 'Problem calling send instances to remote filter')
                anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon_temp, anonymization_history_atom, orthanc_study_id)
                return {'status' : 1, 'error_text' : 'Problem calling send_instances_to_remote_filter'}
            n_to_send = len(flag_by_instance)
            ten_percent_to_send = n_to_send // 10
            i_to_send = 0
            for orthanc_instance_id, flag_send_to_remote in flag_by_instance.items():
                if flag_send_to_remote:
                    if not flag_force_anon:
                        if not flag_images_sent and log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Sending to remote.', **kwargs)
                        if (i_to_send % 10) == 0 and log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level']+3,'Sending %d of %d' % (i_to_send+1, n_to_send), **kwargs)
                    i_try = 0
                    flag_images_sent = False
                    while i_try < 5 and not flag_images_sent:
                        try:
                           # orthanc.RestApiPost('/modalities/%s/store' % os.getenv('PYTHON_ANON_ORTHANC'), orthanc_instance_id)
                            flag_images_sent = True
                        except:
                            i_try += 1
                            if log_message_bitflag:
                                log_message(log_message_bitflag, global_var['log_indent_level'], 'Failed sending image on attempt %d' % i_try, **kwargs)
                            time.sleep(5)
                else:
                    orthanc.RestApiDelete('/instances/%s' % orthanc_instance_id)
                    flag_non_original_detected = True
                i_to_send += 1

        else: # existing patient/study combo

           if log_message_bitflag:
               log_message(log_message_bitflag, global_var['log_indent_level'], 'Skipping re-anon of existing patient/study', **kwargs)

        if flag_non_original_detected:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Some non-original images were not sent', **kwargs)

    if flag_images_sent and log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Images sent to remote modalities', **kwargs)

    # UpdateLookupHTML()
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating lookup table', **kwargs)
    status = update_lookup_html(**kwargs)
    patient_name_anon = '.'
    if len(patient_name_anon_dict) > 0:
        patient_name_anon = ':'
        for patient_name_anon_temp, flag_is_new in patient_name_anon_dict.items():
            if patient_name_anon == ':':
                patient_name_anon = '%s %s' % (patient_name_anon, patient_name_anon_temp)
            else:
                patient_name_anon = '%s, %s' % (patient_name_anon, patient_name_anon_temp)

    status = auto_email('%s Anon Complete' % os.getenv('ORTHANC__NAME'), 'Anonymization complete %s' % patient_name_anon, **kwargs)
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev
    if status['status'] != 0:
        return status

    anonymization_history_atom = anonymization_history_atom_modify(anonymization_history_atom, status=0, error_text='Success', make_date_time='completed')
    anonymization_history = anonymization_history_modify(anonymization_history, 'AnonymizedTo', orthanc_study_id_anon, anonymization_history_atom, orthanc_study_id)

    return {'status' : 0}

# ============================================================================
def anonymize_study_init(orthanc_study_id, flag_force_anon=global_var['flag_force_anon'], trigger_type='manual', remote_user='None', **kwargs):
# ----------------------------------------------------------------------------
    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3
    response_system = orthanc.RestApiGet('/system')
    meta_system = json.loads(response_system)
    aet = meta_system['DicomAet']
    global_var['flag_force_anon'] = flag_force_anon
    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    meta_study = json.loads(response_study)
    anonymization_history = anonymization_history_get(orthanc_study_id)

    # ------------------------------------------------------------------------
    # Check whether this study has been anonymized before (or from another study)
    # ------------------------------------------------------------------------
    # If we are not forcing it, look for any sign of previous anon
    if trigger_type == 'onchange' or not flag_force_anon:
        # Prevent any onchange triggers if already modified or anonymized according to study meta
        flag_skip = ('ModifiedFrom' in meta_study) or ('AnonymizedFrom' in meta_study)
        if flag_skip and log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Appears to be already anonymized (orthanc history)', **kwargs)
        # If this study was previously anonymized and its child exists, skip
        if (not flag_skip) and 'AnonymizedTo' in anonymization_history:
            for orthanc_study_id_anon, atom_list in anonymization_history['AnonymizedTo'].items():
                try:
                    response_study_anon = orthanc.RestApiGet('/studies/%s' % orthanc_study_id_anon)
                    meta_study_anon = json.loads(response_study_anon)
                    if len(meta_study_anon) > 0:
                        flag_skip = True
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Appears to be already anonymized (meta history)', **kwargs)
                        break
                except:
                    continue
        # Do other studies point to this one
        if not flag_skip:
            for orthanc_study_id_other in json.loads(orthanc.RestApiGet('/studies')):
                meta_study_other = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_other))
                anonymization_history_other = anonymization_history_get(orthanc_study_id_other)
                if ('AnonymizedFrom' in meta_study_other and meta_study_other['AnonymizedFrom'] == orthanc_study_id_parent) or \
                   ('ModifiedFrom' in meta_study_other and meta_study_other['ModifiedFrom'] == orthanc_study_id_parent):
                    flag_skip = True
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Appears to be already anonymized (orthanc history prior)', **kwargs)
                if 'AnonymizedFrom' in anonymization_history_other and orthanc_study_id in anonymization_history_other['AnonymizedFrom']:
                    flag_skip = True
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Appears to be already anonymized (meta history child)', **kwargs)
                if flag_skip:
                    break
        
        # Check whether the patient name shows signs of anonymization
        if 'PatientName' in meta_study['PatientMainDicomTags'] and \
            (meta_study['PatientMainDicomTags']['PatientName'].find(meta_system['Name']) >= 0 or 
             (global_var['patient_name_base'] is not None and meta_study['PatientMainDicomTags']['PatientName'].find(global_var['patient_name_base']) >= 0)):
            flag_skip = True
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Appears to be already anonymized (meta history prior)', **kwargs)

        if 'AnonymizedFrom' in anonymization_history:
            flag_skip = True
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Appears to be already anonymized (meta history parent)', **kwargs)

        if flag_skip:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 0}

    status = {'status' : 0}
    if trigger_type == 'onchange' and log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Non-anonymized study stable.  Initiating auto anon', **kwargs)
    #email_message('%s Triggered Anonymization' % aet, 'Anonymization (%s) triggered.  Look for an update upon completion.' % trigger_type, **kwargs)
    auto_email('%s Triggered Anonymization' % aet, 'Anonymization (%s) triggered.  Look for an update upon completion.' % trigger_type, **kwargs)
    status = anonymize_study(orthanc_study_id, trigger_type, remote_user, **kwargs)
    if status['status'] != 0:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Auto anon failed: %s' % status['error_text'], **kwargs)

    if flag_force_anon:
        global_var['flag_force_anon'] = False

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return status

# =======================================================
def auto_email(subject, message, **kwargs):
# -------------------------------------------------------

    if os.getenv('PYTHON_MAIL_AUTO', default='false') == 'true':
        status = email_message(subject, message, **kwargs)
    else:
        status = {'status' : 0}

    return status

# ============================================================================
def base_tag_handling(**kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    flag_keep_siemens_mr = os.getenv('PYTHON_FLAG_KEEP_SIEMENS_MR_TAGS',default='false') == 'true'
    flag_hologic = os.getenv('PYTHON_COLLECT_HOLOGIC',default='false') == 'true'

    if os.path.exists('/etc/orthanc/anon_profile.json'):
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Reading anon profile from /etc/orthanc/anon_profile.json', **kwargs)
        try:
            with open('/etc/orthanc/anon_profile.json', 'r') as lun:
                table_from_ctp = json.load(lun)
        except:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem Reading anon profile from /etc/orthanc/anon_profile.json', **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status' : 1, 'error_text': 'Problem loading anon profile from json file'}, None, None
        if flag_hologic:
            table_from_ctp['0008-1032'] = { 'en' : True, 'op' : 'keep',      'name' : 'ProcedureCodeSeq', 'comment' : 'Winkler needs to keep this for Hologic'}
            table_from_ctp['7e01']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'HologicHeader',    'comment' : 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
            table_from_ctp['0019']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensMRHeader',  'comment' : 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
        if flag_keep_siemens_mr:
            table_from_ctp['0009']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensCSAHeader', 'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['0019']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensMRHeader',  'comment' : 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
            table_from_ctp['0021']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensCSAHeader', 'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['0027']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensCSAHeader', 'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['0029']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensCSAHeader', 'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['0051']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensMRHeader',  'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['0071']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensCSAHeader', 'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['7fdf']      = { 'en' : True, 'op' : 'groupkeep', 'name' : 'SiemensCSAHeader', 'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
    else:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], '/etc/orthanc/anon_profile.json DOES NOT EXIST.  Defaulting to default settings.', **kwargs)
        table_from_ctp = {}
        table_from_ctp['0008-0005'] = {'en' : True,  'op' : 'keep',    'name' : 'SpecificCharacterSet',                         'comment' : ''}
        table_from_ctp['0008-0008'] = {'en' : True,  'op' : 'keep',    'name' : 'ImageType',                                    'comment' : ''}
        table_from_ctp['0008-0012'] = {'en' : True,  'op' : 'keep',    'name' : 'InstanceCreationDate',                         'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0013'] = {'en' : True,  'op' : 'keep',    'name' : 'InstanceCreationTime',                         'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0014'] = {'en' : True,  'op' : 'remove',  'name' : 'InstanceCreatorUID',                           'comment' : ''}
        table_from_ctp['0008-0016'] = {'en' : True,  'op' : 'keep',    'name' : 'SOPClassUID',                                  'comment' : 'In general this is not PHI'}
        table_from_ctp['0008-0018'] = {'en' : True,  'op' : 'orthanc', 'name' : 'SOPInstanceUID',                               'comment' : 'Currently handled by Orthanc'}
        table_from_ctp['0008-0020'] = {'en' : True,  'op' : 'keep',    'name' : 'StudyDate',                                    'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0021'] = {'en' : True,  'op' : 'keep',    'name' : 'SeriesDate',                                   'comment' : ''}
        table_from_ctp['0008-0022'] = {'en' : True,  'op' : 'keep',    'name' : 'AcquisitionDate',                              'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0023'] = {'en' : True,  'op' : 'keep',    'name' : 'ContentDate',                                  'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0024'] = {'en' : True,  'op' : 'remove',  'name' : 'OverlayDate',                                  'comment' : ''}
        table_from_ctp['0008-0025'] = {'en' : True,  'op' : 'remove',  'name' : 'CurveDate',                                    'comment' : ''}
        table_from_ctp['0008-002a'] = {'en' : True,  'op' : 'keep',    'name' : 'AcquisitionDateTime',                          'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0030'] = {'en' : True,  'op' : 'keep',    'name' : 'StudyTime',                                    'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0031'] = {'en' : True,  'op' : 'keep',    'name' : 'SeriesTime',                                   'comment' : ''}
        table_from_ctp['0008-0032'] = {'en' : True,  'op' : 'keep',    'name' : 'AcquisitionTime',                              'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0033'] = {'en' : True,  'op' : 'keep',    'name' : 'ContentTime',                                  'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0008-0034'] = {'en' : True,  'op' : 'remove',  'name' : 'OverlayTime',                                  'comment' : ''}
        table_from_ctp['0008-0035'] = {'en' : True,  'op' : 'remove',  'name' : 'CurveTime',                                    'comment' : ''}
        table_from_ctp['0008-0050'] = {'en' : True,  'op' : 'keep',    'name' : 'AccessionNumber',                              'comment' : 'Orthanc will replace this'}
        table_from_ctp['0008-0052'] = {'en' : False, 'op' : '',        'name' : 'QueryRetrieveLevel',                           'comment' : ''}
        table_from_ctp['0008-0054'] = {'en' : False, 'op' : '',        'name' : 'RetrieveAET',                                  'comment' : ''}
        table_from_ctp['0008-0056'] = {'en' : False, 'op' : '',        'name' : 'InstanceAvailability',                         'comment' : ''}
        table_from_ctp['0008-0058'] = {'en' : False, 'op' : '',        'name' : 'FailedSOPInstanceUIDList',                     'comment' : ''}
        table_from_ctp['0008-0060'] = {'en' : True,  'op' : 'keep',    'name' : 'Modality',                                     'comment' : ''}
        table_from_ctp['0008-0061'] = {'en' : True,  'op' : 'keep',    'name' : 'ModalitiesInStudy',                            'comment' : ''}
        table_from_ctp['0008-0064'] = {'en' : False, 'op' : '',        'name' : 'ConversionType',                               'comment' : ''}
        table_from_ctp['0008-0068'] = {'en' : False, 'op' : '',        'name' : 'PresentationIntentType',                       'comment' : ''}
        table_from_ctp['0008-0070'] = {'en' : True,  'op' : 'keep',    'name' : 'Manufacturer',                                 'comment' : 'We typically keeps this'}
        table_from_ctp['0008-0080'] = {'en' : True,  'op' : 'remove',  'name' : 'InstitutionName',                              'comment' : ''}
        table_from_ctp['0008-0081'] = {'en' : True,  'op' : 'remove',  'name' : 'InstitutionAddress',                           'comment' : ''}
        table_from_ctp['0008-0082'] = {'en' : True,  'op' : 'remove',  'name' : 'InstitutionCodeSeq',                           'comment' : ''}
        table_from_ctp['0008-0090'] = {'en' : True,  'op' : 'empty',   'name' : 'ReferringPhysicianName',                       'comment' : ''}
        table_from_ctp['0008-0092'] = {'en' : True,  'op' : 'remove',  'name' : 'ReferringPhysicianAddress',                    'comment' : ''}
        table_from_ctp['0008-0094'] = {'en' : True,  'op' : 'remove',  'name' : 'ReferringPhysicianPhoneNumbers',               'comment' : ''}
        table_from_ctp['0008-0096'] = {'en' : True,  'op' : 'remove',  'name' : 'ReferringPhysiciansIDSeq',                     'comment' : ''}
        table_from_ctp['0008-0100'] = {'en' : False, 'op' : '',        'name' : 'CodeValue',                                    'comment' : ''}
        table_from_ctp['0008-0102'] = {'en' : False, 'op' : '',        'name' : 'CodingSchemeDesignator',                       'comment' : ''}
        table_from_ctp['0008-0103'] = {'en' : False, 'op' : '',        'name' : 'CodingSchemeVersion',                          'comment' : ''}
        table_from_ctp['0008-0104'] = {'en' : False, 'op' : '',        'name' : 'CodeMeaning',                                  'comment' : ''}
        table_from_ctp['0008-0105'] = {'en' : False, 'op' : '',        'name' : 'MappingResource',                              'comment' : ''}
        table_from_ctp['0008-0106'] = {'en' : False, 'op' : '',        'name' : 'ContextGroupVersion',                          'comment' : ''}
        table_from_ctp['0008-0107'] = {'en' : False, 'op' : '',        'name' : 'ContextGroupLocalVersion',                     'comment' : ''}
        table_from_ctp['0008-010b'] = {'en' : False, 'op' : '',        'name' : 'CodeSetExtensionFlag',                         'comment' : ''}
        table_from_ctp['0008-010c'] = {'en' : True,  'op' : 'remove',  'name' : 'PrivateCodingSchemeCreatorUID',                'comment' : ''}
        table_from_ctp['0008-010d'] = {'en' : True,  'op' : 'remove',  'name' : 'CodeSetExtensionCreatorUID',                   'comment' : ''}
        table_from_ctp['0008-010f'] = {'en' : False, 'op' : '',        'name' : 'ContextIdentifier',                            'comment' : ''}
        table_from_ctp['0008-0201'] = {'en' : True,  'op' : 'remove',  'name' : 'TimezoneOffsetFromUTC',                        'comment' : ''}
        table_from_ctp['0008-1010'] = {'en' : True,  'op' : 'remove',  'name' : 'StationName',                                  'comment' : 'Some groups want to keep this'}
        table_from_ctp['0008-1030'] = {'en' : True,  'op' : 'keep',    'name' : 'StudyDescription',                             'comment' : 'We tends to keep this'}
        if flag_hologic:
            table_from_ctp['0008-1032']={'en' : True, 'op' : 'keep',   'name' : 'ProcedureCodeSeq',                             'comment' : 'Winkler needs to keep this for Hologic'}
        else:
            table_from_ctp['0008-1032']={'en' : True, 'op' : 'remove', 'name' : 'ProcedureCodeSeq',                             'comment' : 'Winkler needs to keep this for Hologic'}
        table_from_ctp['0008-103e'] = {'en' : True,  'op' : 'keep',    'name' : 'SeriesDescription',                            'comment' : 'We tends to keep this'}
        table_from_ctp['0008-1040'] = {'en' : True,  'op' : 'remove',  'name' : 'InstitutionalDepartmentName',                  'comment' : ''}
        table_from_ctp['0008-1048'] = {'en' : True,  'op' : 'remove',  'name' : 'PhysicianOfRecord',                            'comment' : ''}
        table_from_ctp['0008-1049'] = {'en' : True,  'op' : 'remove',  'name' : 'PhysicianOfRecordIdSeq',                       'comment' : ''}
        table_from_ctp['0008-1050'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformingPhysicianName',                      'comment' : ''}
        table_from_ctp['0008-1052'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformingPhysicianIdSeq',                     'comment' : ''}
        table_from_ctp['0008-1060'] = {'en' : True,  'op' : 'remove',  'name' : 'NameOfPhysicianReadingStudy',                  'comment' : ''}
        table_from_ctp['0008-1062'] = {'en' : True,  'op' : 'remove',  'name' : 'PhysicianReadingStudyIdSeq',                   'comment' : ''}
        table_from_ctp['0008-1070'] = {'en' : True,  'op' : 'remove',  'name' : 'OperatorName',                                 'comment' : ''}
        table_from_ctp['0008-1072'] = {'en' : True,  'op' : 'remove',  'name' : 'OperatorsIdentificationSeq',                   'comment' : ''}
        table_from_ctp['0008-1080'] = {'en' : True,  'op' : 'remove',  'name' : 'AdmittingDiagnosisDescription',                'comment' : ''}
        table_from_ctp['0008-1084'] = {'en' : True,  'op' : 'remove',  'name' : 'AdmittingDiagnosisCodeSeq',                    'comment' : ''}
        table_from_ctp['0008-1090'] = {'en' : True,  'op' : 'keep',    'name' : 'ManufacturerModelName',                        'comment' : 'Some groups (Cardiac) like to keep this'}
        table_from_ctp['0008-1100'] = {'en' : False, 'op' : '',        'name' : 'RefResultsSeq',                                'comment' : ''}
        table_from_ctp['0008-1110'] = {'en' : True,  'op' : 'remove',  'name' : 'RefStudySeq',                                  'comment' : ''}
        table_from_ctp['0008-1111'] = {'en' : True,  'op' : 'remove',  'name' : 'RefPPSSeq',                                    'comment' : ''}
        table_from_ctp['0008-1115'] = {'en' : False, 'op' : '',        'name' : 'RefSeriesSeq',                                 'comment' : ''}
        table_from_ctp['0008-1120'] = {'en' : True,  'op' : 'remove',  'name' : 'RefPatientSeq',                                'comment' : ''}
        table_from_ctp['0008-1125'] = {'en' : False, 'op' : '',        'name' : 'RefVisitSeq',                                  'comment' : ''}
        table_from_ctp['0008-1130'] = {'en' : False, 'op' : '',        'name' : 'RefOverlaySeq',                                'comment' : ''}
        table_from_ctp['0008-1140'] = {'en' : True,  'op' : 'orthanc', 'name' : 'RefImageSeq',                                  'comment' : ''}
        table_from_ctp['0008-1145'] = {'en' : False, 'op' : '',        'name' : 'RefCurveSeq',                                  'comment' : ''}
        table_from_ctp['0008-114a'] = {'en' : False, 'op' : '',        'name' : 'RefInstanceSeq',                               'comment' : ''}
        table_from_ctp['0008-1150'] = {'en' : True,  'op' : 'orthanc', 'name' : 'RefSOPClassUID',                               'comment' : 'Currently handled by Orthanc'}
        table_from_ctp['0008-1155'] = {'en' : True,  'op' : 'orthanc', 'name' : 'RefSOPInstanceUID',                            'comment' : 'Currently handled by Orthanc'}
        table_from_ctp['0008-115a'] = {'en' : False, 'op' : '',        'name' : 'SOPClassesSupported',                          'comment' : ''}
        table_from_ctp['0008-1160'] = {'en' : False, 'op' : '',        'name' : 'RefFrameNumber',                               'comment' : ''}
        table_from_ctp['0008-1195'] = {'en' : True,  'op' : 'remove',  'name' : 'TransactionUID',                               'comment' : ''}
        table_from_ctp['0008-1197'] = {'en' : False, 'op' : '',        'name' : 'FailureReason',                                'comment' : ''}
        table_from_ctp['0008-1198'] = {'en' : False, 'op' : '',        'name' : 'FailedSOPSeq',                                 'comment' : ''}
        table_from_ctp['0008-1199'] = {'en' : False, 'op' : '',        'name' : 'RefSOPSeq',                                    'comment' : ''}
        table_from_ctp['0008-2111'] = {'en' : True,  'op' : 'remove',  'name' : 'DerivationDescription',                        'comment' : ''}
        table_from_ctp['0008-2112'] = {'en' : True,  'op' : 'remove',  'name' : 'SourceImageSeq',                               'comment' : ''}
        table_from_ctp['0008-2120'] = {'en' : False, 'op' : '',        'name' : 'StageName',                                    'comment' : ''}
        table_from_ctp['0008-2122'] = {'en' : False, 'op' : '',        'name' : 'StageNumber',                                  'comment' : ''}
        table_from_ctp['0008-2124'] = {'en' : False, 'op' : '',        'name' : 'NumberOfStages',                               'comment' : ''}
        table_from_ctp['0008-2128'] = {'en' : False, 'op' : '',        'name' : 'ViewNumber',                                   'comment' : ''}
        table_from_ctp['0008-2129'] = {'en' : False, 'op' : '',        'name' : 'NumberOfEventTimers',                          'comment' : ''}
        table_from_ctp['0008-212a'] = {'en' : False, 'op' : '',        'name' : 'NumberOfViewsInStage',                         'comment' : ''}
        table_from_ctp['0008-2130'] = {'en' : False, 'op' : '',        'name' : 'EventElapsedTime',                             'comment' : ''}
        table_from_ctp['0008-2132'] = {'en' : False, 'op' : '',        'name' : 'EventTimerName',                               'comment' : ''}
        table_from_ctp['0008-2142'] = {'en' : False, 'op' : '',        'name' : 'StartTrim',                                    'comment' : ''}
        table_from_ctp['0008-2143'] = {'en' : False, 'op' : '',        'name' : 'StopTrim',                                     'comment' : ''}
        table_from_ctp['0008-2144'] = {'en' : False, 'op' : '',        'name' : 'RecommendedDisplayFrameRate',                  'comment' : ''}
        table_from_ctp['0008-2218'] = {'en' : False, 'op' : '',        'name' : 'AnatomicRegionSeq',                            'comment' : ''}
        table_from_ctp['0008-2220'] = {'en' : False, 'op' : '',        'name' : 'AnatomicRegionModifierSeq',                    'comment' : ''}
        table_from_ctp['0008-2228'] = {'en' : False, 'op' : '',        'name' : 'PrimaryAnatomicStructureSeq',                  'comment' : ''}
        table_from_ctp['0008-2229'] = {'en' : False, 'op' : '',        'name' : 'AnatomicStructureSpaceRegionSeq',              'comment' : ''}
        table_from_ctp['0008-2230'] = {'en' : False, 'op' : '',        'name' : 'PrimaryAnatomicStructureModifierSeq',          'comment' : ''}
        table_from_ctp['0008-2240'] = {'en' : False, 'op' : '',        'name' : 'TransducerPositionSeq',                        'comment' : ''}
        table_from_ctp['0008-2242'] = {'en' : False, 'op' : '',        'name' : 'TransducerPositionModifierSeq',                'comment' : ''}
        table_from_ctp['0008-2244'] = {'en' : False, 'op' : '',        'name' : 'TransducerOrientationSeq',                     'comment' : ''}
        table_from_ctp['0008-2246'] = {'en' : False, 'op' : '',        'name' : 'TransducerOrientationModifierSeq',             'comment' : ''}
        table_from_ctp['0008-3010'] = {'en' : True,  'op' : 'remove',  'name' : 'IrradiationEventUID',                          'comment' : ''}
        table_from_ctp['0008-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'IdentifyingComments',                          'comment' : ''}
        table_from_ctp['0008-9007'] = {'en' : False, 'op' : '',        'name' : 'FrameType',                                    'comment' : ''}
        table_from_ctp['0008-9092'] = {'en' : False, 'op' : '',        'name' : 'ReferringImageEvidenceSeq',                    'comment' : ''}
        table_from_ctp['0008-9121'] = {'en' : False, 'op' : '',        'name' : 'RefRawDataSeq',                                'comment' : ''}
        table_from_ctp['0008-9123'] = {'en' : True,  'op' : 'remove',  'name' : 'CreatorVersionUID',                            'comment' : ''}
        table_from_ctp['0008-9124'] = {'en' : False, 'op' : '',        'name' : 'DerivationImageSeq',                           'comment' : ''}
        table_from_ctp['0008-9154'] = {'en' : False, 'op' : '',        'name' : 'SourceImageEvidenceSeq',                       'comment' : ''}
        table_from_ctp['0008-9205'] = {'en' : False, 'op' : '',        'name' : 'PixelPresentation',                            'comment' : ''}
        table_from_ctp['0008-9206'] = {'en' : False, 'op' : '',        'name' : 'VolumetricProperties',                         'comment' : ''}
        table_from_ctp['0008-9207'] = {'en' : False, 'op' : '',        'name' : 'VolumeBasedCalculationTechnique',              'comment' : ''}
        table_from_ctp['0008-9208'] = {'en' : False, 'op' : '',        'name' : 'ComplexImageComponent',                        'comment' : ''}
        table_from_ctp['0008-9209'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionContrast',                          'comment' : ''}
        table_from_ctp['0008-9215'] = {'en' : False, 'op' : '',        'name' : 'DerivationCodeSeq',                            'comment' : ''}
        table_from_ctp['0008-9237'] = {'en' : False, 'op' : '',        'name' : 'RefGrayscalePresentationStateSeq',             'comment' : ''}
        if flag_keep_siemens_mr:
            table_from_ctp['0009'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensCSAHeader',                           'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
        table_from_ctp['0010-0010'] = {'en' : False, 'op' : '',        'name' : 'PatientName',                                  'comment' : 'Handled explicitly by Orthanc'}
        table_from_ctp['0010-0020'] = {'en' : False, 'op' : '',        'name' : 'PatientID',                                    'comment' : 'Handled explicitly by Orthanc'}
        table_from_ctp['0010-0021'] = {'en' : True,  'op' : 'remove',  'name' : 'IssuerOfPatientID',                            'comment' : ''}
        table_from_ctp['0010-0030'] = {'en' : True,  'op' : 'keep',    'name' : 'PatientBirthDate',                             'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0010-0032'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientBirthTime',                             'comment' : ''}
        table_from_ctp['0010-0040'] = {'en' : True,  'op' : 'keep',    'name' : 'PatientSex',                                   'comment' : 'We keep this'}
        table_from_ctp['0010-0050'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientInsurancePlanCodeSeq',                  'comment' : ''}
        table_from_ctp['0010-0101'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientPrimaryLanguageCodeSeq',                'comment' : ''}
        table_from_ctp['0010-0102'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientPrimaryLanguageModifierCodeSeq',        'comment' : ''}
        table_from_ctp['0010-1000'] = {'en' : True,  'op' : 'remove',  'name' : 'OtherPatientIDs',                              'comment' : ''}
        table_from_ctp['0010-1001'] = {'en' : True,  'op' : 'remove',  'name' : 'OtherPatientNames',                            'comment' : ''}
        table_from_ctp['0010-1002'] = {'en' : True,  'op' : 'remove',  'name' : 'OtherPatientIDsSeq',                           'comment' : ''}
        table_from_ctp['0010-1005'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientBirthName',                             'comment' : ''}
        table_from_ctp['0010-1010'] = {'en' : True,  'op' : 'keep',    'name' : 'PatientAge',                                   'comment' : 'We keep this when shifting dates, otherwise remove'}
        table_from_ctp['0010-1020'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientSize',                                  'comment' : ''}
        table_from_ctp['0010-1030'] = {'en' : True,  'op' : 'keep',    'name' : 'PatientWeight',                                'comment' : ''}
        table_from_ctp['0010-1040'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientAddress',                               'comment' : ''}
        table_from_ctp['0010-1050'] = {'en' : True,  'op' : 'remove',  'name' : 'InsurancePlanIdentification',                  'comment' : ''}
        table_from_ctp['0010-1060'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientMotherBirthName',                       'comment' : ''}
        table_from_ctp['0010-1080'] = {'en' : True,  'op' : 'remove',  'name' : 'MilitaryRank',                                 'comment' : ''}
        table_from_ctp['0010-1081'] = {'en' : True,  'op' : 'remove',  'name' : 'BranchOfService',                              'comment' : ''}
        table_from_ctp['0010-1090'] = {'en' : True,  'op' : 'remove',  'name' : 'MedicalRecordLocator',                         'comment' : ''}
        table_from_ctp['0010-2000'] = {'en' : True,  'op' : 'remove',  'name' : 'MedicalAlerts',                                'comment' : ''}
        table_from_ctp['0010-2110'] = {'en' : True,  'op' : 'remove',  'name' : 'ContrastAllergies',                            'comment' : ''}
        table_from_ctp['0010-2150'] = {'en' : True,  'op' : 'remove',  'name' : 'CountryOfResidence',                           'comment' : ''}
        table_from_ctp['0010-2152'] = {'en' : True,  'op' : 'remove',  'name' : 'RegionOfResidence',                            'comment' : ''}
        table_from_ctp['0010-2154'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientPhoneNumbers',                          'comment' : ''}
        table_from_ctp['0010-2160'] = {'en' : True,  'op' : 'remove',  'name' : 'EthnicGroup',                                  'comment' : ''}
        table_from_ctp['0010-2180'] = {'en' : True,  'op' : 'remove',  'name' : 'Occupation',                                   'comment' : ''}
        table_from_ctp['0010-21a0'] = {'en' : True,  'op' : 'remove',  'name' : 'SmokingStatus',                                'comment' : ''}
        table_from_ctp['0010-21b0'] = {'en' : True,  'op' : 'remove',  'name' : 'AdditionalPatientHistory',                     'comment' : ''}
        table_from_ctp['0010-21c0'] = {'en' : True,  'op' : 'remove',  'name' : 'PregnancyStatus',                              'comment' : ''}
        table_from_ctp['0010-21d0'] = {'en' : True,  'op' : 'remove',  'name' : 'LastMenstrualDate',                            'comment' : ''}
        table_from_ctp['0010-21f0'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientReligiousPreference',                   'comment' : ''}
        table_from_ctp['0010-2203'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientSexNeutered',                           'comment' : ''}
        table_from_ctp['0010-2297'] = {'en' : True,  'op' : 'remove',  'name' : 'ResponsiblePerson',                            'comment' : ''}
        table_from_ctp['0010-2299'] = {'en' : True,  'op' : 'remove',  'name' : 'ResponsibleOrganization',                      'comment' : ''}
        table_from_ctp['0010-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientComments',                              'comment' : ''}
        table_from_ctp['0012-0010'] = {'en' : False, 'op' : 'fill',    'name' : 'ClinicalTrialSponsorName',                     'comment' : ''}
        table_from_ctp['0012-0020'] = {'en' : False, 'op' : '',        'name' : 'ClinicalTrialProtocolID',                      'comment' : ''}
        table_from_ctp['0012-0021'] = {'en' : False, 'op' : '',        'name' : 'ClinicalTrialProtocolName',                    'comment' : ''}
        table_from_ctp['0012-0030'] = {'en' : False, 'op' : 'fill',    'name' : 'ClinicalTrialSiteID',                          'comment' : ''}
        table_from_ctp['0012-0031'] = {'en' : False, 'op' : 'fill',    'name' : 'ClinicalTrialSiteName',                        'comment' : ''}
        table_from_ctp['0012-0040'] = {'en' : False, 'op' : 'fill',    'name' : 'ClinicalTrialSubjectID',                       'comment' : ''}
        table_from_ctp['0012-0042'] = {'en' : False, 'op' : '',        'name' : 'ClinicalTrialSubjectReadingID',                'comment' : ''}
        table_from_ctp['0012-0050'] = {'en' : False, 'op' : '',        'name' : 'ClinicalTrialTimePointID',                     'comment' : ''}
        table_from_ctp['0012-0051'] = {'en' : False, 'op' : '',        'name' : 'ClinicalTrialTimePointDescription',            'comment' : ''}
        table_from_ctp['0012-0060'] = {'en' : False, 'op' : '',        'name' : 'CoordinatingCenterName',                       'comment' : ''}
        table_from_ctp['0012-0062'] = {'en' : True,  'op' : 'keep',    'name' : 'PatientIdentityRemoved',                       'comment' : 'Need to keep and-or update'}
        table_from_ctp['0012-0063'] = {'en' : True,  'op' : 'keep',    'name' : 'DeidentificationMethod',                       'comment' : 'Need to fill this with some descriptor'}
        table_from_ctp['0012-0064'] = {'en' : True,  'op' : 'keep',    'name' : 'DeidentificationMethodCodeSeq',                'comment' : 'May need to fill this if 12-63 not filled'}
        table_from_ctp['0018-0010'] = {'en' : False, 'op' : 'empty',   'name' : 'ContrastBolusAgent',                           'comment' : ''}
        table_from_ctp['0018-0012'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusAgentSeq',                        'comment' : ''}
        table_from_ctp['0018-0014'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusAdministrationRouteSeq',          'comment' : ''}
        table_from_ctp['0018-0015'] = {'en' : False, 'op' : '',        'name' : 'BodyPartExamined',                             'comment' : ''}
        table_from_ctp['0018-0020'] = {'en' : False, 'op' : '',        'name' : 'ScanningSeq',                                  'comment' : ''}
        table_from_ctp['0018-0021'] = {'en' : False, 'op' : '',        'name' : 'SeqVariant',                                   'comment' : ''}
        table_from_ctp['0018-0022'] = {'en' : False, 'op' : '',        'name' : 'ScanOptions',                                  'comment' : ''}
        table_from_ctp['0018-0023'] = {'en' : False, 'op' : '',        'name' : 'MRAcquisitionType',                            'comment' : ''}
        table_from_ctp['0018-0024'] = {'en' : False, 'op' : '',        'name' : 'SequenceName',                                 'comment' : ''}
        table_from_ctp['0018-0025'] = {'en' : False, 'op' : '',        'name' : 'AngioFlag',                                    'comment' : ''}
        table_from_ctp['0018-0026'] = {'en' : False, 'op' : '',        'name' : 'InterventionDrugInformationSeq',               'comment' : ''}
        table_from_ctp['0018-0027'] = {'en' : False, 'op' : '',        'name' : 'InterventionDrugStopTime',                     'comment' : ''}
        table_from_ctp['0018-0028'] = {'en' : False, 'op' : '',        'name' : 'InterventionDrugDose',                         'comment' : ''}
        table_from_ctp['0018-0029'] = {'en' : False, 'op' : '',        'name' : 'InterventionDrugCodeSeq',                      'comment' : ''}
        table_from_ctp['0018-002a'] = {'en' : False, 'op' : '',        'name' : 'AdditionalDrugSeq',                            'comment' : ''}
        table_from_ctp['0018-0031'] = {'en' : False, 'op' : '',        'name' : 'Radiopharmaceutical',                          'comment' : ''}
        table_from_ctp['0018-0034'] = {'en' : False, 'op' : '',        'name' : 'InterventionDrugName',                         'comment' : ''}
        table_from_ctp['0018-0035'] = {'en' : False, 'op' : '',        'name' : 'InterventionDrugStartTime',                    'comment' : ''}
        table_from_ctp['0018-0036'] = {'en' : False, 'op' : '',        'name' : 'InterventionalTherapySeq',                     'comment' : ''}
        table_from_ctp['0018-0037'] = {'en' : False, 'op' : '',        'name' : 'TherapyType',                                  'comment' : ''}
        table_from_ctp['0018-0038'] = {'en' : False, 'op' : '',        'name' : 'InterventionalStatus',                         'comment' : ''}
        table_from_ctp['0018-0039'] = {'en' : False, 'op' : '',        'name' : 'TherapyDescription',                           'comment' : ''}
        table_from_ctp['0018-0040'] = {'en' : False, 'op' : '',        'name' : 'CineRate',                                     'comment' : ''}
        table_from_ctp['0018-0050'] = {'en' : False, 'op' : '',        'name' : 'SliceThickness',                               'comment' : ''}
        table_from_ctp['0018-0060'] = {'en' : False, 'op' : '',        'name' : 'KVP',                                          'comment' : ''}
        table_from_ctp['0018-0070'] = {'en' : False, 'op' : '',        'name' : 'CountsAccumulated',                            'comment' : ''}
        table_from_ctp['0018-0071'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionTerminationCondition',              'comment' : ''}
        table_from_ctp['0018-0072'] = {'en' : False, 'op' : '',        'name' : 'EffectiveSeriesDuration',                      'comment' : ''}
        table_from_ctp['0018-0073'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionStartCondition',                    'comment' : ''}
        table_from_ctp['0018-0074'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionStartConditionData',                'comment' : ''}
        table_from_ctp['0018-0075'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionTerminationConditionData',          'comment' : ''}
        table_from_ctp['0018-0080'] = {'en' : False, 'op' : '',        'name' : 'RepetitionTime',                               'comment' : ''}
        table_from_ctp['0018-0081'] = {'en' : True,  'op' : 'keep',    'name' : 'EchoTime',                                     'comment' : ''}
        table_from_ctp['0018-0082'] = {'en' : False, 'op' : '',        'name' : 'InversionTime',                                'comment' : ''}
        table_from_ctp['0018-0083'] = {'en' : False, 'op' : '',        'name' : 'NumberOfAverages',                             'comment' : ''}
        table_from_ctp['0018-0084'] = {'en' : False, 'op' : '',        'name' : 'ImagingFrequency',                             'comment' : ''}
        table_from_ctp['0018-0085'] = {'en' : False, 'op' : '',        'name' : 'ImagedNucleus',                                'comment' : ''}
        table_from_ctp['0018-0086'] = {'en' : True,  'op' : 'keep',    'name' : 'EchoNumber',                                   'comment' : ''}
        table_from_ctp['0018-0087'] = {'en' : False, 'op' : '',        'name' : 'MagneticFieldStrength',                        'comment' : ''}
        table_from_ctp['0018-0088'] = {'en' : False, 'op' : '',        'name' : 'SpacingBetweenSlices',                         'comment' : ''}
        table_from_ctp['0018-0089'] = {'en' : False, 'op' : '',        'name' : 'NumberOfPhaseEncodingSteps',                   'comment' : ''}
        table_from_ctp['0018-0090'] = {'en' : False, 'op' : '',        'name' : 'DataCollectionDiameter',                       'comment' : ''}
        table_from_ctp['0018-0091'] = {'en' : True,  'op' : 'keep',    'name' : 'EchoTrainLength',                              'comment' : ''}
        table_from_ctp['0018-0093'] = {'en' : False, 'op' : '',        'name' : 'PercentSampling',                              'comment' : ''}
        table_from_ctp['0018-0094'] = {'en' : False, 'op' : '',        'name' : 'PercentPhaseFieldOfView',                      'comment' : ''}
        table_from_ctp['0018-0095'] = {'en' : False, 'op' : '',        'name' : 'PixelBandwidth',                               'comment' : ''}
        table_from_ctp['0018-1000'] = {'en' : True,  'op' : 'emptyx',  'name' : 'DeviceSerialNumber',                           'comment' : 'Per Clunie validator'}
        table_from_ctp['0018-1002'] = {'en' : True,  'op' : 'remove',  'name' : 'DeviceUID',                                    'comment' : ''}
        table_from_ctp['0018-1004'] = {'en' : True,  'op' : 'remove',  'name' : 'PlateID',                                      'comment' : ''}
        table_from_ctp['0018-1005'] = {'en' : True,  'op' : 'remove',  'name' : 'GeneratorID',                                  'comment' : ''}
        table_from_ctp['0018-1007'] = {'en' : True,  'op' : 'remove',  'name' : 'CassetteID',                                   'comment' : ''}
        table_from_ctp['0018-1008'] = {'en' : True,  'op' : 'remove',  'name' : 'GantryID',                                     'comment' : ''}
        table_from_ctp['0018-1010'] = {'en' : False, 'op' : '',        'name' : 'SecondaryCaptureDeviceID',                     'comment' : ''}
        table_from_ctp['0018-1011'] = {'en' : False, 'op' : '',        'name' : 'HardcopyCreationDeviceID',                     'comment' : ''}
        table_from_ctp['0018-1012'] = {'en' : True,  'op' : 'remove',  'name' : 'DateOfSecondaryCapture',                       'comment' : ''}
        table_from_ctp['0018-1014'] = {'en' : False, 'op' : '',        'name' : 'TimeOfSecondaryCapture',                       'comment' : ''}
        table_from_ctp['0018-1016'] = {'en' : False, 'op' : '',        'name' : 'SecondaryCaptureDeviceManufacturer',           'comment' : ''}
        table_from_ctp['0018-1017'] = {'en' : False, 'op' : '',        'name' : 'HardcopyDeviceManufacturer',                   'comment' : ''}
        table_from_ctp['0018-1018'] = {'en' : False, 'op' : '',        'name' : 'SecondaryCaptureDeviceManufacturerModelName',  'comment' : ''}
        table_from_ctp['0018-1019'] = {'en' : False, 'op' : '',        'name' : 'SecondaryCaptureDeviceSoftwareVersion',        'comment' : ''}
        table_from_ctp['0018-101a'] = {'en' : False, 'op' : '',        'name' : 'HardcopyDeviceSoftwareVersion',                'comment' : ''}
        table_from_ctp['0018-101b'] = {'en' : False, 'op' : '',        'name' : 'HardcopyDeviceManfuacturerModelName',          'comment' : ''}
        table_from_ctp['0018-1020'] = {'en' : True,  'op' : 'emptyx',  'name' : 'SoftwareVersion',                              'comment' : 'Per Clunie validator'}
        table_from_ctp['0018-1022'] = {'en' : False, 'op' : '',        'name' : 'VideoImageFormatAcquired',                     'comment' : ''}
        table_from_ctp['0018-1023'] = {'en' : False, 'op' : '',        'name' : 'DigitalImageFormatAcquired',                   'comment' : ''}
        table_from_ctp['0018-1030'] = {'en' : True,  'op' : 'keep',    'name' : 'ProtocolName',                                 'comment' : 'We often keeps this'}
        table_from_ctp['0018-1040'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusRoute',                           'comment' : ''}
        table_from_ctp['0018-1041'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusVolume',                          'comment' : ''}
        table_from_ctp['0018-1042'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusStartTime',                       'comment' : ''}
        table_from_ctp['0018-1043'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusStopTime',                        'comment' : ''}
        table_from_ctp['0018-1044'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusTotalDose',                       'comment' : ''}
        table_from_ctp['0018-1045'] = {'en' : False, 'op' : '',        'name' : 'SyringeCounts',                                'comment' : ''}
        table_from_ctp['0018-1046'] = {'en' : False, 'op' : '',        'name' : 'ContrastFlowRate',                             'comment' : ''}
        table_from_ctp['0018-1047'] = {'en' : False, 'op' : '',        'name' : 'ContrastFlowDuration',                         'comment' : ''}
        table_from_ctp['0018-1048'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusIngredient',                      'comment' : ''}
        table_from_ctp['0018-1049'] = {'en' : False, 'op' : '',        'name' : 'ContrastBolusIngredientConcentration',         'comment' : ''}
        table_from_ctp['0018-1050'] = {'en' : False, 'op' : '',        'name' : 'SpatialResolution',                            'comment' : ''}
        table_from_ctp['0018-1060'] = {'en' : False, 'op' : '',        'name' : 'TriggerTime',                                  'comment' : ''}
        table_from_ctp['0018-1061'] = {'en' : False, 'op' : '',        'name' : 'TriggerSourceOrType',                          'comment' : ''}
        table_from_ctp['0018-1062'] = {'en' : False, 'op' : '',        'name' : 'NominalInterval',                              'comment' : ''}
        table_from_ctp['0018-1063'] = {'en' : False, 'op' : '',        'name' : 'FrameTime',                                    'comment' : ''}
        table_from_ctp['0018-1064'] = {'en' : False, 'op' : '',        'name' : 'FramingType',                                  'comment' : ''}
        table_from_ctp['0018-1065'] = {'en' : False, 'op' : '',        'name' : 'FrameTimeVector',                              'comment' : ''}
        table_from_ctp['0018-1066'] = {'en' : False, 'op' : '',        'name' : 'FrameDelay',                                   'comment' : ''}
        table_from_ctp['0018-1067'] = {'en' : False, 'op' : '',        'name' : 'ImageTriggerDelay',                            'comment' : ''}
        table_from_ctp['0018-1068'] = {'en' : False, 'op' : '',        'name' : 'MultiplexGroupTimeOffset',                     'comment' : ''}
        table_from_ctp['0018-1069'] = {'en' : False, 'op' : '',        'name' : 'TriggerTimeOffset',                            'comment' : ''}
        table_from_ctp['0018-106a'] = {'en' : False, 'op' : '',        'name' : 'SynchronizationTrigger',                       'comment' : ''}
        table_from_ctp['0018-106c'] = {'en' : False, 'op' : '',        'name' : 'SynchronizationChannel',                       'comment' : ''}
        table_from_ctp['0018-106e'] = {'en' : False, 'op' : '',        'name' : 'TriggerSamplePosition',                        'comment' : ''}
        table_from_ctp['0018-1070'] = {'en' : False, 'op' : '',        'name' : 'RadiopharmaceuticalRoute',                     'comment' : ''}
        table_from_ctp['0018-1071'] = {'en' : False, 'op' : '',        'name' : 'RadiopharmaceuticalVolume',                    'comment' : ''}
        table_from_ctp['0018-1072'] = {'en' : False, 'op' : '',        'name' : 'RadiopharmaceuticalStartTime',                 'comment' : ''}
        table_from_ctp['0018-1073'] = {'en' : False, 'op' : '',        'name' : 'RadiopharmaceuticalStopTime',                  'comment' : ''}
        table_from_ctp['0018-1074'] = {'en' : False, 'op' : '',        'name' : 'RadionuclideTotalDose',                        'comment' : ''}
        table_from_ctp['0018-1075'] = {'en' : False, 'op' : '',        'name' : 'RadionuclideHalfLife',                         'comment' : ''}
        table_from_ctp['0018-1076'] = {'en' : False, 'op' : '',        'name' : 'RadionuclidePositronFraction',                 'comment' : ''}
        table_from_ctp['0018-1077'] = {'en' : False, 'op' : '',        'name' : 'RadiopharmaceuticalSpecificActivity',          'comment' : ''}
        table_from_ctp['0018-1078'] = {'en' : True,  'op' : 'keep',    'name' : 'RadiopharmaceuticalStartDateTime',             'comment' : ''}
        table_from_ctp['0018-1079'] = {'en' : True,  'op' : 'keep',    'name' : 'RadiopharmaceuticalStopDateTime',              'comment' : ''}
        table_from_ctp['0018-1080'] = {'en' : False, 'op' : '',        'name' : 'BeatRejectionFlag',                            'comment' : ''}
        table_from_ctp['0018-1081'] = {'en' : False, 'op' : '',        'name' : 'LowRRValue',                                   'comment' : ''}
        table_from_ctp['0018-1082'] = {'en' : False, 'op' : '',        'name' : 'HighRRValue',                                  'comment' : ''}
        table_from_ctp['0018-1083'] = {'en' : False, 'op' : '',        'name' : 'IntervalsAcquired',                            'comment' : ''}
        table_from_ctp['0018-1084'] = {'en' : False, 'op' : '',        'name' : 'IntervalsRejected',                            'comment' : ''}
        table_from_ctp['0018-1085'] = {'en' : False, 'op' : '',        'name' : 'PVCRejection',                                 'comment' : ''}
        table_from_ctp['0018-1086'] = {'en' : False, 'op' : '',        'name' : 'SkipBeats',                                    'comment' : ''}
        table_from_ctp['0018-1088'] = {'en' : False, 'op' : '',        'name' : 'HeartRate',                                    'comment' : ''}
        table_from_ctp['0018-1090'] = {'en' : False, 'op' : '',        'name' : 'CardiacNumberOfImages',                        'comment' : ''}
        table_from_ctp['0018-1094'] = {'en' : False, 'op' : '',        'name' : 'TriggerWindow',                                'comment' : ''}
        table_from_ctp['0018-1100'] = {'en' : False, 'op' : '',        'name' : 'ReconstructionDiameter',                       'comment' : ''}
        table_from_ctp['0018-1110'] = {'en' : False, 'op' : '',        'name' : 'DistanceSourceToDetector',                     'comment' : ''}
        table_from_ctp['0018-1111'] = {'en' : False, 'op' : '',        'name' : 'DistanceSourceToPatient',                      'comment' : ''}
        table_from_ctp['0018-1114'] = {'en' : False, 'op' : '',        'name' : 'EstimatedRadiographicMagnificationFactor',     'comment' : ''}
        table_from_ctp['0018-1120'] = {'en' : False, 'op' : '',        'name' : 'GantryDetectorTilt',                           'comment' : ''}
        table_from_ctp['0018-1121'] = {'en' : False, 'op' : '',        'name' : 'GantryDetectorSlew',                           'comment' : ''}
        table_from_ctp['0018-1130'] = {'en' : False, 'op' : '',        'name' : 'TableHeight',                                  'comment' : ''}
        table_from_ctp['0018-1131'] = {'en' : False, 'op' : '',        'name' : 'TableTraverse',                                'comment' : ''}
        table_from_ctp['0018-1134'] = {'en' : False, 'op' : '',        'name' : 'TableMotion',                                  'comment' : ''}
        table_from_ctp['0018-1135'] = {'en' : False, 'op' : '',        'name' : 'TableVerticalIncrement',                       'comment' : ''}
        table_from_ctp['0018-1136'] = {'en' : False, 'op' : '',        'name' : 'TableLateralIncrement',                        'comment' : ''}
        table_from_ctp['0018-1137'] = {'en' : False, 'op' : '',        'name' : 'TableLongitudinalIncrement',                   'comment' : ''}
        table_from_ctp['0018-1138'] = {'en' : False, 'op' : '',        'name' : 'TableAngle',                                   'comment' : ''}
        table_from_ctp['0018-113a'] = {'en' : False, 'op' : '',        'name' : 'TableType',                                    'comment' : ''}
        table_from_ctp['0018-1140'] = {'en' : False, 'op' : '',        'name' : 'RotationDirection',                            'comment' : ''}
        table_from_ctp['0018-1141'] = {'en' : False, 'op' : '',        'name' : 'AngularPosition',                              'comment' : ''}
        table_from_ctp['0018-1142'] = {'en' : False, 'op' : '',        'name' : 'RadialPosition',                               'comment' : ''}
        table_from_ctp['0018-1143'] = {'en' : False, 'op' : '',        'name' : 'ScanArc',                                      'comment' : ''}
        table_from_ctp['0018-1144'] = {'en' : False, 'op' : '',        'name' : 'AngularStep',                                  'comment' : ''}
        table_from_ctp['0018-1145'] = {'en' : False, 'op' : '',        'name' : 'CenterOfRotationOffset',                       'comment' : ''}
        table_from_ctp['0018-1147'] = {'en' : False, 'op' : '',        'name' : 'FieldOfViewShape',                             'comment' : ''}
        table_from_ctp['0018-1149'] = {'en' : False, 'op' : '',        'name' : 'FieldOfViewDimension',                         'comment' : ''}
        table_from_ctp['0018-1150'] = {'en' : False, 'op' : '',        'name' : 'ExposureTime',                                 'comment' : ''}
        table_from_ctp['0018-1151'] = {'en' : False, 'op' : '',        'name' : 'XRayTubeCurrent',                              'comment' : ''}
        table_from_ctp['0018-1152'] = {'en' : False, 'op' : '',        'name' : 'Exposure',                                     'comment' : ''}
        table_from_ctp['0018-1153'] = {'en' : False, 'op' : '',        'name' : 'ExposureInuAs',                                'comment' : ''}
        table_from_ctp['0018-1154'] = {'en' : False, 'op' : '',        'name' : 'AveragePulseWidth',                            'comment' : ''}
        table_from_ctp['0018-1155'] = {'en' : False, 'op' : '',        'name' : 'RadiationSetting',                             'comment' : ''}
        table_from_ctp['0018-1156'] = {'en' : False, 'op' : '',        'name' : 'RectificationType',                            'comment' : ''}
        table_from_ctp['0018-115a'] = {'en' : False, 'op' : '',        'name' : 'RadiationMode',                                'comment' : ''}
        table_from_ctp['0018-115e'] = {'en' : False, 'op' : '',        'name' : 'ImageAreaDoseProduct',                         'comment' : ''}
        table_from_ctp['0018-1160'] = {'en' : False, 'op' : '',        'name' : 'FilterType',                                   'comment' : ''}
        table_from_ctp['0018-1161'] = {'en' : False, 'op' : '',        'name' : 'TypeOfFilters',                                'comment' : ''}
        table_from_ctp['0018-1162'] = {'en' : False, 'op' : '',        'name' : 'IntensifierSize',                              'comment' : ''}
        table_from_ctp['0018-1164'] = {'en' : False, 'op' : '',        'name' : 'ImagerPixelSpacing',                           'comment' : ''}
        table_from_ctp['0018-1166'] = {'en' : False, 'op' : '',        'name' : 'Grid',                                         'comment' : ''}
        table_from_ctp['0018-1170'] = {'en' : False, 'op' : '',        'name' : 'GeneratorPower',                               'comment' : ''}
        table_from_ctp['0018-1180'] = {'en' : False, 'op' : '',        'name' : 'CollimatorGridName',                           'comment' : ''}
        table_from_ctp['0018-1181'] = {'en' : False, 'op' : '',        'name' : 'CollimatorType',                               'comment' : ''}
        table_from_ctp['0018-1182'] = {'en' : False, 'op' : '',        'name' : 'FocalDistance',                                'comment' : ''}
        table_from_ctp['0018-1183'] = {'en' : False, 'op' : '',        'name' : 'XFocusCenter',                                 'comment' : ''}
        table_from_ctp['0018-1184'] = {'en' : False, 'op' : '',        'name' : 'YFocusCenter',                                 'comment' : ''}
        table_from_ctp['0018-1190'] = {'en' : False, 'op' : '',        'name' : 'FocalSpot',                                    'comment' : ''}
        table_from_ctp['0018-1191'] = {'en' : False, 'op' : '',        'name' : 'AnodeTargetMaterial',                          'comment' : ''}
        table_from_ctp['0018-11a0'] = {'en' : False, 'op' : '',        'name' : 'BodyPartThickness',                            'comment' : ''}
        table_from_ctp['0018-11a2'] = {'en' : False, 'op' : '',        'name' : 'CompressionForce',                             'comment' : ''}
        table_from_ctp['0018-1200'] = {'en' : True,  'op' : 'remove',  'name' : 'DateOfLastCalibration',                        'comment' : ''}
        table_from_ctp['0018-1201'] = {'en' : False, 'op' : '',        'name' : 'TimeOfLastCalibration',                        'comment' : ''}
        table_from_ctp['0018-1210'] = {'en' : False, 'op' : '',        'name' : 'ConvolutionKernel',                            'comment' : ''}
        table_from_ctp['0018-1242'] = {'en' : False, 'op' : '',        'name' : 'ActualFrameDuration',                          'comment' : ''}
        table_from_ctp['0018-1243'] = {'en' : False, 'op' : '',        'name' : 'CountRate',                                    'comment' : ''}
        table_from_ctp['0018-1244'] = {'en' : False, 'op' : '',        'name' : 'PreferredPlaybackSequencing',                  'comment' : ''}
        table_from_ctp['0018-1250'] = {'en' : False, 'op' : '',        'name' : 'ReceiveCoilName',                              'comment' : ''}
        table_from_ctp['0018-1251'] = {'en' : False, 'op' : '',        'name' : 'TransmitCoilName',                             'comment' : ''}
        table_from_ctp['0018-1260'] = {'en' : False, 'op' : '',        'name' : 'PlateType',                                    'comment' : ''}
        table_from_ctp['0018-1261'] = {'en' : False, 'op' : '',        'name' : 'PhosphorType',                                 'comment' : ''}
        table_from_ctp['0018-1300'] = {'en' : False, 'op' : '',        'name' : 'ScanVelocity',                                 'comment' : ''}
        table_from_ctp['0018-1301'] = {'en' : False, 'op' : '',        'name' : 'WholeBodyTechnique',                           'comment' : ''}
        table_from_ctp['0018-1302'] = {'en' : False, 'op' : '',        'name' : 'ScanLength',                                   'comment' : ''}
        table_from_ctp['0018-1310'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionMatrix',                            'comment' : ''}
        table_from_ctp['0018-1312'] = {'en' : False, 'op' : '',        'name' : 'PhaseEncodingDirection',                       'comment' : ''}
        table_from_ctp['0018-1314'] = {'en' : False, 'op' : '',        'name' : 'FlipAngle',                                    'comment' : ''}
        table_from_ctp['0018-1315'] = {'en' : False, 'op' : '',        'name' : 'VariableFlipAngleFlag',                        'comment' : ''}
        table_from_ctp['0018-1316'] = {'en' : False, 'op' : '',        'name' : 'SAR',                                          'comment' : ''}
        table_from_ctp['0018-1318'] = {'en' : False, 'op' : '',        'name' : 'dBDt',                                         'comment' : ''}
        table_from_ctp['0018-1400'] = {'en' : True,  'op' : 'remove',  'name' : 'AcquisitionDeviceProcessingDescription',       'comment' : ''}
        table_from_ctp['0018-1401'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionDeviceProcessingCode',              'comment' : ''}
        table_from_ctp['0018-1402'] = {'en' : False, 'op' : '',        'name' : 'CassetteOrientation',                          'comment' : ''}
        table_from_ctp['0018-1403'] = {'en' : False, 'op' : '',        'name' : 'CassetteSize',                                 'comment' : ''}
        table_from_ctp['0018-1404'] = {'en' : False, 'op' : '',        'name' : 'ExposuresOnPlate',                             'comment' : ''}
        table_from_ctp['0018-1405'] = {'en' : False, 'op' : '',        'name' : 'RelativeXRayExposure',                         'comment' : ''}
        table_from_ctp['0018-1450'] = {'en' : False, 'op' : '',        'name' : 'ColumnAngulation',                             'comment' : ''}
        table_from_ctp['0018-1460'] = {'en' : False, 'op' : '',        'name' : 'TomoLayerHeight',                              'comment' : ''}
        table_from_ctp['0018-1470'] = {'en' : False, 'op' : '',        'name' : 'TomoAngle',                                    'comment' : ''}
        table_from_ctp['0018-1480'] = {'en' : False, 'op' : '',        'name' : 'TomoTime',                                     'comment' : ''}
        table_from_ctp['0018-1490'] = {'en' : False, 'op' : '',        'name' : 'TomoType',                                     'comment' : ''}
        table_from_ctp['0018-1491'] = {'en' : False, 'op' : '',        'name' : 'TomoClass',                                    'comment' : ''}
        table_from_ctp['0018-1495'] = {'en' : False, 'op' : '',        'name' : 'NumberofTomosynthesisSourceImages',            'comment' : ''}
        table_from_ctp['0018-1500'] = {'en' : False, 'op' : '',        'name' : 'PositionerMotion',                             'comment' : ''}
        table_from_ctp['0018-1508'] = {'en' : False, 'op' : '',        'name' : 'PositionerType',                               'comment' : ''}
        table_from_ctp['0018-1510'] = {'en' : False, 'op' : '',        'name' : 'PositionerPrimaryAngle',                       'comment' : ''}
        table_from_ctp['0018-1511'] = {'en' : False, 'op' : '',        'name' : 'PositionerSecondaryAngle',                     'comment' : ''}
        table_from_ctp['0018-1520'] = {'en' : False, 'op' : '',        'name' : 'PositionerPrimaryAngleIncrement',              'comment' : ''}
        table_from_ctp['0018-1521'] = {'en' : False, 'op' : '',        'name' : 'PositionerSecondaryAngleIncrement',            'comment' : ''}
        table_from_ctp['0018-1530'] = {'en' : False, 'op' : '',        'name' : 'DetectorPrimaryAngle',                         'comment' : ''}
        table_from_ctp['0018-1531'] = {'en' : False, 'op' : '',        'name' : 'DetectorSecondaryAngle',                       'comment' : ''}
        table_from_ctp['0018-1600'] = {'en' : False, 'op' : '',        'name' : 'ShutterShape',                                 'comment' : ''}
        table_from_ctp['0018-1602'] = {'en' : False, 'op' : '',        'name' : 'ShutterLeftVerticalEdge',                      'comment' : ''}
        table_from_ctp['0018-1604'] = {'en' : False, 'op' : '',        'name' : 'ShutterRightVerticalEdge',                     'comment' : ''}
        table_from_ctp['0018-1606'] = {'en' : False, 'op' : '',        'name' : 'ShutterUpperHorizontalEdge',                   'comment' : ''}
        table_from_ctp['0018-1608'] = {'en' : False, 'op' : '',        'name' : 'ShutterLowerHorizontalEdge',                   'comment' : ''}
        table_from_ctp['0018-1610'] = {'en' : False, 'op' : '',        'name' : 'CenterOfCircularShutter',                      'comment' : ''}
        table_from_ctp['0018-1612'] = {'en' : False, 'op' : '',        'name' : 'RadiusOfCircularShutter',                      'comment' : ''}
        table_from_ctp['0018-1620'] = {'en' : False, 'op' : '',        'name' : 'VerticesOfPolygonalShutter',                   'comment' : ''}
        table_from_ctp['0018-1622'] = {'en' : False, 'op' : '',        'name' : 'ShutterPresentationValue',                     'comment' : ''}
        table_from_ctp['0018-1623'] = {'en' : False, 'op' : '',        'name' : 'ShutterOverlayGroup',                          'comment' : ''}
        table_from_ctp['0018-1700'] = {'en' : False, 'op' : '',        'name' : 'CollimatorShape',                              'comment' : ''}
        table_from_ctp['0018-1702'] = {'en' : False, 'op' : '',        'name' : 'CollimatorLeftVerticalEdge',                   'comment' : ''}
        table_from_ctp['0018-1704'] = {'en' : False, 'op' : '',        'name' : 'CollimatorRightVerticalEdge',                  'comment' : ''}
        table_from_ctp['0018-1706'] = {'en' : False, 'op' : '',        'name' : 'CollimatorUpperHorizontalEdge',                'comment' : ''}
        table_from_ctp['0018-1708'] = {'en' : False, 'op' : '',        'name' : 'CollimatorLowerHorizontalEdge',                'comment' : ''}
        table_from_ctp['0018-1710'] = {'en' : False, 'op' : '',        'name' : 'CenterOfCircularCollimator',                   'comment' : ''}
        table_from_ctp['0018-1712'] = {'en' : False, 'op' : '',        'name' : 'RadiusOfCircularCollimator',                   'comment' : ''}
        table_from_ctp['0018-1720'] = {'en' : False, 'op' : '',        'name' : 'VerticesOfPolygonalCollimator',                'comment' : ''}
        table_from_ctp['0018-1800'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionTimeSynchronized',                  'comment' : ''}
        table_from_ctp['0018-1801'] = {'en' : False, 'op' : '',        'name' : 'TimeSource',                                   'comment' : ''}
        table_from_ctp['0018-1802'] = {'en' : False, 'op' : '',        'name' : 'TimeDistributionProtocol',                     'comment' : ''}
        table_from_ctp['0018-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'AcquisitionComments',                          'comment' : ''}
        table_from_ctp['0018-5000'] = {'en' : False, 'op' : '',        'name' : 'OutputPower',                                  'comment' : ''}
        table_from_ctp['0018-5010'] = {'en' : False, 'op' : '',        'name' : 'TransducerData',                               'comment' : ''}
        table_from_ctp['0018-5012'] = {'en' : False, 'op' : '',        'name' : 'FocusDepth',                                   'comment' : ''}
        table_from_ctp['0018-5020'] = {'en' : False, 'op' : '',        'name' : 'ProcessingFunction',                           'comment' : ''}
        table_from_ctp['0018-5021'] = {'en' : False, 'op' : '',        'name' : 'PostprocessingFunction',                       'comment' : ''}
        table_from_ctp['0018-5022'] = {'en' : False, 'op' : '',        'name' : 'MechanicalIndex',                              'comment' : ''}
        table_from_ctp['0018-5024'] = {'en' : False, 'op' : '',        'name' : 'ThermalIndex',                                 'comment' : ''}
        table_from_ctp['0018-5026'] = {'en' : False, 'op' : '',        'name' : 'CranialThermalIndex',                          'comment' : ''}
        table_from_ctp['0018-5027'] = {'en' : False, 'op' : '',        'name' : 'SoftTissueThermalIndex',                       'comment' : ''}
        table_from_ctp['0018-5028'] = {'en' : False, 'op' : '',        'name' : 'SoftTissueFocusThermalIndex',                  'comment' : ''}
        table_from_ctp['0018-5029'] = {'en' : False, 'op' : '',        'name' : 'SoftTissueSurfaceThermalIndex',                'comment' : ''}
        table_from_ctp['0018-5050'] = {'en' : False, 'op' : '',        'name' : 'DepthOfScanField',                             'comment' : ''}
        table_from_ctp['0018-5100'] = {'en' : False, 'op' : '',        'name' : 'PatientPosition',                              'comment' : ''}
        table_from_ctp['0018-5101'] = {'en' : False, 'op' : '',        'name' : 'ViewPosition',                                 'comment' : ''}
        table_from_ctp['0018-5104'] = {'en' : False, 'op' : '',        'name' : 'ProjectionEponymousNameCodeSeq',               'comment' : ''}
        table_from_ctp['0018-5210'] = {'en' : False, 'op' : '',        'name' : 'ImageTransformationMatrix',                    'comment' : ''}
        table_from_ctp['0018-5212'] = {'en' : False, 'op' : '',        'name' : 'ImageTranslationVector',                       'comment' : ''}
        table_from_ctp['0018-6000'] = {'en' : False, 'op' : '',        'name' : 'Sensitivity',                                  'comment' : ''}
        table_from_ctp['0018-6011'] = {'en' : False, 'op' : '',        'name' : 'SeqOfUltrasoundRegions',                       'comment' : ''}
        table_from_ctp['0018-6012'] = {'en' : False, 'op' : '',        'name' : 'RegionSpatialFormat',                          'comment' : ''}
        table_from_ctp['0018-6014'] = {'en' : False, 'op' : '',        'name' : 'RegionDataType',                               'comment' : ''}
        table_from_ctp['0018-6016'] = {'en' : False, 'op' : '',        'name' : 'RegionFlags',                                  'comment' : ''}
        table_from_ctp['0018-6018'] = {'en' : False, 'op' : '',        'name' : 'RegionLocationMinX0',                          'comment' : ''}
        table_from_ctp['0018-601a'] = {'en' : False, 'op' : '',        'name' : 'RegionLocationMinY0',                          'comment' : ''}
        table_from_ctp['0018-601c'] = {'en' : False, 'op' : '',        'name' : 'RegionLocationMaxX1',                          'comment' : ''}
        table_from_ctp['0018-601e'] = {'en' : False, 'op' : '',        'name' : 'RegionLocationMaxY1',                          'comment' : ''}
        table_from_ctp['0018-6020'] = {'en' : False, 'op' : '',        'name' : 'ReferencePixelX0',                             'comment' : ''}
        table_from_ctp['0018-6022'] = {'en' : False, 'op' : '',        'name' : 'ReferencePixelY0',                             'comment' : ''}
        table_from_ctp['0018-6024'] = {'en' : False, 'op' : '',        'name' : 'PhysicalUnitsXDirection',                      'comment' : ''}
        table_from_ctp['0018-6026'] = {'en' : False, 'op' : '',        'name' : 'PhysicalUnitsYDirection',                      'comment' : ''}
        table_from_ctp['0018-6028'] = {'en' : False, 'op' : '',        'name' : 'ReferencePixelPhysicalValueX',                 'comment' : ''}
        table_from_ctp['0018-602a'] = {'en' : False, 'op' : '',        'name' : 'ReferencePixelPhysicalValueY',                 'comment' : ''}
        table_from_ctp['0018-602c'] = {'en' : False, 'op' : '',        'name' : 'PhysicalDeltaX',                               'comment' : ''}
        table_from_ctp['0018-602e'] = {'en' : False, 'op' : '',        'name' : 'PhysicalDeltaY',                               'comment' : ''}
        table_from_ctp['0018-6030'] = {'en' : False, 'op' : '',        'name' : 'TransducerFrequency',                          'comment' : ''}
        table_from_ctp['0018-6031'] = {'en' : False, 'op' : '',        'name' : 'TransducerType',                               'comment' : ''}
        table_from_ctp['0018-6032'] = {'en' : False, 'op' : '',        'name' : 'PulseRepetitionFrequency',                     'comment' : ''}
        table_from_ctp['0018-6034'] = {'en' : False, 'op' : '',        'name' : 'DopplerCorrectionAngle',                       'comment' : ''}
        table_from_ctp['0018-6036'] = {'en' : False, 'op' : '',        'name' : 'SteeringAngle',                                'comment' : ''}
        table_from_ctp['0018-6038'] = {'en' : False, 'op' : '',        'name' : 'DopplerSampleVolumeXPosition',                 'comment' : ''}
        table_from_ctp['0018-603a'] = {'en' : False, 'op' : '',        'name' : 'DopplerSampleVolumeYPosition',                 'comment' : ''}
        table_from_ctp['0018-603c'] = {'en' : False, 'op' : '',        'name' : 'TMLinePositionX0',                             'comment' : ''}
        table_from_ctp['0018-603e'] = {'en' : False, 'op' : '',        'name' : 'TMLinePositionY0',                             'comment' : ''}
        table_from_ctp['0018-6040'] = {'en' : False, 'op' : '',        'name' : 'TMLinePositionX1',                             'comment' : ''}
        table_from_ctp['0018-6042'] = {'en' : False, 'op' : '',        'name' : 'TMLinePositionY1',                             'comment' : ''}
        table_from_ctp['0018-6044'] = {'en' : False, 'op' : '',        'name' : 'PixelComponentOrganization',                   'comment' : ''}
        table_from_ctp['0018-6046'] = {'en' : False, 'op' : '',        'name' : 'PixelComponentMask',                           'comment' : ''}
        table_from_ctp['0018-6048'] = {'en' : False, 'op' : '',        'name' : 'PixelComponentRangeStart',                     'comment' : ''}
        table_from_ctp['0018-604a'] = {'en' : False, 'op' : '',        'name' : 'PixelComponentRangeStop',                      'comment' : ''}
        table_from_ctp['0018-604c'] = {'en' : False, 'op' : '',        'name' : 'PixelComponentPhysicalUnits',                  'comment' : ''}
        table_from_ctp['0018-604e'] = {'en' : False, 'op' : '',        'name' : 'PixelComponentDataType',                       'comment' : ''}
        table_from_ctp['0018-6050'] = {'en' : False, 'op' : '',        'name' : 'NumberOfTableBreakPoints',                     'comment' : ''}
        table_from_ctp['0018-6052'] = {'en' : False, 'op' : '',        'name' : 'TableOfXBreakPoints',                          'comment' : ''}
        table_from_ctp['0018-6054'] = {'en' : False, 'op' : '',        'name' : 'TableOfYBreakPoints',                          'comment' : ''}
        table_from_ctp['0018-6056'] = {'en' : False, 'op' : '',        'name' : 'NumberOfTableEntries',                         'comment' : ''}
        table_from_ctp['0018-6058'] = {'en' : False, 'op' : '',        'name' : 'TableOfPixelValues',                           'comment' : ''}
        table_from_ctp['0018-605a'] = {'en' : False, 'op' : '',        'name' : 'TableOfParameterValues',                       'comment' : ''}
        table_from_ctp['0018-7000'] = {'en' : False, 'op' : '',        'name' : 'DetectorConditionsNominalFlag',                'comment' : ''}
        table_from_ctp['0018-7001'] = {'en' : False, 'op' : '',        'name' : 'DetectorTemperature',                          'comment' : ''}
        table_from_ctp['0018-7004'] = {'en' : False, 'op' : '',        'name' : 'DetectorType',                                 'comment' : ''}
        table_from_ctp['0018-7005'] = {'en' : False, 'op' : '',        'name' : 'DetectorConfiguration',                        'comment' : ''}
        table_from_ctp['0018-7006'] = {'en' : False, 'op' : '',        'name' : 'DetectorDescription',                          'comment' : ''}
        table_from_ctp['0018-7008'] = {'en' : False, 'op' : '',        'name' : 'DetectorMode',                                 'comment' : ''}
        table_from_ctp['0018-700a'] = {'en' : True,  'op' : 'remove',  'name' : 'DetectorID',                                   'comment' : ''}
        table_from_ctp['0018-700c'] = {'en' : True,  'op' : 'remove',  'name' : 'DateOfLastDetectorCalibration',                'comment' : ''}
        table_from_ctp['0018-700e'] = {'en' : False, 'op' : '',        'name' : 'TimeOfLastDetectorCalibration',                'comment' : ''}
        table_from_ctp['0018-7010'] = {'en' : False, 'op' : '',        'name' : 'ExposuresOnDetectorSinceLastCalibration',      'comment' : ''}
        table_from_ctp['0018-7011'] = {'en' : False, 'op' : '',        'name' : 'ExposuresOnDetectorSinceManufactured',         'comment' : ''}
        table_from_ctp['0018-7012'] = {'en' : False, 'op' : '',        'name' : 'DetectorTimeSinceLastExposure',                'comment' : ''}
        table_from_ctp['0018-7014'] = {'en' : False, 'op' : '',        'name' : 'DetectorActiveTime',                           'comment' : ''}
        table_from_ctp['0018-7016'] = {'en' : False, 'op' : '',        'name' : 'DetectorActivationOffsetFromExposure',         'comment' : ''}
        table_from_ctp['0018-701a'] = {'en' : False, 'op' : '',        'name' : 'DetectorBinning',                              'comment' : ''}
        table_from_ctp['0018-7020'] = {'en' : False, 'op' : '',        'name' : 'DetectorElementPhysicalSize',                  'comment' : ''}
        table_from_ctp['0018-7022'] = {'en' : False, 'op' : '',        'name' : 'DetectorElementSpacing',                       'comment' : ''}
        table_from_ctp['0018-7024'] = {'en' : False, 'op' : '',        'name' : 'DetectorActiveShape',                          'comment' : ''}
        table_from_ctp['0018-7026'] = {'en' : False, 'op' : '',        'name' : 'DetectorActiveDimension',                      'comment' : ''}
        table_from_ctp['0018-7028'] = {'en' : False, 'op' : '',        'name' : 'DetectorActiveOrigin',                         'comment' : ''}
        table_from_ctp['0018-7030'] = {'en' : False, 'op' : '',        'name' : 'FieldOfViewOrigin',                            'comment' : ''}
        table_from_ctp['0018-7032'] = {'en' : False, 'op' : '',        'name' : 'FieldOfViewRotation',                          'comment' : ''}
        table_from_ctp['0018-7034'] = {'en' : False, 'op' : '',        'name' : 'FieldOfViewHorizontalFlip',                    'comment' : ''}
        table_from_ctp['0018-7040'] = {'en' : False, 'op' : '',        'name' : 'GridAbsorbingMaterial',                        'comment' : ''}
        table_from_ctp['0018-7041'] = {'en' : False, 'op' : '',        'name' : 'GridSpacingMaterial',                          'comment' : ''}
        table_from_ctp['0018-7042'] = {'en' : False, 'op' : '',        'name' : 'GridThickness',                                'comment' : ''}
        table_from_ctp['0018-7044'] = {'en' : False, 'op' : '',        'name' : 'GridPitch',                                    'comment' : ''}
        table_from_ctp['0018-7046'] = {'en' : False, 'op' : '',        'name' : 'GridAspectRatio',                              'comment' : ''}
        table_from_ctp['0018-7048'] = {'en' : False, 'op' : '',        'name' : 'GridPeriod',                                   'comment' : ''}
        table_from_ctp['0018-704c'] = {'en' : False, 'op' : '',        'name' : 'GridFocalDistance',                            'comment' : ''}
        table_from_ctp['0018-7050'] = {'en' : False, 'op' : '',        'name' : 'FilterMaterial',                               'comment' : ''}
        table_from_ctp['0018-7052'] = {'en' : False, 'op' : '',        'name' : 'FilterThicknessMinimum',                       'comment' : ''}
        table_from_ctp['0018-7054'] = {'en' : False, 'op' : '',        'name' : 'FilterThicknessMaximum',                       'comment' : ''}
        table_from_ctp['0018-7060'] = {'en' : False, 'op' : '',        'name' : 'ExposureControlMode',                          'comment' : ''}
        table_from_ctp['0018-7062'] = {'en' : False, 'op' : '',        'name' : 'ExposureControlModeDescription',               'comment' : ''}
        table_from_ctp['0018-7064'] = {'en' : False, 'op' : '',        'name' : 'ExposureStatus',                               'comment' : ''}
        table_from_ctp['0018-7065'] = {'en' : False, 'op' : '',        'name' : 'PhototimerSetting',                            'comment' : ''}
        table_from_ctp['0018-8150'] = {'en' : False, 'op' : '',        'name' : 'ExposureTimeInuS',                             'comment' : ''}
        table_from_ctp['0018-8151'] = {'en' : False, 'op' : '',        'name' : 'XRayTubeCurrentInuA',                          'comment' : ''}
        table_from_ctp['0018-9004'] = {'en' : False, 'op' : '',        'name' : 'ContentQualification',                         'comment' : ''}
        table_from_ctp['0018-9005'] = {'en' : False, 'op' : '',        'name' : 'PulseSequenceName',                            'comment' : ''}
        table_from_ctp['0018-9006'] = {'en' : False, 'op' : '',        'name' : 'MRImagingModifierSeq',                         'comment' : ''}
        table_from_ctp['0018-9008'] = {'en' : False, 'op' : '',        'name' : 'EchoPulseSeq',                                 'comment' : ''}
        table_from_ctp['0018-9009'] = {'en' : False, 'op' : '',        'name' : 'InversionRecovery',                            'comment' : ''}
        table_from_ctp['0018-9010'] = {'en' : False, 'op' : '',        'name' : 'FlowCompensation',                             'comment' : ''}
        table_from_ctp['0018-9011'] = {'en' : False, 'op' : '',        'name' : 'MultipleSpinEcho',                             'comment' : ''}
        table_from_ctp['0018-9012'] = {'en' : False, 'op' : '',        'name' : 'MultiPlanarExcitation',                        'comment' : ''}
        table_from_ctp['0018-9014'] = {'en' : False, 'op' : '',        'name' : 'PhaseContrast',                                'comment' : ''}
        table_from_ctp['0018-9015'] = {'en' : False, 'op' : '',        'name' : 'TimeOfFlightContrast',                         'comment' : ''}
        table_from_ctp['0018-9016'] = {'en' : False, 'op' : '',        'name' : 'Spoiling',                                     'comment' : ''}
        table_from_ctp['0018-9017'] = {'en' : False, 'op' : '',        'name' : 'SteadyStatePulseSeq',                          'comment' : ''}
        table_from_ctp['0018-9018'] = {'en' : False, 'op' : '',        'name' : 'EchoPlanarPulseSeq',                           'comment' : ''}
        table_from_ctp['0018-9019'] = {'en' : False, 'op' : '',        'name' : 'TagAngleFirstAxis',                            'comment' : ''}
        table_from_ctp['0018-9020'] = {'en' : False, 'op' : '',        'name' : 'MagnetizationTransfer',                        'comment' : ''}
        table_from_ctp['0018-9021'] = {'en' : False, 'op' : '',        'name' : 'T2Preparation',                                'comment' : ''}
        table_from_ctp['0018-9022'] = {'en' : False, 'op' : '',        'name' : 'BloodSignalNulling',                           'comment' : ''}
        table_from_ctp['0018-9024'] = {'en' : False, 'op' : '',        'name' : 'SaturationRecovery',                           'comment' : ''}
        table_from_ctp['0018-9025'] = {'en' : False, 'op' : '',        'name' : 'SpectrallySelectedSuppression',                'comment' : ''}
        table_from_ctp['0018-9026'] = {'en' : False, 'op' : '',        'name' : 'SpectrallySelectedExcitation',                 'comment' : ''}
        table_from_ctp['0018-9027'] = {'en' : False, 'op' : '',        'name' : 'SpatialPreSaturation',                         'comment' : ''}
        table_from_ctp['0018-9028'] = {'en' : False, 'op' : '',        'name' : 'Tagging',                                      'comment' : ''}
        table_from_ctp['0018-9029'] = {'en' : False, 'op' : '',        'name' : 'OversamplingPhase',                            'comment' : ''}
        table_from_ctp['0018-9030'] = {'en' : False, 'op' : '',        'name' : 'TagSpacingFirstDimension',                     'comment' : ''}
        table_from_ctp['0018-9032'] = {'en' : False, 'op' : '',        'name' : 'GeometryOfKSpaceTraversal',                    'comment' : ''}
        table_from_ctp['0018-9033'] = {'en' : False, 'op' : '',        'name' : 'SegmentedKSpaceTraversal',                     'comment' : ''}
        table_from_ctp['0018-9034'] = {'en' : False, 'op' : '',        'name' : 'RectilinearPhaseEncodeReordering',             'comment' : ''}
        table_from_ctp['0018-9035'] = {'en' : False, 'op' : '',        'name' : 'TagThickness',                                 'comment' : ''}
        table_from_ctp['0018-9036'] = {'en' : False, 'op' : '',        'name' : 'PartialFourierDirection',                      'comment' : ''}
        table_from_ctp['0018-9037'] = {'en' : False, 'op' : '',        'name' : 'GatingSynchronizationTechnique',               'comment' : ''}
        table_from_ctp['0018-9041'] = {'en' : False, 'op' : '',        'name' : 'ReceiveCoilManufacturerName',                  'comment' : ''}
        table_from_ctp['0018-9042'] = {'en' : False, 'op' : '',        'name' : 'MRReceiveCoilSeq',                             'comment' : ''}
        table_from_ctp['0018-9043'] = {'en' : False, 'op' : '',        'name' : 'ReceiveCoilType',                              'comment' : ''}
        table_from_ctp['0018-9044'] = {'en' : False, 'op' : '',        'name' : 'QuadratureReceiveCoil',                        'comment' : ''}
        table_from_ctp['0018-9045'] = {'en' : False, 'op' : '',        'name' : 'MultiCoilDefinitionSeq',                       'comment' : ''}
        table_from_ctp['0018-9046'] = {'en' : False, 'op' : '',        'name' : 'MultiCoilConfiguration',                       'comment' : ''}
        table_from_ctp['0018-9047'] = {'en' : False, 'op' : '',        'name' : 'MultiCoilElementName',                         'comment' : ''}
        table_from_ctp['0018-9048'] = {'en' : False, 'op' : '',        'name' : 'MultiCoilElementUsed',                         'comment' : ''}
        table_from_ctp['0018-9049'] = {'en' : False, 'op' : '',        'name' : 'MRTransmitCoilSeq',                            'comment' : ''}
        table_from_ctp['0018-9050'] = {'en' : False, 'op' : '',        'name' : 'TransmitCoilManufacturerName',                 'comment' : ''}
        table_from_ctp['0018-9051'] = {'en' : False, 'op' : '',        'name' : 'TransmitCoilType',                             'comment' : ''}
        table_from_ctp['0018-9052'] = {'en' : False, 'op' : '',        'name' : 'SpectralWidth',                                'comment' : ''}
        table_from_ctp['0018-9053'] = {'en' : False, 'op' : '',        'name' : 'ChemicalShiftReference',                       'comment' : ''}
        table_from_ctp['0018-9054'] = {'en' : False, 'op' : '',        'name' : 'VolumeLocalizationTechnique',                  'comment' : ''}
        table_from_ctp['0018-9058'] = {'en' : False, 'op' : '',        'name' : 'MRAcquisitionFrequencyEncodingSteps',          'comment' : ''}
        table_from_ctp['0018-9059'] = {'en' : False, 'op' : '',        'name' : 'DeCoupling',                                   'comment' : ''}
        table_from_ctp['0018-9060'] = {'en' : False, 'op' : '',        'name' : 'DeCoupledNucleus',                             'comment' : ''}
        table_from_ctp['0018-9061'] = {'en' : False, 'op' : '',        'name' : 'DeCouplingFrequency',                          'comment' : ''}
        table_from_ctp['0018-9062'] = {'en' : False, 'op' : '',        'name' : 'DeCouplingMethod',                             'comment' : ''}
        table_from_ctp['0018-9063'] = {'en' : False, 'op' : '',        'name' : 'DeCouplingChemicalShiftReference',             'comment' : ''}
        table_from_ctp['0018-9064'] = {'en' : False, 'op' : '',        'name' : 'KSpaceFiltering',                              'comment' : ''}
        table_from_ctp['0018-9065'] = {'en' : False, 'op' : '',        'name' : 'TimeDomainFiltering',                          'comment' : ''}
        table_from_ctp['0018-9066'] = {'en' : False, 'op' : '',        'name' : 'NumberOfZeroFills',                            'comment' : ''}
        table_from_ctp['0018-9067'] = {'en' : False, 'op' : '',        'name' : 'BaselineCorrection',                           'comment' : ''}
        table_from_ctp['0018-9070'] = {'en' : False, 'op' : '',        'name' : 'CardiacRRIntervalSpecified',                   'comment' : ''}
        table_from_ctp['0018-9073'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionDuration',                          'comment' : ''}
        table_from_ctp['0018-9074'] = {'en' : True,  'op' : 'keep',    'name' : 'FrameAcquisitionDateTime',                     'comment' : 'Per Clunie validator'}
        table_from_ctp['0018-9075'] = {'en' : False, 'op' : '',        'name' : 'DiffusionDirectionality',                      'comment' : ''}
        table_from_ctp['0018-9076'] = {'en' : False, 'op' : '',        'name' : 'DiffusionGradientDirectionSeq',                'comment' : ''}
        table_from_ctp['0018-9077'] = {'en' : False, 'op' : '',        'name' : 'ParallelAcquisition',                          'comment' : ''}
        table_from_ctp['0018-9078'] = {'en' : False, 'op' : '',        'name' : 'ParallelAcquisitionTechnique',                 'comment' : ''}
        table_from_ctp['0018-9079'] = {'en' : False, 'op' : '',        'name' : 'InversionTimes',                               'comment' : ''}
        table_from_ctp['0018-9080'] = {'en' : False, 'op' : '',        'name' : 'MetaboliteMapDescription',                     'comment' : ''}
        table_from_ctp['0018-9081'] = {'en' : False, 'op' : '',        'name' : 'PartialFourier',                               'comment' : ''}
        table_from_ctp['0018-9082'] = {'en' : False, 'op' : '',        'name' : 'EffectiveEchoTime',                            'comment' : ''}
        table_from_ctp['0018-9084'] = {'en' : False, 'op' : '',        'name' : 'ChemicalShiftSeq',                             'comment' : ''}
        table_from_ctp['0018-9085'] = {'en' : False, 'op' : '',        'name' : 'CardiacSignalSource',                          'comment' : ''}
        table_from_ctp['0018-9087'] = {'en' : False, 'op' : '',        'name' : 'DiffusionBValue',                              'comment' : ''}
        table_from_ctp['0018-9089'] = {'en' : False, 'op' : '',        'name' : 'DiffusionGradientOrientation',                 'comment' : ''}
        table_from_ctp['0018-9090'] = {'en' : False, 'op' : '',        'name' : 'VelocityEncodingDirection',                    'comment' : ''}
        table_from_ctp['0018-9091'] = {'en' : False, 'op' : '',        'name' : 'VelocityEncodingMinimumValue',                 'comment' : ''}
        table_from_ctp['0018-9093'] = {'en' : False, 'op' : '',        'name' : 'NumberOfKSpaceTrajectories',                   'comment' : ''}
        table_from_ctp['0018-9094'] = {'en' : False, 'op' : '',        'name' : 'CoverageOfKSpace',                             'comment' : ''}
        table_from_ctp['0018-9095'] = {'en' : False, 'op' : '',        'name' : 'SpectroscopyAcquisitionPhaseRows',             'comment' : ''}
        table_from_ctp['0018-9096'] = {'en' : False, 'op' : '',        'name' : 'ParallelReductionFactorInPlane',               'comment' : ''}
        table_from_ctp['0018-9098'] = {'en' : False, 'op' : '',        'name' : 'TransmitterFrequency',                         'comment' : ''}
        table_from_ctp['0018-9100'] = {'en' : False, 'op' : '',        'name' : 'ResonantNucleus',                              'comment' : ''}
        table_from_ctp['0018-9101'] = {'en' : False, 'op' : '',        'name' : 'FrequencyCorrection',                          'comment' : ''}
        table_from_ctp['0018-9103'] = {'en' : False, 'op' : '',        'name' : 'MRSpectroscopyFOVGeometrySeq',                 'comment' : ''}
        table_from_ctp['0018-9104'] = {'en' : False, 'op' : '',        'name' : 'SlabThickness',                                'comment' : ''}
        table_from_ctp['0018-9105'] = {'en' : False, 'op' : '',        'name' : 'SlabOrientation',                              'comment' : ''}
        table_from_ctp['0018-9106'] = {'en' : False, 'op' : '',        'name' : 'MidSlabPosition',                              'comment' : ''}
        table_from_ctp['0018-9107'] = {'en' : False, 'op' : '',        'name' : 'MRSpatialSaturationSeq',                       'comment' : ''}
        table_from_ctp['0018-9112'] = {'en' : False, 'op' : '',        'name' : 'MRTimingAndRelatedParametersSeq',              'comment' : ''}
        table_from_ctp['0018-9114'] = {'en' : False, 'op' : '',        'name' : 'MREchoSeq',                                    'comment' : ''}
        table_from_ctp['0018-9115'] = {'en' : False, 'op' : '',        'name' : 'MRModifierSeq',                                'comment' : ''}
        table_from_ctp['0018-9117'] = {'en' : False, 'op' : '',        'name' : 'MRDiffusionSeq',                               'comment' : ''}
        table_from_ctp['0018-9118'] = {'en' : False, 'op' : '',        'name' : 'CardiacTriggerSeq',                            'comment' : ''}
        table_from_ctp['0018-9119'] = {'en' : False, 'op' : '',        'name' : 'MRAveragesSeq',                                'comment' : ''}
        table_from_ctp['0018-9125'] = {'en' : False, 'op' : '',        'name' : 'MRFOVGeometrySeq',                             'comment' : ''}
        table_from_ctp['0018-9126'] = {'en' : False, 'op' : '',        'name' : 'VolumeLocalizationSeq',                        'comment' : ''}
        table_from_ctp['0018-9127'] = {'en' : False, 'op' : '',        'name' : 'SpectroscopyAcquisitionDataColumns',           'comment' : ''}
        table_from_ctp['0018-9147'] = {'en' : False, 'op' : '',        'name' : 'DiffusionAnisotropyType',                      'comment' : ''}
        table_from_ctp['0018-9151'] = {'en' : True,  'op' : 'keep',    'name' : 'FrameReferenceDateTime',                       'comment' : 'Per Clunie validator'}
        table_from_ctp['0018-9152'] = {'en' : False, 'op' : '',        'name' : 'MetaboliteMapSeq',                             'comment' : ''}
        table_from_ctp['0018-9155'] = {'en' : False, 'op' : '',        'name' : 'ParallelReductionFactorOutOfPlane',            'comment' : ''}
        table_from_ctp['0018-9159'] = {'en' : False, 'op' : '',        'name' : 'SpectroscopyAcquisitionOutOfPlanePhaseSteps',  'comment' : ''}
        table_from_ctp['0018-9166'] = {'en' : False, 'op' : '',        'name' : 'BulkMotionStatus',                             'comment' : ''}
        table_from_ctp['0018-9168'] = {'en' : True,  'op' : 'keep',    'name' : 'ParallelReductionFactorSecondInPlane',         'comment' : 'Per Clunie validator'}
        table_from_ctp['0018-9169'] = {'en' : False, 'op' : '',        'name' : 'CardiacBeatRejectionTechnique',                'comment' : ''}
        table_from_ctp['0018-9170'] = {'en' : False, 'op' : '',        'name' : 'RespiratoryMotionCompensation',                'comment' : ''}
        table_from_ctp['0018-9171'] = {'en' : False, 'op' : '',        'name' : 'RespiratorySignalSource',                      'comment' : ''}
        table_from_ctp['0018-9172'] = {'en' : False, 'op' : '',        'name' : 'BulkMotionCompensationTechnique',              'comment' : ''}
        table_from_ctp['0018-9173'] = {'en' : False, 'op' : '',        'name' : 'BulkMotionSignal',                             'comment' : ''}
        table_from_ctp['0018-9174'] = {'en' : False, 'op' : '',        'name' : 'ApplicableSafetyStandardAgency',               'comment' : ''}
        table_from_ctp['0018-9175'] = {'en' : False, 'op' : '',        'name' : 'ApplicableSafetyStandardVersion',              'comment' : ''}
        table_from_ctp['0018-9176'] = {'en' : False, 'op' : '',        'name' : 'OperationModeSeq',                             'comment' : ''}
        table_from_ctp['0018-9177'] = {'en' : False, 'op' : '',        'name' : 'OperatingModeType',                            'comment' : ''}
        table_from_ctp['0018-9178'] = {'en' : False, 'op' : '',        'name' : 'OperationMode',                                'comment' : ''}
        table_from_ctp['0018-9179'] = {'en' : False, 'op' : '',        'name' : 'SpecificAbsorptionRateDefinition',             'comment' : ''}
        table_from_ctp['0018-9180'] = {'en' : False, 'op' : '',        'name' : 'GradientOutputType',                           'comment' : ''}
        table_from_ctp['0018-9181'] = {'en' : False, 'op' : '',        'name' : 'SpecificAbsorptionRateValue',                  'comment' : ''}
        table_from_ctp['0018-9182'] = {'en' : False, 'op' : '',        'name' : 'GradientOutput',                               'comment' : ''}
        table_from_ctp['0018-9183'] = {'en' : False, 'op' : '',        'name' : 'FlowCompensationDirection',                    'comment' : ''}
        table_from_ctp['0018-9184'] = {'en' : False, 'op' : '',        'name' : 'TaggingDelay',                                 'comment' : ''}
        table_from_ctp['0018-9195'] = {'en' : False, 'op' : '',        'name' : 'ChemicalShiftsMinimumIntegrationLimit',        'comment' : ''}
        table_from_ctp['0018-9196'] = {'en' : False, 'op' : '',        'name' : 'ChemicalShiftsMaximumIntegrationLimit',        'comment' : ''}
        table_from_ctp['0018-9197'] = {'en' : False, 'op' : '',        'name' : 'MRVelocityEncodingSeq',                        'comment' : ''}
        table_from_ctp['0018-9198'] = {'en' : False, 'op' : '',        'name' : 'FirstOrderPhaseCorrection',                    'comment' : ''}
        table_from_ctp['0018-9199'] = {'en' : False, 'op' : '',        'name' : 'WaterReferencedPhaseCorrection',               'comment' : ''}
        table_from_ctp['0018-9200'] = {'en' : False, 'op' : '',        'name' : 'MRSpectroscopyAcquisitionType',                'comment' : ''}
        table_from_ctp['0018-9214'] = {'en' : False, 'op' : '',        'name' : 'RespiratoryMotionStatus',                      'comment' : ''}
        table_from_ctp['0018-9217'] = {'en' : False, 'op' : '',        'name' : 'VelocityEncodingMaximumValue',                 'comment' : ''}
        table_from_ctp['0018-9218'] = {'en' : False, 'op' : '',        'name' : 'TagSpacingSecondDimension',                    'comment' : ''}
        table_from_ctp['0018-9219'] = {'en' : False, 'op' : '',        'name' : 'TagAngleSecondAxis',                           'comment' : ''}
        table_from_ctp['0018-9220'] = {'en' : False, 'op' : '',        'name' : 'FrameAcquisitionDuration',                     'comment' : ''}
        table_from_ctp['0018-9226'] = {'en' : False, 'op' : '',        'name' : 'MRImageFrameTypeSeq',                          'comment' : ''}
        table_from_ctp['0018-9227'] = {'en' : False, 'op' : '',        'name' : 'MRSpectroscopyFrameTypeSeq',                   'comment' : ''}
        table_from_ctp['0018-9231'] = {'en' : False, 'op' : '',        'name' : 'MRAcquisitionPhaseEncodingStepsInPlane',       'comment' : ''}
        table_from_ctp['0018-9232'] = {'en' : False, 'op' : '',        'name' : 'MRAcquisitionPhaseEncodingStepsOutOfPlane',    'comment' : ''}
        table_from_ctp['0018-9234'] = {'en' : False, 'op' : '',        'name' : 'SpectroscopyAcquisitionPhaseColumns',          'comment' : ''}
        table_from_ctp['0018-9236'] = {'en' : False, 'op' : '',        'name' : 'CardiacMotionStatus',                          'comment' : ''}
        table_from_ctp['0018-9239'] = {'en' : False, 'op' : '',        'name' : 'SpecificAbsorptionRateSeq',                    'comment' : ''}
        table_from_ctp['0018-9424'] = {'en' : True,  'op' : 'remove',  'name' : 'AcquisitionProtocolDescription',               'comment' : ''}
        table_from_ctp['0018-a003'] = {'en' : True,  'op' : 'remove',  'name' : 'ContributionDescription',                      'comment' : ''}
        if flag_hologic or flag_keep_siemens_mr:
            table_from_ctp['0019'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensMRHeader',                            'comment' : 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
        table_from_ctp['0020-000d'] = {'en' : True,  'op' : 'orthanc', 'name' : 'StudyInstanceUID',                             'comment' : 'Currently handled by Orthanc'}
        table_from_ctp['0020-000e'] = {'en' : True,  'op' : 'orthanc', 'name' : 'SeriesInstanceUID',                            'comment' : 'Currently handled by Orthanc'}
        table_from_ctp['0020-0010'] = {'en' : True,  'op' : 'keep',    'name' : 'StudyID',                                      'comment' : 'Orthanc later anonymizes this'}
        table_from_ctp['0020-0011'] = {'en' : False, 'op' : '',        'name' : 'SeriesNumber',                                 'comment' : ''}
        table_from_ctp['0020-0012'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionNumber',                            'comment' : ''}
        table_from_ctp['0020-0013'] = {'en' : False, 'op' : '',        'name' : 'InstanceNumber',                               'comment' : ''}
        table_from_ctp['0020-0019'] = {'en' : False, 'op' : '',        'name' : 'ItemNumber',                                   'comment' : ''}
        table_from_ctp['0020-0020'] = {'en' : False, 'op' : '',        'name' : 'PatientOrientation',                           'comment' : ''}
        table_from_ctp['0020-0022'] = {'en' : False, 'op' : '',        'name' : 'OverlayNumber',                                'comment' : ''}
        table_from_ctp['0020-0024'] = {'en' : False, 'op' : '',        'name' : 'CurveNumber',                                  'comment' : ''}
        table_from_ctp['0020-0026'] = {'en' : False, 'op' : '',        'name' : 'LUTNumber',                                    'comment' : ''}
        table_from_ctp['0020-0032'] = {'en' : False, 'op' : '',        'name' : 'ImagePosition',                                'comment' : ''}
        table_from_ctp['0020-0037'] = {'en' : False, 'op' : '',        'name' : 'ImageOrientation',                             'comment' : ''}
        table_from_ctp['0020-0052'] = {'en' : True,  'op' : 'orthanc', 'name' : 'FrameOfReferenceUID',                          'comment' : 'Currently handled by Orthanc'}
        table_from_ctp['0020-0060'] = {'en' : False, 'op' : '',        'name' : 'Laterality',                                   'comment' : ''}
        table_from_ctp['0020-0062'] = {'en' : False, 'op' : '',        'name' : 'ImageLaterality',                              'comment' : ''}
        table_from_ctp['0020-0100'] = {'en' : False, 'op' : '',        'name' : 'TemporalPositionIdentifier',                   'comment' : ''}
        table_from_ctp['0020-0105'] = {'en' : False, 'op' : '',        'name' : 'NumberOfTemporalPositions',                    'comment' : ''}
        table_from_ctp['0020-0110'] = {'en' : False, 'op' : '',        'name' : 'TemporalResolution',                           'comment' : ''}
        table_from_ctp['0020-0200'] = {'en' : True,  'op' : 'remove',  'name' : 'SynchronizationFrameOfReferenceUID',           'comment' : ''}
        table_from_ctp['0020-1000'] = {'en' : False, 'op' : '',        'name' : 'SeriesInStudy',                                'comment' : ''}
        table_from_ctp['0020-1002'] = {'en' : False, 'op' : '',        'name' : 'ImagesInAcquisition',                          'comment' : ''}
        table_from_ctp['0020-1004'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionsInStudy',                          'comment' : ''}
        table_from_ctp['0020-1040'] = {'en' : False, 'op' : '',        'name' : 'PositionReferenceIndicator',                   'comment' : ''}
        table_from_ctp['0020-1041'] = {'en' : False, 'op' : '',        'name' : 'SliceLocation',                                'comment' : ''}
        table_from_ctp['0020-1070'] = {'en' : False, 'op' : '',        'name' : 'OtherStudyNumbers',                            'comment' : ''}
        table_from_ctp['0020-1200'] = {'en' : False, 'op' : '',        'name' : 'NumberOfPatientRelatedStudies',                'comment' : ''}
        table_from_ctp['0020-1202'] = {'en' : False, 'op' : '',        'name' : 'NumberOfPatientRelatedSeries',                 'comment' : ''}
        table_from_ctp['0020-1204'] = {'en' : False, 'op' : '',        'name' : 'NumberOfPatientRelatedInstances',              'comment' : ''}
        table_from_ctp['0020-1206'] = {'en' : False, 'op' : '',        'name' : 'NumberOfStudyRelatedSeries',                   'comment' : ''}
        table_from_ctp['0020-1208'] = {'en' : False, 'op' : '',        'name' : 'NumberOfStudyRelatedInstances',                'comment' : ''}
        table_from_ctp['0020-1209'] = {'en' : False, 'op' : '',        'name' : 'NumberOfSeriesRelatedInstances',               'comment' : ''}
        table_from_ctp['0020-3401'] = {'en' : True,  'op' : 'remove',  'name' : 'ModifyingDeviceID',                            'comment' : ''}
        table_from_ctp['0020-3404'] = {'en' : True,  'op' : 'remove',  'name' : 'ModifyingDeviceManufacturer',                  'comment' : ''}
        table_from_ctp['0020-3406'] = {'en' : True,  'op' : 'remove',  'name' : 'ModifiedImageDescription',                     'comment' : ''}
        table_from_ctp['0020-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'ImageComments',                                'comment' : 'We often keeps this, but siemens retro-recon puts PHI here'}
        table_from_ctp['0020-9056'] = {'en' : False, 'op' : '',        'name' : 'StackID',                                      'comment' : ''}
        table_from_ctp['0020-9057'] = {'en' : False, 'op' : '',        'name' : 'InStackPositionNumber',                        'comment' : ''}
        table_from_ctp['0020-9071'] = {'en' : False, 'op' : '',        'name' : 'FrameAnatomySeq',                              'comment' : ''}
        table_from_ctp['0020-9072'] = {'en' : False, 'op' : '',        'name' : 'FrameLaterality',                              'comment' : ''}
        table_from_ctp['0020-9111'] = {'en' : False, 'op' : '',        'name' : 'FrameContentSeq',                              'comment' : ''}
        table_from_ctp['0020-9113'] = {'en' : False, 'op' : '',        'name' : 'PlanePositionSeq',                             'comment' : ''}
        table_from_ctp['0020-9116'] = {'en' : False, 'op' : '',        'name' : 'PlaneOrientationSeq',                          'comment' : ''}
        table_from_ctp['0020-9128'] = {'en' : False, 'op' : '',        'name' : 'TemporalPositionIndex',                        'comment' : ''}
        table_from_ctp['0020-9153'] = {'en' : False, 'op' : '',        'name' : 'TriggerDelayTime',                             'comment' : ''}
        table_from_ctp['0020-9156'] = {'en' : False, 'op' : '',        'name' : 'FrameAcquisitionNumber',                       'comment' : ''}
        table_from_ctp['0020-9157'] = {'en' : False, 'op' : '',        'name' : 'DimensionIndexValues',                         'comment' : ''}
        table_from_ctp['0020-9158'] = {'en' : False, 'op' : '',        'name' : 'FrameComments',                                'comment' : ''}
        table_from_ctp['0020-9161'] = {'en' : True,  'op' : 'remove',  'name' : 'ConcatenationUID',                             'comment' : ''}
        table_from_ctp['0020-9162'] = {'en' : False, 'op' : '',        'name' : 'InConcatenationNumber',                        'comment' : ''}
        table_from_ctp['0020-9163'] = {'en' : False, 'op' : '',        'name' : 'InConcatenationTotalNumber',                   'comment' : ''}
        table_from_ctp['0020-9164'] = {'en' : True,  'op' : 'keep',    'name' : 'DimensionOrganizationUID',                     'comment' : 'Per clunie validator - Dicom standard requires keeping this UID used for multiframe enhanced'}
        table_from_ctp['0020-9165'] = {'en' : False, 'op' : '',        'name' : 'DimensionIndexPointer',                        'comment' : ''}
        table_from_ctp['0020-9167'] = {'en' : False, 'op' : '',        'name' : 'FunctionalGroupSequencePointer',               'comment' : ''}
        table_from_ctp['0020-9213'] = {'en' : False, 'op' : '',        'name' : 'DimensionIndexPrivateCreator',                 'comment' : ''}
        table_from_ctp['0020-9221'] = {'en' : False, 'op' : '',        'name' : 'DimensionOrganizationSeq',                     'comment' : ''}
        table_from_ctp['0020-9222'] = {'en' : False, 'op' : '',        'name' : 'DimensionSeq',                                 'comment' : ''}
        table_from_ctp['0020-9228'] = {'en' : False, 'op' : '',        'name' : 'ConcatenationFrameOffsetNumber',               'comment' : ''}
        table_from_ctp['0020-9238'] = {'en' : False, 'op' : '',        'name' : 'FunctionalGroupPrivateCreator',                'comment' : ''}
        if flag_keep_siemens_mr:
            table_from_ctp['0021'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensCSAHeader',                           'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
            table_from_ctp['0027'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensCSAHeader',                           'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
        table_from_ctp['0028-0002'] = {'en' : False, 'op' : '',        'name' : 'SamplesPerPixel',                              'comment' : ''}
        table_from_ctp['0028-0004'] = {'en' : False, 'op' : '',        'name' : 'PhotometricInterpretation',                    'comment' : ''}
        table_from_ctp['0028-0006'] = {'en' : False, 'op' : '',        'name' : 'PlanarConfiguration',                          'comment' : ''}
        table_from_ctp['0028-0008'] = {'en' : False, 'op' : '',        'name' : 'NumberOfFrames',                               'comment' : ''}
        table_from_ctp['0028-0009'] = {'en' : False, 'op' : '',        'name' : 'FrameIncrementPointer',                        'comment' : ''}
        table_from_ctp['0028-0010'] = {'en' : False, 'op' : '',        'name' : 'Rows',                                         'comment' : ''}
        table_from_ctp['0028-0011'] = {'en' : False, 'op' : '',        'name' : 'Columns',                                      'comment' : ''}
        table_from_ctp['0028-0012'] = {'en' : False, 'op' : '',        'name' : 'Planes',                                       'comment' : ''}
        table_from_ctp['0028-0014'] = {'en' : False, 'op' : '',        'name' : 'UltrasoundColorDataPresent',                   'comment' : ''}
        table_from_ctp['0028-0030'] = {'en' : False, 'op' : '',        'name' : 'PixelSpacing',                                 'comment' : ''}
        table_from_ctp['0028-0031'] = {'en' : False, 'op' : '',        'name' : 'ZoomFactor',                                   'comment' : ''}
        table_from_ctp['0028-0032'] = {'en' : False, 'op' : '',        'name' : 'ZoomCenter',                                   'comment' : ''}
        table_from_ctp['0028-0034'] = {'en' : False, 'op' : '',        'name' : 'PixelAspectRatio',                             'comment' : ''}
        table_from_ctp['0028-0051'] = {'en' : False, 'op' : '',        'name' : 'CorrectedImage',                               'comment' : ''}
        table_from_ctp['0028-0100'] = {'en' : False, 'op' : '',        'name' : 'BitsAllocated',                                'comment' : ''}
        table_from_ctp['0028-0101'] = {'en' : False, 'op' : '',        'name' : 'BitsStored',                                   'comment' : ''}
        table_from_ctp['0028-0102'] = {'en' : False, 'op' : '',        'name' : 'HighBit',                                      'comment' : ''}
        table_from_ctp['0028-0103'] = {'en' : False, 'op' : '',        'name' : 'PixelRepresentation',                          'comment' : ''}
        table_from_ctp['0028-0106'] = {'en' : False, 'op' : '',        'name' : 'SmallestImagePixelValue',                      'comment' : ''}
        table_from_ctp['0028-0107'] = {'en' : False, 'op' : '',        'name' : 'LargestImagePixelValue',                       'comment' : ''}
        table_from_ctp['0028-0108'] = {'en' : False, 'op' : '',        'name' : 'SmallestPixelValueInSeries',                   'comment' : ''}
        table_from_ctp['0028-0109'] = {'en' : False, 'op' : '',        'name' : 'LargestPixelValueInSeries',                    'comment' : ''}
        table_from_ctp['0028-0110'] = {'en' : False, 'op' : '',        'name' : 'SmallestImagePixelValueInPlane',               'comment' : ''}
        table_from_ctp['0028-0111'] = {'en' : False, 'op' : '',        'name' : 'LargestImagePixelValueInPlane',                'comment' : ''}
        table_from_ctp['0028-0120'] = {'en' : False, 'op' : '',        'name' : 'PixelPaddingValue',                            'comment' : ''}
        table_from_ctp['0028-0300'] = {'en' : False, 'op' : '',        'name' : 'QualityControlImage',                          'comment' : ''}
        table_from_ctp['0028-0301'] = {'en' : False, 'op' : '',        'name' : 'BurnedInAnnotation',                           'comment' : ''}
        table_from_ctp['0028-1040'] = {'en' : False, 'op' : '',        'name' : 'PixelIntensityRelationship',                   'comment' : ''}
        table_from_ctp['0028-1041'] = {'en' : False, 'op' : '',        'name' : 'PixelIntensityRelationshipSign',               'comment' : ''}
        table_from_ctp['0028-1050'] = {'en' : False, 'op' : '',        'name' : 'WindowCenter',                                 'comment' : ''}
        table_from_ctp['0028-1051'] = {'en' : False, 'op' : '',        'name' : 'WindowWidth',                                  'comment' : ''}
        table_from_ctp['0028-1052'] = {'en' : False, 'op' : '',        'name' : 'RescaleIntercept',                             'comment' : ''}
        table_from_ctp['0028-1053'] = {'en' : False, 'op' : '',        'name' : 'RescaleSlope',                                 'comment' : ''}
        table_from_ctp['0028-1054'] = {'en' : False, 'op' : '',        'name' : 'RescaleType',                                  'comment' : ''}
        table_from_ctp['0028-1055'] = {'en' : False, 'op' : '',        'name' : 'WindowCenterWidthExplanation',                 'comment' : ''}
        table_from_ctp['0028-1090'] = {'en' : False, 'op' : '',        'name' : 'RecommendedViewingMode',                       'comment' : ''}
        table_from_ctp['0028-1101'] = {'en' : False, 'op' : '',        'name' : 'RedPaletteColorLUTDescriptor',                 'comment' : ''}
        table_from_ctp['0028-1102'] = {'en' : False, 'op' : '',        'name' : 'GreenPaletteColorLUTDescriptor',               'comment' : ''}
        table_from_ctp['0028-1103'] = {'en' : False, 'op' : '',        'name' : 'BluePaletteColorLUTDescriptor',                'comment' : ''}
        table_from_ctp['0028-1199'] = {'en' : True,  'op' : 'remove',  'name' : 'PaletteColorLUTUID',                           'comment' : ''}
        table_from_ctp['0028-1201'] = {'en' : False, 'op' : '',        'name' : 'RedPaletteColorLUTData',                       'comment' : ''}
        table_from_ctp['0028-1202'] = {'en' : False, 'op' : '',        'name' : 'GreenPaletteColorLUTData',                     'comment' : ''}
        table_from_ctp['0028-1203'] = {'en' : False, 'op' : '',        'name' : 'BluePaletteColorLUTData',                      'comment' : ''}
        table_from_ctp['0028-1214'] = {'en' : False, 'op' : '',        'name' : 'LargePaletteColorLUTUid',                      'comment' : ''}
        table_from_ctp['0028-1221'] = {'en' : False, 'op' : '',        'name' : 'SegmentedRedPaletteColorLUTData',              'comment' : ''}
        table_from_ctp['0028-1222'] = {'en' : False, 'op' : '',        'name' : 'SegmentedGreenPaletteColorLUTData',            'comment' : ''}
        table_from_ctp['0028-1223'] = {'en' : False, 'op' : '',        'name' : 'SegmentedBluePaletteColorLUTData',             'comment' : ''}
        table_from_ctp['0028-1300'] = {'en' : False, 'op' : '',        'name' : 'ImplantPresent',                               'comment' : ''}
        table_from_ctp['0028-1350'] = {'en' : False, 'op' : '',        'name' : 'PartialView',                                  'comment' : ''}
        table_from_ctp['0028-1351'] = {'en' : False, 'op' : '',        'name' : 'PartialViewDescription',                       'comment' : ''}
        table_from_ctp['0028-2110'] = {'en' : False, 'op' : '',        'name' : 'LossyImageCompression',                        'comment' : ''}
        table_from_ctp['0028-2112'] = {'en' : False, 'op' : '',        'name' : 'LossyImageCompressionRatio',                   'comment' : ''}
        table_from_ctp['0028-3000'] = {'en' : False, 'op' : '',        'name' : 'ModalityLUTSeq',                               'comment' : ''}
        table_from_ctp['0028-3002'] = {'en' : False, 'op' : '',        'name' : 'LUTDescriptor',                                'comment' : ''}
        table_from_ctp['0028-3003'] = {'en' : False, 'op' : '',        'name' : 'LUTExplanation',                               'comment' : ''}
        table_from_ctp['0028-3004'] = {'en' : False, 'op' : '',        'name' : 'ModalityLUTType',                              'comment' : ''}
        table_from_ctp['0028-3006'] = {'en' : False, 'op' : '',        'name' : 'LUTData',                                      'comment' : ''}
        table_from_ctp['0028-3010'] = {'en' : False, 'op' : '',        'name' : 'VOILUTSeq',                                    'comment' : ''}
        table_from_ctp['0028-3110'] = {'en' : False, 'op' : '',        'name' : 'SoftcopyVOILUTSeq',                            'comment' : ''}
        table_from_ctp['0028-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'ImagePresentationComments',                    'comment' : ''}
        table_from_ctp['0028-5000'] = {'en' : False, 'op' : '',        'name' : 'BiPlaneAcquisitionSeq',                        'comment' : ''}
        table_from_ctp['0028-6010'] = {'en' : False, 'op' : '',        'name' : 'RepresentativeFrameNumber',                    'comment' : ''}
        table_from_ctp['0028-6020'] = {'en' : False, 'op' : '',        'name' : 'FrameNumbersOfInterest',                       'comment' : ''}
        table_from_ctp['0028-6022'] = {'en' : False, 'op' : '',        'name' : 'FrameOfInterestDescription',                   'comment' : ''}
        table_from_ctp['0028-6030'] = {'en' : False, 'op' : '',        'name' : 'MaskPointer',                                  'comment' : ''}
        table_from_ctp['0028-6040'] = {'en' : False, 'op' : '',        'name' : 'RWavePointer',                                 'comment' : ''}
        table_from_ctp['0028-6100'] = {'en' : False, 'op' : '',        'name' : 'MaskSubtractionSeq',                           'comment' : ''}
        table_from_ctp['0028-6101'] = {'en' : False, 'op' : '',        'name' : 'MaskOperation',                                'comment' : ''}
        table_from_ctp['0028-6102'] = {'en' : False, 'op' : '',        'name' : 'ApplicableFrameRange',                         'comment' : ''}
        table_from_ctp['0028-6110'] = {'en' : False, 'op' : '',        'name' : 'MaskFrameNumbers',                             'comment' : ''}
        table_from_ctp['0028-6112'] = {'en' : False, 'op' : '',        'name' : 'ContrastFrameAveraging',                       'comment' : ''}
        table_from_ctp['0028-6114'] = {'en' : False, 'op' : '',        'name' : 'MaskSubPixelShift',                            'comment' : ''}
        table_from_ctp['0028-6120'] = {'en' : False, 'op' : '',        'name' : 'TIDOffset',                                    'comment' : ''}
        table_from_ctp['0028-6190'] = {'en' : False, 'op' : '',        'name' : 'MaskOperationExplanation',                     'comment' : ''}
        table_from_ctp['0028-9001'] = {'en' : False, 'op' : '',        'name' : 'DataPointRows',                                'comment' : ''}
        table_from_ctp['0028-9002'] = {'en' : False, 'op' : '',        'name' : 'DataPointColumns',                             'comment' : ''}
        table_from_ctp['0028-9003'] = {'en' : False, 'op' : '',        'name' : 'SignalDomain',                                 'comment' : ''}
        table_from_ctp['0028-9099'] = {'en' : False, 'op' : '',        'name' : 'LargestMonochromePixelValue',                  'comment' : ''}
        table_from_ctp['0028-9108'] = {'en' : False, 'op' : '',        'name' : 'DataRepresentation',                           'comment' : ''}
        table_from_ctp['0028-9110'] = {'en' : False, 'op' : '',        'name' : 'PixelMatrixSeq',                               'comment' : ''}
        table_from_ctp['0028-9132'] = {'en' : False, 'op' : '',        'name' : 'FrameVOILUTSeq',                               'comment' : ''}
        table_from_ctp['0028-9145'] = {'en' : False, 'op' : '',        'name' : 'PixelValueTransformationSeq',                  'comment' : ''}
        table_from_ctp['0028-9235'] = {'en' : False, 'op' : '',        'name' : 'SignalDomainRows',                             'comment' : ''}
        if flag_keep_siemens_mr:
            table_from_ctp['0029'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensCSAHeader',                           'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
        table_from_ctp['0032-000a'] = {'en' : False, 'op' : '',        'name' : 'StudyStatusID',                                'comment' : ''}
        table_from_ctp['0032-000c'] = {'en' : False, 'op' : '',        'name' : 'StudyPriorityID',                              'comment' : ''}
        table_from_ctp['0032-0012'] = {'en' : True,  'op' : 'remove',  'name' : 'StudyIDIssuer',                                'comment' : ''}
        table_from_ctp['0032-0032'] = {'en' : True,  'op' : 'remove',  'name' : 'StudyVerifiedDate',                            'comment' : ''}
        table_from_ctp['0032-0033'] = {'en' : False, 'op' : '',        'name' : 'StudyVerifiedTime',                            'comment' : ''}
        table_from_ctp['0032-0034'] = {'en' : True,  'op' : 'remove',  'name' : 'StudyReadDate',                                'comment' : ''}
        table_from_ctp['0032-0035'] = {'en' : False, 'op' : '',        'name' : 'StudyReadTime',                                'comment' : ''}
        table_from_ctp['0032-1000'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStudyStartDate',                      'comment' : ''}
        table_from_ctp['0032-1001'] = {'en' : False, 'op' : '',        'name' : 'ScheduledStudyStartTime',                      'comment' : ''}
        table_from_ctp['0032-1010'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStudyStopDate',                       'comment' : ''}
        table_from_ctp['0032-1011'] = {'en' : False, 'op' : '',        'name' : 'ScheduledStudyStopTime',                       'comment' : ''}
        table_from_ctp['0032-1020'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStudyLocation',                       'comment' : ''}
        table_from_ctp['0032-1021'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStudyLocationAET',                    'comment' : ''}
        table_from_ctp['0032-1030'] = {'en' : True,  'op' : 'remove',  'name' : 'ReasonforStudy',                               'comment' : ''}
        table_from_ctp['0032-1032'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestingPhysician',                          'comment' : ''}
        table_from_ctp['0032-1033'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestingService',                            'comment' : ''}
        table_from_ctp['0032-1040'] = {'en' : True,  'op' : 'remove',  'name' : 'StudyArrivalDate',                             'comment' : ''}
        table_from_ctp['0032-1041'] = {'en' : False, 'op' : '',        'name' : 'StudyArrivalTime',                             'comment' : ''}
        table_from_ctp['0032-1050'] = {'en' : True,  'op' : 'remove',  'name' : 'StudyCompletionDate',                          'comment' : ''}
        table_from_ctp['0032-1051'] = {'en' : False, 'op' : '',        'name' : 'StudyCompletionTime',                          'comment' : ''}
        table_from_ctp['0032-1055'] = {'en' : False, 'op' : '',        'name' : 'StudyComponentStatusID',                       'comment' : ''}
        table_from_ctp['0032-1060'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestedProcedureDescription',                'comment' : ''}
        table_from_ctp['0032-1064'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestedProcedureCodeSeq',                    'comment' : ''}
        table_from_ctp['0032-1070'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestedContrastAgent',                       'comment' : ''}
        table_from_ctp['0032-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'StudyComments',                                'comment' : ''}
        table_from_ctp['0038-0004'] = {'en' : False, 'op' : '',        'name' : 'RefPatientAliasSeq',                           'comment' : ''}
        table_from_ctp['0038-0008'] = {'en' : False, 'op' : '',        'name' : 'VisitStatusID',                                'comment' : ''}
        table_from_ctp['0038-0010'] = {'en' : True,  'op' : 'remove',  'name' : 'AdmissionID',                                  'comment' : ''}
        table_from_ctp['0038-0011'] = {'en' : True,  'op' : 'remove',  'name' : 'IssuerOfAdmissionID',                          'comment' : ''}
        table_from_ctp['0038-0016'] = {'en' : False, 'op' : '',        'name' : 'RouteOfAdmissions',                            'comment' : ''}
        table_from_ctp['0038-001a'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledAdmissionDate',                       'comment' : ''}
        table_from_ctp['0038-001b'] = {'en' : False, 'op' : '',        'name' : 'ScheduledAdmissionTime',                       'comment' : ''}
        table_from_ctp['0038-001c'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledDischargeDate',                       'comment' : ''}
        table_from_ctp['0038-001d'] = {'en' : False, 'op' : '',        'name' : 'ScheduledDischargeTime',                       'comment' : ''}
        table_from_ctp['0038-001e'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledPatientInstitutionResidence',         'comment' : ''}
        table_from_ctp['0038-0020'] = {'en' : True,  'op' : 'remove',  'name' : 'AdmittingDate',                                'comment' : ''}
        table_from_ctp['0038-0021'] = {'en' : True,  'op' : 'remove',  'name' : 'AdmittingTime',                                'comment' : ''}
        table_from_ctp['0038-0030'] = {'en' : True,  'op' : 'remove',  'name' : 'DischargeDate',                                'comment' : ''}
        table_from_ctp['0038-0032'] = {'en' : False, 'op' : '',        'name' : 'DischargeTime',                                'comment' : ''}
        table_from_ctp['0038-0040'] = {'en' : True,  'op' : 'remove',  'name' : 'DischargeDiagnosisDescription',                'comment' : ''}
        table_from_ctp['0038-0044'] = {'en' : False, 'op' : '',        'name' : 'DischargeDiagnosisCodeSeq',                    'comment' : ''}
        table_from_ctp['0038-0050'] = {'en' : True,  'op' : 'remove',  'name' : 'SpecialNeeds',                                 'comment' : ''}
        table_from_ctp['0038-0060'] = {'en' : True,  'op' : 'remove',  'name' : 'ServiceEpisodeID',                             'comment' : ''}
        table_from_ctp['0038-0061'] = {'en' : True,  'op' : 'remove',  'name' : 'IssuerOfServiceEpisodeId',                     'comment' : ''}
        table_from_ctp['0038-0062'] = {'en' : True,  'op' : 'remove',  'name' : 'ServiceEpisodeDescription',                    'comment' : ''}
        table_from_ctp['0038-0300'] = {'en' : True,  'op' : 'remove',  'name' : 'CurrentPatientLocation',                       'comment' : ''}
        table_from_ctp['0038-0400'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientInstitutionResidence',                  'comment' : ''}
        table_from_ctp['0038-0500'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientState',                                 'comment' : ''}
        table_from_ctp['0038-1234'] = {'en' : True,  'op' : 'remove',  'name' : 'ReferencedPatientAliasSeq',                    'comment' : ''}
        table_from_ctp['0038-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'VisitComments',                                'comment' : ''}
        table_from_ctp['003a-0004'] = {'en' : False, 'op' : '',        'name' : 'WaveformOriginality',                          'comment' : ''}
        table_from_ctp['003a-0005'] = {'en' : False, 'op' : '',        'name' : 'NumberOfWaveformChannels',                     'comment' : ''}
        table_from_ctp['003a-0010'] = {'en' : False, 'op' : '',        'name' : 'NumberOfWaveformSamples',                      'comment' : ''}
        table_from_ctp['003a-001a'] = {'en' : False, 'op' : '',        'name' : 'SamplingFrequency',                            'comment' : ''}
        table_from_ctp['003a-0020'] = {'en' : False, 'op' : '',        'name' : 'MultiplexGroupLabel',                          'comment' : ''}
        table_from_ctp['003a-0200'] = {'en' : False, 'op' : '',        'name' : 'ChannelDefinitionSeq',                         'comment' : ''}
        table_from_ctp['003a-0202'] = {'en' : False, 'op' : '',        'name' : 'WaveformChannelNumber',                        'comment' : ''}
        table_from_ctp['003a-0203'] = {'en' : False, 'op' : '',        'name' : 'ChannelLabel',                                 'comment' : ''}
        table_from_ctp['003a-0205'] = {'en' : False, 'op' : '',        'name' : 'ChannelStatus',                                'comment' : ''}
        table_from_ctp['003a-0208'] = {'en' : False, 'op' : '',        'name' : 'ChannelSourceSeq',                             'comment' : ''}
        table_from_ctp['003a-0209'] = {'en' : False, 'op' : '',        'name' : 'ChannelSourceModifiersSeq',                    'comment' : ''}
        table_from_ctp['003a-020a'] = {'en' : False, 'op' : '',        'name' : 'SourceWaveformSeq',                            'comment' : ''}
        table_from_ctp['003a-020c'] = {'en' : False, 'op' : '',        'name' : 'ChannelDerivationDescription',                 'comment' : ''}
        table_from_ctp['003a-0210'] = {'en' : False, 'op' : '',        'name' : 'ChannelSensitivity',                           'comment' : ''}
        table_from_ctp['003a-0211'] = {'en' : False, 'op' : '',        'name' : 'ChannelSensitivityUnitsSeq',                   'comment' : ''}
        table_from_ctp['003a-0212'] = {'en' : False, 'op' : '',        'name' : 'ChannelSensitivityCorrectionFactor',           'comment' : ''}
        table_from_ctp['003a-0213'] = {'en' : False, 'op' : '',        'name' : 'ChannelBaseline',                              'comment' : ''}
        table_from_ctp['003a-0214'] = {'en' : False, 'op' : '',        'name' : 'ChannelTimeSkew',                              'comment' : ''}
        table_from_ctp['003a-0215'] = {'en' : False, 'op' : '',        'name' : 'ChannelSampleSkew',                            'comment' : ''}
        table_from_ctp['003a-0218'] = {'en' : False, 'op' : '',        'name' : 'ChannelOffset',                                'comment' : ''}
        table_from_ctp['003a-021a'] = {'en' : False, 'op' : '',        'name' : 'WaveformBitsStored',                           'comment' : ''}
        table_from_ctp['003a-0220'] = {'en' : False, 'op' : '',        'name' : 'FilterLowFrequency',                           'comment' : ''}
        table_from_ctp['003a-0221'] = {'en' : False, 'op' : '',        'name' : 'FilterHighFrequency',                          'comment' : ''}
        table_from_ctp['003a-0222'] = {'en' : False, 'op' : '',        'name' : 'NotchFilterFrequency',                         'comment' : ''}
        table_from_ctp['003a-0223'] = {'en' : False, 'op' : '',        'name' : 'NotchFilterBandwidth',                         'comment' : ''}
        table_from_ctp['0040-0001'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStationAET',                          'comment' : ''}
        table_from_ctp['0040-0002'] = {'en' : True,  'op' : 'remove',  'name' : 'SPSStartDate',                                 'comment' : ''}
        table_from_ctp['0040-0003'] = {'en' : False, 'op' : '',        'name' : 'SPSStartTime',                                 'comment' : ''}
        table_from_ctp['0040-0004'] = {'en' : True,  'op' : 'remove',  'name' : 'SPSEndDate',                                   'comment' : ''}
        table_from_ctp['0040-0005'] = {'en' : False, 'op' : '',        'name' : 'SPSEndTime',                                   'comment' : ''}
        table_from_ctp['0040-0006'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledPerformingPhysicianName',             'comment' : ''}
        table_from_ctp['0040-0007'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledProcedureStepDescription',            'comment' : ''}
        table_from_ctp['0040-0008'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledProtocolCodeSeq',                     'comment' : ''}
        table_from_ctp['0040-0009'] = {'en' : False, 'op' : '',        'name' : 'SPSID',                                        'comment' : ''}
        table_from_ctp['0040-000b'] = {'en' : True,  'op' : 'remove',  'name' : '',                                             'comment' : ''}
        table_from_ctp['0040-0010'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStationName',                         'comment' : ''}
        table_from_ctp['0040-0011'] = {'en' : True,  'op' : 'remove',  'name' : 'SPSLocation',                                  'comment' : ''}
        table_from_ctp['0040-0012'] = {'en' : True,  'op' : 'remove',  'name' : 'PreMedication',                                'comment' : ''}
        table_from_ctp['0040-0020'] = {'en' : False, 'op' : '',        'name' : 'SPSStatus',                                    'comment' : ''}
        table_from_ctp['0040-0100'] = {'en' : False, 'op' : '',        'name' : 'SPSSeq',                                       'comment' : ''}
        table_from_ctp['0040-0220'] = {'en' : False, 'op' : '',        'name' : 'RefNonImageCompositeSOPInstanceSeq',           'comment' : ''}
        table_from_ctp['0040-0241'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedStationAET',                          'comment' : ''}
        table_from_ctp['0040-0242'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedStationName',                         'comment' : ''}
        table_from_ctp['0040-0243'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedLocation',                            'comment' : ''}
        table_from_ctp['0040-0244'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepStartDate',              'comment' : ''}
        table_from_ctp['0040-0245'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepStartTime',              'comment' : ''}
        table_from_ctp['0040-0248'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedStationNameCodeSeq',                  'comment' : ''}
        table_from_ctp['0040-0250'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepEndDate',                'comment' : ''}
        table_from_ctp['0040-0251'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepEndTime',                'comment' : ''}
        table_from_ctp['0040-0252'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepStatus',                 'comment' : ''}
        table_from_ctp['0040-0253'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepID',                     'comment' : ''}
        table_from_ctp['0040-0254'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureStepDescription',            'comment' : ''}
        table_from_ctp['0040-0255'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProcedureTypeDescription',            'comment' : ''}
        table_from_ctp['0040-0260'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedProtocolCodeSeq',                     'comment' : ''}
        table_from_ctp['0040-0270'] = {'en' : False, 'op' : '',        'name' : 'ScheduledStepAttributesSeq',                   'comment' : ''}
        table_from_ctp['0040-0275'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestAttributesSeq',                         'comment' : ''}
        table_from_ctp['0040-0280'] = {'en' : True,  'op' : 'remove',  'name' : 'PPSComments',                                  'comment' : ''}
        table_from_ctp['0040-0281'] = {'en' : False, 'op' : '',        'name' : 'PPSDiscontinuationReasonCodeSeq',              'comment' : ''}
        table_from_ctp['0040-0293'] = {'en' : False, 'op' : '',        'name' : 'QuantitySeq',                                  'comment' : ''}
        table_from_ctp['0040-0294'] = {'en' : False, 'op' : '',        'name' : 'Quantity',                                     'comment' : ''}
        table_from_ctp['0040-0295'] = {'en' : False, 'op' : '',        'name' : 'MeasuringUnitsSeq',                            'comment' : ''}
        table_from_ctp['0040-0296'] = {'en' : False, 'op' : '',        'name' : 'BillingItemSeq',                               'comment' : ''}
        table_from_ctp['0040-0300'] = {'en' : False, 'op' : '',        'name' : 'TotalTimeOfFluoroscopy',                       'comment' : ''}
        table_from_ctp['0040-0301'] = {'en' : False, 'op' : '',        'name' : 'TotalNumberOfExposures',                       'comment' : ''}
        table_from_ctp['0040-0302'] = {'en' : False, 'op' : '',        'name' : 'EntranceDose',                                 'comment' : ''}
        table_from_ctp['0040-0303'] = {'en' : False, 'op' : '',        'name' : 'ExposedArea',                                  'comment' : ''}
        table_from_ctp['0040-0306'] = {'en' : False, 'op' : '',        'name' : 'DistanceSourceToEntrance',                     'comment' : ''}
        table_from_ctp['0040-0307'] = {'en' : False, 'op' : '',        'name' : 'DistanceSourceToSupport',                      'comment' : ''}
        table_from_ctp['0040-030e'] = {'en' : True,  'op' : 'remove',  'name' : 'RETIRED_ExposureDoseSequence',                 'comment' : 'Something embeds stuff here, maybe when loading another institutions pacs into our pacs?'}
        table_from_ctp['0040-0310'] = {'en' : False, 'op' : '',        'name' : 'CommentsOnRadiationDose',                      'comment' : ''}
        table_from_ctp['0040-0312'] = {'en' : False, 'op' : '',        'name' : 'XRayOutput',                                   'comment' : ''}
        table_from_ctp['0040-0314'] = {'en' : False, 'op' : '',        'name' : 'HalfValueLayer',                               'comment' : ''}
        table_from_ctp['0040-0316'] = {'en' : False, 'op' : '',        'name' : 'OrganDose',                                    'comment' : ''}
        table_from_ctp['0040-0318'] = {'en' : False, 'op' : '',        'name' : 'OrganExposed',                                 'comment' : ''}
        table_from_ctp['0040-0320'] = {'en' : False, 'op' : '',        'name' : 'BillingProcedureStepSeq',                      'comment' : ''}
        table_from_ctp['0040-0321'] = {'en' : False, 'op' : '',        'name' : 'FilmConsumptionSeq',                           'comment' : ''}
        table_from_ctp['0040-0324'] = {'en' : False, 'op' : '',        'name' : 'BillingSuppliesAndDevicesSeq',                 'comment' : ''}
        table_from_ctp['0040-0330'] = {'en' : False, 'op' : '',        'name' : 'RefProcedureStepSeq',                          'comment' : ''}
        table_from_ctp['0040-0340'] = {'en' : False, 'op' : '',        'name' : 'PerformedSeriesSeq',                           'comment' : ''}
        table_from_ctp['0040-0400'] = {'en' : False, 'op' : '',        'name' : 'SPSComments',                                  'comment' : ''}
        table_from_ctp['0040-050a'] = {'en' : False, 'op' : '',        'name' : 'SpecimenAccessionNumber',                      'comment' : ''}
        table_from_ctp['0040-0550'] = {'en' : False, 'op' : '',        'name' : 'SpecimenSeq',                                  'comment' : ''}
        table_from_ctp['0040-0551'] = {'en' : False, 'op' : '',        'name' : 'SpecimenIdentifier',                           'comment' : ''}
        table_from_ctp['0040-0555'] = {'en' : True, 'op' : 'emptyseq', 'name' : 'AcquisitionContextSequence',                   'comment' : 'Per Clunie, must exist but can be empty'}
        table_from_ctp['0040-0556'] = {'en' : False, 'op' : '',        'name' : 'AcquisitionContextDescription',                'comment' : ''}
        table_from_ctp['0040-059a'] = {'en' : False, 'op' : '',        'name' : 'SpecimenTypeCodeSeq',                          'comment' : ''}
        table_from_ctp['0040-06fa'] = {'en' : False, 'op' : '',        'name' : 'SlideIdentifier',                              'comment' : ''}
        table_from_ctp['0040-071a'] = {'en' : False, 'op' : '',        'name' : 'ImageCenterPointCoordinatesSeq',               'comment' : ''}
        table_from_ctp['0040-072a'] = {'en' : False, 'op' : '',        'name' : 'XOffsetInSlideCoordinateSystem',               'comment' : ''}
        table_from_ctp['0040-073a'] = {'en' : False, 'op' : '',        'name' : 'YOffsetInSlideCoordinateSystem',               'comment' : ''}
        table_from_ctp['0040-074a'] = {'en' : False, 'op' : '',        'name' : 'ZOffsetInSlideCoordinateSystem',               'comment' : ''}
        table_from_ctp['0040-08d8'] = {'en' : False, 'op' : '',        'name' : 'PixelSpacingSeq',                              'comment' : ''}
        table_from_ctp['0040-08da'] = {'en' : False, 'op' : '',        'name' : 'CoordinateSystemAxisCodeSeq',                  'comment' : ''}
        table_from_ctp['0040-08ea'] = {'en' : False, 'op' : '',        'name' : 'MeasurementUnitsCodeSeq',                      'comment' : ''}
        table_from_ctp['0040-1001'] = {'en' : True,  'op' : 'empty',   'name' : 'RequestedProcedureID',                         'comment' : ''}
        table_from_ctp['0040-1002'] = {'en' : False, 'op' : '',        'name' : 'ReasonForTheRequestedProcedure',               'comment' : ''}
        table_from_ctp['0040-1003'] = {'en' : False, 'op' : '',        'name' : 'RequestedProcedurePriority',                   'comment' : ''}
        table_from_ctp['0040-1004'] = {'en' : True,  'op' : 'remove',  'name' : 'PatientTransportArrangements',                 'comment' : ''}
        table_from_ctp['0040-1005'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestedProcedureLocation',                   'comment' : ''}
        table_from_ctp['0040-1008'] = {'en' : False, 'op' : '',        'name' : 'ConfidentialityCode',                          'comment' : ''}
        table_from_ctp['0040-1009'] = {'en' : False, 'op' : '',        'name' : 'ReportingPriority',                            'comment' : ''}
        table_from_ctp['0040-1010'] = {'en' : True,  'op' : 'remove',  'name' : 'NamesOfIntendedRecipientsOfResults',           'comment' : ''}
        table_from_ctp['0040-1011'] = {'en' : True,  'op' : 'remove',  'name' : 'IntendedRecipientsOfResultsIDSequence',        'comment' : ''}
        table_from_ctp['0040-1102'] = {'en' : True,  'op' : 'remove',  'name' : 'PersonAddress',                                'comment' : ''}
        table_from_ctp['0040-1103'] = {'en' : True,  'op' : 'remove',  'name' : 'PersonTelephoneNumbers',                       'comment' : ''}
        table_from_ctp['0040-1400'] = {'en' : True,  'op' : 'remove',  'name' : 'RequestedProcedureComments',                   'comment' : ''}
        table_from_ctp['0040-2001'] = {'en' : True,  'op' : 'remove',  'name' : 'ReasonForTheImagingServiceRequest',            'comment' : ''}
        table_from_ctp['0040-2004'] = {'en' : True,  'op' : 'remove',  'name' : 'IssueDateOfImagingServiceRequest',             'comment' : ''}
        table_from_ctp['0040-2005'] = {'en' : False, 'op' : '',        'name' : 'IssueTimeOfImagingServiceRequest',             'comment' : ''}
        table_from_ctp['0040-2008'] = {'en' : True,  'op' : 'remove',  'name' : 'OrderEnteredBy',                               'comment' : ''}
        table_from_ctp['0040-2009'] = {'en' : True,  'op' : 'remove',  'name' : 'OrderEntererLocation',                         'comment' : ''}
        table_from_ctp['0040-2010'] = {'en' : True,  'op' : 'remove',  'name' : 'OrderCallbackPhoneNumber',                     'comment' : ''}
        table_from_ctp['0040-2016'] = {'en' : True,  'op' : 'remove',  'name' : 'PlacerOrderNumber',                            'comment' : ''}
        table_from_ctp['0040-2017'] = {'en' : True,  'op' : 'remove',  'name' : 'FillerOrderNumber',                            'comment' : ''}
        table_from_ctp['0040-2400'] = {'en' : True,  'op' : 'remove',  'name' : 'ImagingServiceRequestComments',                'comment' : ''}
        table_from_ctp['0040-3001'] = {'en' : True,  'op' : 'remove',  'name' : 'ConfidentialityPatientData',                   'comment' : ''}
        table_from_ctp['0040-4023'] = {'en' : True,  'op' : 'remove',  'name' : 'RefGenPurposeSchedProcStepTransUID',           'comment' : ''}
        table_from_ctp['0040-4025'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStationNameCodeSeq',                  'comment' : ''}
        table_from_ctp['0040-4027'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledStationGeographicLocCodeSeq',         'comment' : ''}
        table_from_ctp['0040-4030'] = {'en' : True,  'op' : 'remove',  'name' : 'PerformedStationGeoLocCodeSeq',                'comment' : ''}
        table_from_ctp['0040-4034'] = {'en' : True,  'op' : 'remove',  'name' : 'ScheduledHumanPerformersSeq',                  'comment' : ''}
        table_from_ctp['0040-4035'] = {'en' : True,  'op' : 'remove',  'name' : 'ActualHumanPerformersSequence',                'comment' : ''}
        table_from_ctp['0040-4036'] = {'en' : True,  'op' : 'remove',  'name' : 'HumanPerformersOrganization',                  'comment' : ''}
        table_from_ctp['0040-4037'] = {'en' : True,  'op' : 'remove',  'name' : 'HumanPerformersName',                          'comment' : ''}
        table_from_ctp['0040-8302'] = {'en' : False, 'op' : '',        'name' : 'EntranceDoseInmGy',                            'comment' : ''}
        table_from_ctp['0040-9096'] = {'en' : False, 'op' : '',        'name' : 'RealWorldValueMappingSeq',                     'comment' : ''}
        table_from_ctp['0040-9210'] = {'en' : False, 'op' : '',        'name' : 'LUTLabel',                                     'comment' : ''}
        table_from_ctp['0040-9211'] = {'en' : False, 'op' : '',        'name' : 'RealWorldValueLUTLastValueMappedUS',           'comment' : ''}
        table_from_ctp['0040-9212'] = {'en' : False, 'op' : '',        'name' : 'RealWorldValueLUTData',                        'comment' : ''}
        table_from_ctp['0040-9216'] = {'en' : False, 'op' : '',        'name' : 'RealWorldValueLUTFirstValueMappedUS',          'comment' : ''}
        table_from_ctp['0040-9224'] = {'en' : False, 'op' : '',        'name' : 'RealWorldValueIntercept',                      'comment' : ''}
        table_from_ctp['0040-9225'] = {'en' : False, 'op' : '',        'name' : 'RealWorldValueSlope',                          'comment' : ''}
        table_from_ctp['0040-a010'] = {'en' : False, 'op' : '',        'name' : 'RelationshipType',                             'comment' : ''}
        table_from_ctp['0040-a027'] = {'en' : True,  'op' : 'remove',  'name' : 'VerifyingOrganization',                        'comment' : ''}
        table_from_ctp['0040-a030'] = {'en' : True,  'op' : 'remove',  'name' : 'VerificationDateTime',                         'comment' : ''}
        table_from_ctp['0040-a032'] = {'en' : True,  'op' : 'remove',  'name' : 'ObservationDateTime',                          'comment' : ''}
        table_from_ctp['0040-a040'] = {'en' : False, 'op' : '',        'name' : 'ValueType',                                    'comment' : ''}
        table_from_ctp['0040-a043'] = {'en' : False, 'op' : '',        'name' : 'ConceptNameCodeSeq',                           'comment' : ''}
        table_from_ctp['0040-a050'] = {'en' : False, 'op' : '',        'name' : 'ContinuityOfContent',                          'comment' : ''}
        table_from_ctp['0040-a073'] = {'en' : False, 'op' : '',        'name' : 'VerifyingObserverSeq',                         'comment' : ''}
        table_from_ctp['0040-a075'] = {'en' : True,  'op' : 'remove',  'name' : 'VerifyingObserverName',                        'comment' : ''}
        table_from_ctp['0040-a078'] = {'en' : True,  'op' : 'remove',  'name' : 'AuthorObserverSequence',                       'comment' : ''}
        table_from_ctp['0040-a07a'] = {'en' : True,  'op' : 'remove',  'name' : 'ParticipantSequence',                          'comment' : ''}
        table_from_ctp['0040-a07c'] = {'en' : True,  'op' : 'remove',  'name' : 'CustodialOrganizationSeq',                     'comment' : ''}
        table_from_ctp['0040-a088'] = {'en' : True,  'op' : 'remove',  'name' : 'VerifyingObserverIdentificationCodeSeq',       'comment' : ''}
        table_from_ctp['0040-a0b0'] = {'en' : False, 'op' : '',        'name' : 'RefWaveformChannels',                          'comment' : ''}
        table_from_ctp['0040-a120'] = {'en' : True,  'op' : 'remove',  'name' : 'DateTime',                                     'comment' : ''}
        table_from_ctp['0040-a121'] = {'en' : True,  'op' : 'remove',  'name' : 'Date',                                         'comment' : ''}
        table_from_ctp['0040-a122'] = {'en' : False, 'op' : '',        'name' : 'Time',                                         'comment' : ''}
        table_from_ctp['0040-a123'] = {'en' : True,  'op' : 'remove',  'name' : 'PersonName',                                   'comment' : ''}
        table_from_ctp['0040-a124'] = {'en' : True,  'op' : 'remove',  'name' : 'UID',                                          'comment' : ''}
        table_from_ctp['0040-a130'] = {'en' : False, 'op' : '',        'name' : 'TemporalRangeType',                            'comment' : ''}
        table_from_ctp['0040-a132'] = {'en' : False, 'op' : '',        'name' : 'RefSamplePositions',                           'comment' : ''}
        table_from_ctp['0040-a136'] = {'en' : False, 'op' : '',        'name' : 'RefFrameNumbers',                              'comment' : ''}
        table_from_ctp['0040-a138'] = {'en' : False, 'op' : '',        'name' : 'RefTimeOffsets',                               'comment' : ''}
        table_from_ctp['0040-a13a'] = {'en' : True,  'op' : 'remove',  'name' : 'RefDatetime',                                  'comment' : ''}
        table_from_ctp['0040-a160'] = {'en' : False, 'op' : '',        'name' : 'TextValue',                                    'comment' : ''}
        table_from_ctp['0040-a168'] = {'en' : False, 'op' : '',        'name' : 'ConceptCodeSeq',                               'comment' : ''}
        table_from_ctp['0040-a180'] = {'en' : False, 'op' : '',        'name' : 'AnnotationGroupNumber',                        'comment' : ''}
        table_from_ctp['0040-a195'] = {'en' : False, 'op' : '',        'name' : 'ModifierCodeSeq',                              'comment' : ''}
        table_from_ctp['0040-a300'] = {'en' : False, 'op' : '',        'name' : 'MeasuredValueSeq',                             'comment' : ''}
        table_from_ctp['0040-a30a'] = {'en' : False, 'op' : '',        'name' : 'NumericValue',                                 'comment' : ''}
        table_from_ctp['0040-a360'] = {'en' : False, 'op' : '',        'name' : 'PredecessorDocumentsSeq',                      'comment' : ''}
        table_from_ctp['0040-a370'] = {'en' : False, 'op' : '',        'name' : 'RefRequestSeq',                                'comment' : ''}
        table_from_ctp['0040-a372'] = {'en' : False, 'op' : '',        'name' : 'PerformedProcedureCodeSeq',                    'comment' : ''}
        table_from_ctp['0040-a375'] = {'en' : False, 'op' : '',        'name' : 'CurrentRequestedProcedureEvidenceSeq',         'comment' : ''}
        table_from_ctp['0040-a385'] = {'en' : False, 'op' : '',        'name' : 'PertinentOtherEvidenceSeq',                    'comment' : ''}
        table_from_ctp['0040-a491'] = {'en' : False, 'op' : '',        'name' : 'CompletionFlag',                               'comment' : ''}
        table_from_ctp['0040-a492'] = {'en' : False, 'op' : '',        'name' : 'CompletionFlagDescription',                    'comment' : ''}
        table_from_ctp['0040-a493'] = {'en' : False, 'op' : '',        'name' : 'VerificationFlag',                             'comment' : ''}
        table_from_ctp['0040-a504'] = {'en' : False, 'op' : '',        'name' : 'ContentTemplateSeq',                           'comment' : ''}
        table_from_ctp['0040-a525'] = {'en' : False, 'op' : '',        'name' : 'IdenticalDocumentsSeq',                        'comment' : ''}
        table_from_ctp['0040-a730'] = {'en' : True,  'op' : 'remove',  'name' : 'ContentSeq',                                   'comment' : ''}
        table_from_ctp['0040-b020'] = {'en' : False, 'op' : '',        'name' : 'AnnotationSeq',                                'comment' : ''}
        table_from_ctp['0040-db00'] = {'en' : False, 'op' : '',        'name' : 'TemplateIdentifier',                           'comment' : ''}
        table_from_ctp['0040-db06'] = {'en' : False, 'op' : '',        'name' : 'TemplateVersion',                              'comment' : ''}
        table_from_ctp['0040-db07'] = {'en' : False, 'op' : '',        'name' : 'TemplateLocalVersion',                         'comment' : ''}
        table_from_ctp['0040-db0b'] = {'en' : False, 'op' : '',        'name' : 'TemplateExtensionFlag',                        'comment' : ''}
        table_from_ctp['0040-db0c'] = {'en' : True,  'op' : 'remove',  'name' : 'TemplateExtensionOrganizationUID',             'comment' : ''}
        table_from_ctp['0040-db0d'] = {'en' : True,  'op' : 'remove',  'name' : 'TemplateExtensionCreatorUID',                  'comment' : ''}
        table_from_ctp['0040-db73'] = {'en' : False, 'op' : '',        'name' : 'RefContentItemIdentifier',                     'comment' : ''}
        if flag_keep_siemens_mr:
            table_from_ctp['0051'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensMRHeader',                            'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
        table_from_ctp['0060-3000'] = {'en' : True,  'op' : 'remove',  'name' : 'OverlayData',                                  'comment' : ''}
        table_from_ctp['0060-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'OverlayComments',                              'comment' : ''}
        table_from_ctp['0070-031a'] = {'en' : True,  'op' : 'remove',  'name' : 'FiducialUID',                                  'comment' : ''}
        if flag_keep_siemens_mr:
            table_from_ctp['0071'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensCSAHeader',                           'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
        table_from_ctp['0088-0140'] = {'en' : True,  'op' : 'remove',  'name' : 'StorageMediaFilesetUID',                       'comment' : ''}
        table_from_ctp['0088-0200'] = {'en' : True,  'op' : 'remove',  'name' : 'IconImageSequence',                            'comment' : ''}
        table_from_ctp['0088-0906'] = {'en' : True,  'op' : 'remove',  'name' : 'TopicSubject',                                 'comment' : ''}
        table_from_ctp['0088-0910'] = {'en' : True,  'op' : 'remove',  'name' : 'TopicAuthor',                                  'comment' : ''}
        table_from_ctp['0088-0912'] = {'en' : True,  'op' : 'remove',  'name' : 'TopicKeyWords',                                'comment' : ''}
        table_from_ctp['0400-0100'] = {'en' : True,  'op' : 'remove',  'name' : 'DigitalSignatureUID',                          'comment' : ''}
        table_from_ctp['0400-0561'] = {'en' : True,  'op' : 'remove',  'name' : 'OriginalAttributesSequence',                   'comment' : 'yet another PHI location snuck in by importing foreign DICOM'}
        table_from_ctp['2030-0020'] = {'en' : True,  'op' : 'remove',  'name' : 'TextString',                                   'comment' : ''}
        table_from_ctp['3006-0024'] = {'en' : True,  'op' : 'remove',  'name' : 'ReferencedFrameOfReferenceUID',                'comment' : ''}
        table_from_ctp['3006-00c2'] = {'en' : True,  'op' : 'remove',  'name' : 'RelatedFrameOfReferenceUID',                   'comment' : ''}
        table_from_ctp['300a-0013'] = {'en' : True,  'op' : 'remove',  'name' : 'DoseReferenceUID',                             'comment' : ''}
        table_from_ctp['4000-0010'] = {'en' : True,  'op' : 'remove',  'name' : 'Arbitrary',                                    'comment' : ''}
        table_from_ctp['4000-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'TextComments',                                 'comment' : ''}
        table_from_ctp['4008-0042'] = {'en' : True,  'op' : 'remove',  'name' : 'ResultsIDIssuer',                              'comment' : ''}
        table_from_ctp['4008-0102'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationRecorder',                       'comment' : ''}
        table_from_ctp['4008-010a'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationTranscriber',                    'comment' : ''}
        table_from_ctp['4008-010b'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationText',                           'comment' : ''}
        table_from_ctp['4008-010c'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationAuthor',                         'comment' : ''}
        table_from_ctp['4008-0111'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationApproverSequence',               'comment' : ''}
        table_from_ctp['4008-0114'] = {'en' : True,  'op' : 'remove',  'name' : 'PhysicianApprovingInterpretation',             'comment' : ''}
        table_from_ctp['4008-0115'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationDiagnosisDescription',           'comment' : ''}
        table_from_ctp['4008-0118'] = {'en' : True,  'op' : 'remove',  'name' : 'ResultsDistributionListSeq',                   'comment' : ''}
        table_from_ctp['4008-0119'] = {'en' : True,  'op' : 'remove',  'name' : 'DistributionName',                             'comment' : ''}
        table_from_ctp['4008-011a'] = {'en' : True,  'op' : 'remove',  'name' : 'DistributionAddress',                          'comment' : ''}
        table_from_ctp['4008-0202'] = {'en' : True,  'op' : 'remove',  'name' : 'InterpretationIdIssuer',                       'comment' : ''}
        table_from_ctp['4008-0300'] = {'en' : True,  'op' : 'remove',  'name' : 'Impressions',                                  'comment' : ''}
        table_from_ctp['4008-4000'] = {'en' : True,  'op' : 'remove',  'name' : 'ResultComments',                               'comment' : ''}
        table_from_ctp['50..']      = {'en' : True,  'op' : 'groupremovere', 'name' : 'Curves',                                 'comment' : 'Curve data.  Regex permitted in group spec.'}
        table_from_ctp['60..']      = {'en' : True,  'op' : 'groupremovere', 'name' : 'Overlays',                               'comment' : 'Overlays might have burned in PHI.  Regex permitted in group spec.'}
        if flag_hologic:
            table_from_ctp['7e01'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'HologicHeader',                            'comment' : 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
        if flag_keep_siemens_mr:
            table_from_ctp['7fdf'] = { 'en' : True,  'op' : 'groupkeep', 'name' : 'SiemensCSAHeader',                           'comment' : 'Siemens protocol stuff.  Does capture study date internally'}
        table_from_ctp['fffa-fffa'] = {'en' : True,  'op' : 'remove',  'name' : 'DigitalSignaturesSeq',                         'comment' : ''}
        table_from_ctp['fffc-fffc'] = {'en' : True,  'op' : 'remove',  'name' : 'DataSetTrailingPadding',                       'comment' : ''}

    tag_handling = { 'keep' : {}, 'remove' : {} }
    found_private_address = False
    found_private_groups = False
    for key_address, dict_address in table_from_ctp.items():
        if dict_address['en']:
            if dict_address['op'] not in tag_handling:
                tag_handling[dict_address['op']] = {}
            if dict_address['op'] == 'groupkeep':
                if int(key_address,16) % 2 == 1:
                    found_private_groups = True
            else:
                if dict_address['op'] != 'groupremovere':
                    address_group, address_element = key_address.split('-')
                    if int(address_group,16) % 2 == 1:
                        found_private_address = True
            tag_handling[dict_address['op']][key_address] = True

    tag_handling_list = { 'keep' : [], 'remove' : [] }
    for key_address, flag_address in tag_handling['keep'].items():
        tag_handling_list['keep'] += [key_address]
    for key_address, flag_address in tag_handling['remove'].items():
        tag_handling_list['remove'] += [key_address]
    if 'groupkeep' in tag_handling:
        tag_handling_list['groupkeep'] = []
        for key_address, flag_address in tag_handling['groupkeep'].items():
            tag_handling_list['groupkeep'] += [key_address]
    if 'groupremovere' in tag_handling:
        tag_handling_list['groupremovere'] = []
        for key_address, flag_address in tag_handling['groupremovere'].items():
            tag_handling_list['groupremovere'] += [key_address]

    tag_handling['KeepSomePrivate'] = found_private_groups or found_private_address

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev
   
    return {'status' : 0}, tag_handling, tag_handling_list

# ============================================================================
def check_split_2d_from_cview_tomo(orthanc_study_id, **kwargs):
    """ In the tomologic study, we separated 2D series from Tomo derived series"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    meta_series_data = json.loads(orthanc.RestApiGet('/studies/%s/series' % orthanc_study_id))

    # We need R/L CC, R/L MLO for 2D and C-View (others are extra)
    search_strings = [ 'r cc', 'l cc', 'r mlo', 'l mlo' ]
    counts = {'2d' : {}, 'cview': {}}
    for search_string in search_strings:
        for count in ['2d', 'cview']:
            counts[count][search_string] = 0

    for meta_series in meta_series_data:
        flag = {'cview' : false, 'non2d' : false }
        if 'SeriesDescription' in meta_series['MainDicomTags']:
            series_description = meta_series['MainDicomTags']['SeriesDescription'].lower()
            flag['cview'] = flag['cview'] or series_description.find('c-view') >= 0
            flag['non2d'] = flag['non2d'] or flag['cview']
            flag['non2d'] = flag['non2d'] or series_description.find('tomo') >= 0
            if flag['cview'] or (not flag['non2d']):
                for search_string in search_strings:
                    if series_description.find(search_string) >= 0:
                        if flag['cview']:
                            counts['cview'][search_string] += 1
                        else:
                            counts['2d'][search_string] += 1

    local_sum = {'2d' : 0, 'cview': 0}
    for type_str, count_dict in counts.items():
        for search_string, search_count in count_dict.items():
            local_sum[type_str] += search_count

    if (local_sum['2d'] < 4) or (local_sum['cview'] < 4):
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Incomplete number of either 2D or C-View', **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], json.dumps(counts, indent=3), **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return False
    else:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return True

# ============================================================================
def check_xref_modality(**kwargs):
    """Check for environmental variable defining xref modality"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3
    flag_xref_modality=False
    xref_modality=None
    if 'PYTHON_XREF_MODALITY' in os.environ:
        for modality in json.loads(orthanc.RestApiGet('/modalities')):
            if modality == os.environ['PYTHON_XREF_MODALITY']:
                flag_xref_modality = True
                xref_modality = modality
                break

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return flag_xref_modality, xref_modality

# ============================================================================
def confirm_or_create_lookup_table_sql(pg_connection=None, pg_cursor=None, **kwargs):
    """Confirm existence of our lookup table in the database and create if necessary"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':1, 'error_text':'confirm_or_create_lookup_table: Problem querying for patientid table'}

    row = pg_cursor.fetchone()
    if row is not None and int(row[0]) == 0:
        status = create_lookup_table_sql(pg_connection=pg_connection, 
                                         pg_cursor = pg_cursor, **kwargs)
        if status['status'] != 0:
            if flag_local_db:
                pg_connection.rollback()
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}
        
# ============================================================================
def connect_to_database(**kwargs):
    """Make connection to our postgres database"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Get the login parameters
    if 'PostgreSQL' in global_var['orthanc_configuration']:
        pg_username = global_var['orthanc_configuration']['PostgreSQL']['Username']
        pg_password = global_var['orthanc_configuration']['PostgreSQL']['Password']
        pg_host = global_var['orthanc_configuration']['PostgreSQL']['Host']
        pg_port = global_var['orthanc_configuration']['PostgreSQL']['Port']
    else:
        if 'ORTHANC__POSTGRESQL__USERNAME' not in os.environ or \
            'ORTHANC__POSTGRESQL__PASSWORD' not in os.environ or \
            'ORTHANC__POSTGRESQL__HOST' not in os.environ:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 3, 
                    'error_text': 'Environmental variables for postgres not declared'}
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':error_status, 
                'error_text':'connect_to_database: Problem connecting to database'}, None, None

    # Setup cursor
    error_status += 1
    try:
        pg_cursor = pg_connection.cursor()
    except:
        if pg_connection is not None:
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':error_status, 
                'error_text':'connect_to_database: Something went wrong with cursor creation'}, None, None

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status':0}, pg_connection, pg_cursor

# ============================================================================
def construct_patient_name(internal_number, 
                           patient_name_base_local=global_var['patient_name_base'], 
                           patient_name_id_char=global_var['patient_name_id_char'], **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    if patient_name_base_local is None:
        patient_name_base_local = get_patient_name_base(**kwargs)

    local_patient_name_id_char = patient_name_id_char

    patient_name = '%s^%s%06d^^^' % (patient_name_base_local, local_patient_name_id_char, internal_number)

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return patient_name
              
# ============================================================================
def create_lookup_table_sql(pg_connection=None, pg_cursor=None, **kwargs):
    """Create the lookup tables"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True 
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
                global_var['log_indent_level'] = log_indent_level_prev
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
                global_var['log_indent_level'] = log_indent_level_prev
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
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': code, 'error_text': 'create_lookup_table_sql: Problem creating table %s' % table_name}
        code += 1

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status' : 0}

# =======================================================
def email_message(subject, message_body, subtype='plain', alternates=None, cc=None, **kwargs):
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
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3
 
    if alternates is None:
        if 'PYTHON_MAIL_TO' not in os.environ or \
           'PYTHON_MAIL_ORIGIN' not in os.environ or \
           'PYTHON_MAIL_SERVER' not in os.environ:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0),**kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return{'status':1, 'error_text': 'Environmental variables for python mail not declared'}
        recipients = os.getenv('PYTHON_MAIL_TO').split(',')
    else:
        if 'PYTHON_MAIL_ORIGIN' not in os.environ or \
           'PYTHON_MAIL_SERVER' not in os.environ:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0),**kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0),**kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0),**kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':4, 'error_text':'email_message: Is the smtp down?'}
    s.send_message(msg)
    s.quit()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0),**kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status':0}

# =======================================================
def email_study_report(orthanc_study_id):
    """Generate email of study statistics"""
# -------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
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

    flag_anonymized = 'AnonymizedFrom' in meta_study

    flag_check_remote_aet = os.getenv('PYTHON_FLAG_CHECK_INCOMING_STUDIES_FOR_COMPLETENESS', default='false') == 'true' and not flag_anonymized
    if flag_check_remote_aet:
        remote_stats = get_metadata_from_remote_aet(orthanc_study_id, meta_study=meta_study)

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

    if flag_check_remote_aet:
        if remote_stats['RemoteNotOnLocal'] > 0:
            message_body += [' '*4 + '<p style="color:red"><em>ATTENTION!</em> Some series may NOT have transferred from the scanner.  See <a href="#NotOnLocal">notes below</a>!</p>']
 
    # Main study info
    message_body += [' '*4 + '<table border=1>']
    message_body += [' '*6 + '<tr><th>Item</th><th>Value</th></tr>']
    message_body += [' '*6 + '<tr><td>Study</td><td><a href="https://%s/%s/app/explorer.html#study?uuid=%s">%s</a></td></tr>' % (global_var['fqdn'], global_var['website'], orthanc_study_id,study_description)]
    if flag_anonymized:
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
    if flag_check_remote_aet:
        message_body += [' '*6 + '<tr><th>Series</th><th>Instances</th><th>Station</th><th>Anatomy</th><th>Description</th><th>Scanner</th><th>Comment</th></tr>']
    else:
        message_body += [' '*6 + '<tr><th>Series</th><th>Instances</th><th>Station</th><th>Anatomy</th><th>Description</th></tr>']
    series_data = {}
    for orthanc_series_id in meta_study['Series']:
        response_series = orthanc.RestApiGet('/series/%s' % orthanc_series_id)
        meta_series = json.loads(response_series)
        series_number = int(meta_series['MainDicomTags']['SeriesNumber'])
        for key in ['Instances', 'StationName', 'BodyPartExamined', 'SeriesDescription', 'SeriesInstanceUID']:
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
        if flag_check_remote_aet:
            series_instance_uid = series_data[series_number]['SeriesInstanceUID']
            if 'RemoteModality' in remote_stats['Series'][series_instance_uid]:
                color = 'lightgreen' if remote_stats['Series'][series_instance_uid]['remote'] else 'pink'
                line_of_text += '<td style="background-color:%s">%s</td>' % (color,remote_stats['Series'][series_instance_uid]['RemoteModality'])
                remote_modality = remote_stats['Series'][series_instance_uid]['RemoteModality']
                if remote_stats['RemoteModality'][remote_modality]['responsive']:
                    line_of_text += '<td></td>'
                else:
                    line_of_text += '<td style="background-color:pink">Unresponsive</td>'
            else:
                line_of_text += '<td style="background-color:pink">Unknown Origin</td><td></td>'

        line_of_text += '</tr>'
        message_body += [line_of_text]

    message_body += [' '*4 + '</table>']

    if flag_check_remote_aet and remote_stats['RemoteNotOnLocal'] > 0:
        email_subject = 'PHI Study Report (Missing Series) from %s' % aet
        message_body += [' '*4 + '<h2 style="color:red" id="NotOnLocal">Series on Scanner But Missing From This Orthanc</h2>']
        message_body += [' '*4 + '<table border=1>']
        message_body += [' '*6 + '<tr><th>Series</th><th>Description</th><th>Scanner</th></tr>']
        for series_instance_uid, dict_series in remote_stats['Series'].items():
            if not dict_series['local']:
                series_number = dict_series['number']
                series_desctription = dict_series['description']
                line_of_text = ' '*6 + '<tr>'
                line_of_text += '<td align="center">%s</td>' % dict_series['number']
                line_of_text += '<td align="center">%s</td>' % dict_series['description']
                line_of_text += '<td align="center">%s</td>' % dict_series['RemoteModality']
                line_of_text += '</tr>'
                message_body += [line_of_text]
        message_body += [' '*4 + '</table>']
    else:
        email_subject = 'PHI Study Report from %s' % aet

    message_body += [' '*2 + '</body>', '</html>']

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] = log_indent_level_prev

    kwargs = {'subtype' : 'html' }
    #return email_message(email_subject, '\n'.join( message_body), **kwargs)
    return auto_email(email_subject, '\n'.join( message_body), **kwargs)

# ============================================================================
def filter_and_delete_instances(orthanc_study_id, **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    counts = {    'series': { 'start' : 0, 'end' : 0, 'deleted' : 0 },
              'instances' : { 'start' : 0, 'end' : 0, 'deteled' : 0 }}
    flag_deleted = { 'series' : False, 'instances' : False }

    # Count the number of series
    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    meta_study = json.loads(response_study)
    counts['series']['start'] = len(meta_study['Series'])
  
    # Determine what instances to delete
    flag_by_instance = filter_what_instances_to_keep(orthanc_study_ids=[orthanc_study_id], **kwargs)

    # Delete instances
    counts['instances']['start'] = len(flag_by_instance)
    counts['instances']['end'] = len(flag_by_instance)
    for orthanc_instance_id, flag_keep in flag_by_instance.items():
        if not flag_keep:
            counts['instances']['end'] -= 1
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Prefilter is deleting %s' % orthanc_instance_id, **kwargs)
            orthanc.RestApiDelete('/instances/%s' % orthanc_instance_id)

    # Refresh study info after deletion
    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    meta_study = json.loads(response_study)
    counts['series']['end'] = len(meta_study['Series'])

    for type_str in ['series', 'instances']:
        flag_deleted[type_str] = counts[type_str]['start'] > counts[type_str]['end']
        counts[type_str]['deleted'] = counts[type_str]['start'] - counts[type_str]['end']

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return counts, flag_deleted

# ============================================================================
def filter_and_delete_series_by_modality(orthanc_study_id, **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    counts = { 'start' : 0, 'end' : 0, 'deleted' : 0 }
    flag_deleted = False

    # Count the number of series
    response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
    meta_study = json.loads(response_study)
    counts['start'] = len(meta_study['Series'])
    counts['end'] = len(meta_study['Series'])

    # Get environment
    modalities_allowed = os.getenv('PYTHON_ALLOWED_MODALITIES', default='').split(',')
    modalities_denied = os.getenv('PYTHON_DENIED_MODALITIES', default='').split(',')

    # Filter series
    for orthanc_series_id in meta_study['Series']:
        meta_series = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id))
        if 'Modalitty' in meta_series['MainDicomTags']:
            modality_series = meta_series['MainDicomTags']['Modality']
            flag_allowed = len(modalities_allowed) == 0
            for modality_allowed in modalities_allowed:
                flag_allowed = flag_allowed or modality_series == modality_allowed
            for modality_denied in modalities_denied:
                flag_allowed = flag_allowed and (modality_series != modality_denied)
            if not flag_allowed:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Deleting denied modality %s %s' % (modality_series, orthanc_series_id), **kwargs)
                orthanc.RestApiDelete('/series/%s' % orthanc_series_id)
                flag_deleted = True
                counts['end'] -= 1
                counts['deleted'] += 1 

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return counts, flag_deleted

# =======================================================
def filter_what_instances_to_keep(orthanc_study_ids=None, orthanc_series_ids=None, orthanc_instance_ids=None, **kwargs):
# -------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    instances_to_check = {}
    flag_by_instance = {}

    if orthanc_study_ids is not None:
        for orthanc_study_id in orthanc_study_ids:
            response_study = orthanc.RestApiGet('/studies/%s/instances' % orthanc_study_id)
            for meta_instance in json.loads(response_study):
                 instances_to_check[meta_instance['ID']] = True
            
    if orthanc_series_ids is not None:
        for orthanc_series_id in orthanc_series_ids:
            response_series = orthanc.RestApiGet('/series/%s' % orthanc_series_id)
            for orthanc_instance_id in json.loads(response_series)['Instances']:
                instances_to_check[orthanc_instance_id] = True

    if orthanc_instance_ids is not None:
        for orthanc_instance_id in orthanc_instance_ids:
            instances_to_check[orthanc_instance_id] = True

    re_original_primary = re.compile('.*ORIGINAL.PRIMARY.*')
    for orthanc_instance_id in list(instances_to_check.keys()):

        # Pull the meta data
        try:
            response_instance = orthanc.RestApiGet('/instances/%s/simplified-tags' % orthanc_instance_id)
        except:
            continue
        meta_instance = json.loads(response_instance)

        # By default we assume derived (for safety) unless proven otherwise by existing ImageType 
        flag_assume_original_primary = os.getenv('PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY', default='false') == 'true'
        flag_original_primary = os.getenv('PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY', default='false') == 'true'
        flag_primary = os.getenv('PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY', default='false') == 'true'
        if not flag_assume_original_primary: #Turn off in order to keep Derived/Secondaries
            if 'ImageType' in meta_instance:
                flag_original_primary = re_original_primary.match(meta_instance['ImageType']) is not None
                flag_primary = flag_primary or meta_instance['ImageType'].find('PRIMARY') >= 0
            else:
                if 'FrameType' in meta_instance:
                    flag_original_primary = re_original_primary.match(meta_instance['FrameType']) is not None
                    flag_primary = flag_primary or meta_instance['FrameType'].find('PRIMARY') >= 0
    
        #Exception for HIFU and Dynacad
        flag_dynacad = False
        #flag_dynacad = flag_dynacad or ('SeriesDescription' in meta_instance and meta_instance['SeriesDescription'].find('DCAD') >= 0)
        #flag_dynacad = flag_dynacad or ('0073,1003' in meta_instance and meta_instance['0073,1003'].find('DYNACAD') >= 0)
        
        #Checking for non-mammo images
        flag_screen_for_reports = os.getenv('PYTHON_FLAG_SCREEN_FOR_REPORTS',default='true') == 'true' #turn on to weed out reports
        flag_non_report = 'ImageType' in meta_instance
        if flag_screen_for_reports: #Test for unwanted mammo studies
            for field_type, field_items in {                                  'ImageType' : ['dose', 'screen', 'report', 'exam protocol'],
                                                                       'StudyDescription' : ['securview'],
                                                     'SecondaryCaptureDeviceManufacturer' : ['pacsgear', 'hipgrahics', 'hipgraphics', 'lexmark'],
                                            'SecondaryCaptureDeviceManufacturerModelName' : ['pacsscan', 'inspace'],
                                                                            'StationName' : ['rapid', 'sonosite'],
                                                                           'Manufacturer' : ['ischemaview'],
                                                                  'ManufacturerModelName' : ['securview', 'blackford'],
                                                                      'SeriesDescription' : ['screen *s[a-z]*er', 'dose report', 'screen snapshot', 
                                                                                             'no rpt', 'summary', 'vpct', 'history', 'rapid', 
                                                                                             'securview', 'patient protocol', 'phoenix', 
                                                                                             'carestream', 'req', 'report', 'blackford']}.items():
                if flag_non_report and field_type in meta_instance:
                    for field_item in field_items:
                        flag_non_report = flag_non_report and re.match('.*%s.*' % field_item, meta_instance[field_type], re.IGNORECASE) is None
                if not flag_non_report:
                    break

        #Consider both original and primary
        if (os.getenv('PYTHON_FLAG_MUST_BE_ORIGINAL', default='true') == 'true'):
           flag_by_instance[orthanc_instance_id] = flag_dynacad or (flag_original_primary and flag_non_report)
        else:
           flag_by_instance[orthanc_instance_id] = flag_dynacad or (flag_primary and flag_non_report)

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    if len(flag_by_instance) == 0:
        return None

    return flag_by_instance

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

    found = False
    i_row_match = None
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

    found = False
    i_row_match = None
    for i_row_temp, study_instance_uid_list in lookup_table['StudyInstanceUID'].items():
        i_row_match = i_row_temp
        if isinstance(study_instance_uid_list, list):
            found = study_instance_uid in study_instance_uid_list
        else:
            found = study_instance_uid == study_instance_uid_list
        if found:
            break

    return found, i_row_match

# ============================================================================
def get_internal_number(sql_pid, patient_id_modifier,
                        pg_connection=None, pg_cursor=None, **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev

            return status, None
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev

            return {'status':1, 'error_text': 'get_internal_number: Must provide both con and cur'}, None

    sql_query = "SELECT value FROM internalnumber WHERE pid=%s" 
    try:
        pg_cursor.execute(sql_query, (sql_pid,))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev

        return {'status':1, 'error_text':'get_internal_number: Problem querying for patientid table'}, None

    if pg_cursor.rowcount > 0:
        row = pg_cursor.fetchone()
        internal_number = int(row[0])
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev

        return {'status': 0}, internal_number
    else:

        internal_number = None
        internal_number_new = None
        internal_number_type = os.getenv('PYTHON_INTERNAL_NUMBER_TYPE', default='random')

        while internal_number is None:

            if internal_number_type == 'random':
                internal_number_new = random.randrange(1,999999)
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
                internal_number = int(sql_pid)
                break

            if internal_number_new > 999999:
                pg_connection.rollback()
                if flag_local_db:
                    pg_cursor.close()
                    pg_connection.close()
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev

                return {'status': 4, 'error_text': 'get_internal_number: Internal number overrun'}, None

            sql_query = "SELECT count(*) FROM internalnumber WHERE value=%s"
            try:
                pg_cursor.execute(sql_query, (internal_number_new,))
            except:
                pg_connection.rollback()
                if flag_local_db:
                    pg_cursor.close()
                    pg_connection.close()
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status':2, 'error_text':'get_internal_number: querying new internal number'}, None
            row = pg_cursor.fetchone()
            if row is not None and int(row[0]) == 0:
                internal_number = int(internal_number_new)
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
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 3, 'error_text': 'get_internal_number: Problem saving the internal number'}, None
        pg_connection.commit()

    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, internal_number
 
# ============================================================================
def get_internal_numbers_by_patient_id(patient_id,
                                       pg_connection=None, pg_cursor=None, **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    internal_numbers = []

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, internal_numbers
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'get_internal_numbers_by_patient_id: Must provide both con and cur'}, internal_numbers

    sql_query = "SELECT value FROM internalnumber WHERE pid IN (SELECT pid FROM patientid WHERE value=%s)"
    try:
        pg_cursor.execute(sql_query, (patient_id,))
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev

        return {'status':1, 'error_text':'get_internal_numbers_by_patient_id: Problem querying for patientid table'}, internal_numbers
    row = pg_cursor.fetchone()
    while row is not None:
        internal_numbers += [row[0]]
        row = pg_cursor.fetchone()

    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, internal_numbers
 
# ============================================================================
def get_metadata_from_remote_aet(orthanc_study_id, meta_study=None):
    """Determine if RemoteAET exists and query it about the current study.
       Return meta data gathered from remote AET"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3

    output = {}

    if meta_study is None:
        response_study = orthanc.RestApiGet('/studies/%s' % orthanc_study_id)
        meta_study = json.loads(response_study)

    study_instance_uid = meta_study['MainDicomTags']['StudyInstanceUID']

    # Map the modalities
    response_modalities = orthanc.RestApiGet('/modalities')
    modality_aet_map = {}
    for modality_name in json.loads(response_modalities):
        meta_modality = json.loads(orthanc.RestApiGet('/modalities/%s/configuration' % modality_name))
        modality_aet_map[meta_modality['AET']] = modality_name
    modality_store_to_query = json.loads(os.getenv('PYTHON_MAP_SENDING_TO_QUERY', default='{}'))

    # Check remote for matching series
    output['RemoteModality'] = {}
    output['Series'] = {}
    output['LocalOnRemote'] = 0
    output['RemoteNotOnLocal'] = 0
    for orthanc_series_id in meta_study['Series']:

        response_series = orthanc.RestApiGet('/series/%s' % orthanc_series_id)
        meta_series = json.loads(response_series)
        series_instance_uid = meta_series['MainDicomTags']['SeriesInstanceUID']
        response_series = orthanc.RestApiGet('/series/%s/metadata' % orthanc_series_id)
        meta_series = json.loads(response_series)
        if series_instance_uid not in output['Series']:
            output['Series'][series_instance_uid] = {'local' : True, 'remote' : False}
        remote_modality = None
        if 'RemoteAET' in meta_series:
            response_remote_modality = orthanc.RestApiGet('/series/%s/metadata/RemoteAET' % orthanc_series_id)
            if len(response_remote_modality.strip()) > 0:
                remote_aet = response_remote_modality.strip().decode('utf-8')
                remote_modality = modality_aet_map[remote_aet] if remote_aet in modality_aet_map else None
                if remote_modality in modality_store_to_query:
                    remote_modality = modality_store_to_query[remote_modality]
                if remote_modality is not None and remote_modality not in output['RemoteModality']:
                    output['RemoteModality'][remote_modality] = {}
                    try:
                        response_echo = orthanc.RestApiPost('/modalities/%s/echo' % remote_modality, json.dumps({'Timeout' : 10}))
                        output['RemoteModality'][remote_modality]['responsive'] = True
                    except:
                        output['RemoteModality'][remote_modality]['responsive'] = False
                
        if remote_modality is not None:
            output['Series'][series_instance_uid]['RemoteModality'] = remote_modality
            if not output['RemoteModality'][remote_modality]['responsive']:
                output['Series'][series_instance_uid]['RemoteModalityResponsive'] = False
            else:
                query_dicom = {'StudyInstanceUID' : study_instance_uid, 
                               'SeriesInstanceUID' : series_instance_uid}
                query_series = {'Level' : 'Series',
                                'Query' : query_dicom}
                response_query_series = orthanc.RestApiPost('/modalities/%s/query' % remote_modality, json.dumps(query_series))
                remote_found = False
                meta_query_series = json.loads(response_query_series) if len(response_query_series.strip()) > 0 else {}
                if 'ID' in meta_query_series:
                    response_query_id = orthanc.RestApiGet('/queries/' + meta_query_series['ID'])
                    if len(response_query_id.strip()) > 0:
                        meta_query_id = json.loads(response_query_id)
                        if meta_query_id[0] == "answers":
                            response_query_id_answer = orthanc.RestApiGet('/queries/' + meta_query_series['ID'] + '/answers')
                            if len(response_query_id_answer.strip()) > 0:
                                meta_query_id_answer = json.loads(response_query_id_answer)
                                if meta_query_id_answer[0] == "0":
                                    response_query_id_answer_zero = orthanc.RestApiGet('/queries/' + meta_query_series['ID'] + '/answers/0')
                                    if len(response_query_id_answer_zero.strip()) > 0:
                                        meta_query_id_answer_zero = json.loads(response_query_id_answer_zero)
                                        if meta_query_id_answer_zero[0] == "content":
                                            response_content = orthanc.RestApiGet('/queries/' + meta_query_series['ID'] + '/answers/0/content')
                                            if len(response_content.strip()) > 0:
                                                remote_found = True
                output['Series'][series_instance_uid]['remote'] = remote_found
                output['LocalOnRemote'] += 1

    # Since RemoteAET is stored at the series or lower level, only after querying series can we now query at the study level
    for remote_modality, remote_dict in output['RemoteModality'].items():
        if remote_dict['responsive']:
            query_series = {'Level': 'Series', 
                            'Query': {'StudyInstanceUID': study_instance_uid,
                                      'SeriesNumber' : '*', 'SeriesDescription' : '*'}}
            response_query_series = orthanc.RestApiPost('/modalities/%s/query' % remote_modality, json.dumps(query_series))
            meta_query_series = json.loads(response_query_series) if len(response_query_series.strip()) > 0 else {}
            if 'ID' in meta_query_series:
                response_answer_series = orthanc.RestApiGet('%s/answers' % meta_query_series['Path'])
                meta_answer_series = json.loads(response_answer_series) if len(response_answer_series.strip()) > 0 else []
                for answer_id_series in meta_answer_series:
                    response_answer_id_series = orthanc.RestApiGet('%s/answers/%s' % (meta_query_series['Path'],answer_id_series))
                    meta_answer_id_series = json.loads(response_answer_id_series) if len(response_answer_id_series.strip()) > 0 else {}
                    if 'content' in meta_answer_id_series:
                        response_answer_content_series = orthanc.RestApiGet('%s/answers/%s/content' % (meta_query_series['Path'],answer_id_series))
                        meta_answer_content_series = json.loads(response_answer_content_series) if len(response_answer_content_series.strip()) > 0 else {}
                        series_number = meta_answer_content_series[u'0020,0011']['Value'] if u'0020,0011' in meta_answer_content_series else ''
                        series_description = meta_answer_content_series[u'0008,103e']['Value'] if u'0008,103e' in meta_answer_content_series else ''
                        series_instance_uid = meta_answer_content_series[u'0020,000e']['Value']
                        if series_instance_uid not in output['Series'] and series_description.lower().find('phoenix') < 0:
                            output['Series'][series_instance_uid] = {'local' : False, 'remote' : True, 
                                                                     'number' : series_number, 'description' : series_description}
                            output['Series'][series_instance_uid]['RemoteModality'] = remote_modality
                            output['Series'][series_instance_uid]['RemoteModalityResponsive'] = True
                            output['RemoteNotOnLocal'] += 1
        
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] = log_indent_level_prev
                
    return output

# ============================================================================
def get_patient_ids(orthanc_study_id=None,
                    meta_study=None,
                    patient_id_modifier='', **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    if orthanc_study_id is None and meta_study is None:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 1, 'error_text': 'Insufficient inputs to get_patient_ids'}, None
    elif meta_study is None:
        meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))

    # Scan the usual places
    patient_id_search = {'main': ['PatientID'], 'alternate':['OtherPatientIDs', 'RETIRED_OtherPatientIDs']}
    patient_id = {}
    for patient_id_type, patient_id_list in patient_id_search.items():
        patient_id[patient_id_type] = {}
        for patient_id_string in patient_id_list:
            if patient_id_string in meta_study['PatientMainDicomTags'] and len(meta_study['PatientMainDicomTags'][patient_id_string].strip()) > 0:
                patient_id_temp = '%s%s' % (meta_study['PatientMainDicomTags'][patient_id_string].strip(), patient_id_modifier)
                patient_id[patient_id_type][patient_id_temp] = True
    # Old style sequence
    if 'OtherPatientIDsSequence' in meta_study['PatientMainDicomTags']:
        for other_patient_id_dict in meta_study['PatientMainDicomTags']['OtherPatientIDsSequence']:
            if 'PatientID' in other_patient_id_dict and len(other_patient_id_dict['PatientID'].strip()) > 0:
                patient_id_temp = '%s%s' % (other_patient_id_dict['PatientID'].strip(),patient_id_modifier)
                patient_id['alternate'][patient_id_temp] = True

    # Now pull an image to get at other patient ids
    orthanc_instance_id = json.loads(orthanc.RestApiGet('/studies/%s/instances' % meta_study['ID']))[0]['ID']
    meta_instance = json.loads(orthanc.RestApiGet('/instances/%s/tags?simplify' % orthanc_instance_id))
    for patient_id_type, patient_id_list in patient_id_search.items():
        patient_id[patient_id_type] = {}
        for patient_id_string in patient_id_list:
            if patient_id_string in meta_instance and len(meta_instance[patient_id_string].strip()) > 0:
                patient_id_temp = '%s%s' % (meta_instance[patient_id_string].strip(), patient_id_modifier)
                patient_id[patient_id_type][patient_id_temp] = True
    # Old style sequence
    if 'OtherPatientIDsSequence' in meta_instance:
        for other_patient_id_dict in meta_instance['OtherPatientIDsSequence']:
            if 'PatientID' in other_patient_id_dict and len(other_patient_id_dict['PatientID'].strip()) > 0:
                patient_id_temp = '%s%s' % (other_patient_id_dict['PatientID'].strip(),patient_id_modifier)
                patient_id['alternate'][patient_id_temp] = True

    patient_ids = {}
    patient_ids_count = 0
    patient_ids_dict = {}
    for patient_id_type in ['main', 'alternate']:
        for patient_id_temp, dumby in patient_id[patient_id_type].items():
            if patient_id_temp not in patient_ids_dict:
                patient_ids_count += 1
                patient_ids[patient_ids_count] = patient_id_temp
                patient_ids_dict[patient_id_temp] = True

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status' : 0}, patient_ids

# ============================================================================
def get_patient_name_base(**kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    if global_var['patient_name_base'] is None:
        meta_system = json.loads(orthanc.RestApiGet('/system'))
        global_var['patient_name_base'] = meta_system['Name']

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return global_var['patient_name_base']

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
def irb_label_regex_map(irb_label, extra=''):
    """Map the irb_label (from a study's label list) to associated irb parameters"""
# ----------------------------------------------------------------------------

    global global_var
    irb_label_standard = None
    description = None
    patient_name_base = None
    for irb_standard, irb_dict in global_var['irb_label_regex_map'].items():
        res = re.match(irb_dict['label_re'], irb_label, re.IGNORECASE)
        if res is not None:
            if irb_standard == 'other':
                patient_name_base = res.group(1)
                description = irb_dict['description']
                irb_label_standard = irb_label
            else:
                patient_name_base = irb_dict['name_base']
                description = irb_dict['description']
                irb_label_standard = irb_standard
            break
    if patient_name_base is None:
        meta_system = json.loads(orthanc.RestApiGet('/system'))
        patient_name_base = ''
        extra = meta_system['Name']
        description = 'Default Orthanc name base'
        irb_label_standard = "irbdefault"

    return {'patient_name_base' : patient_name_base, 'extra' : extra, 'irb_standard' : irb_label_standard, 'description' : description}
   
# ============================================================================
def load_lookup_table(file_lookup, make_backup=False, **kwargs):
    """Parse the lookup table.  Make backup if directed."""
# ----------------------------------------------------------------------------

    global global_var
    lookup_table = {}
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    if not os.path.exists(file_lookup):
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status': 0}, lookup_table

    if not global_var['flag']['beautiful_soup']:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':1, 'error_text':'load_lookup_table: No Beautiful soup'}, lookup_table

    try:
        with open(file_lookup, 'r') as lun:
            lookup_text = lun.read()
    except: 
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':2, 'error_text':'load_lookup_table: Problem reading lookup'}, lookup_table

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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':3, 'error_text':'load_lookup_table: No head found'}, lookup_table

    try:
        table = soup.find('table')
    except AttributeError as e:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'No tables found, exiting', **kwargs)
        sys.exit(1)
    
    try:
        rows = table.find_all('tr')
    except AttributeError as e:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'No table rows found, exiting', **kwargs)
        sys.exit(2)
    
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

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status':0}, lookup_table

# ============================================================================
def load_phi_to_anon_map(pg_connection=None, pg_cursor = None, **kwargs):
    """Query the postgres database for phi to anon maps"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'load_phi_to_anon_map: Must provide both con and cur'}, None, None, None

    # Confirm our lookup tables
    status = confirm_or_create_lookup_table_sql(pg_connection=pg_connection, pg_cursor=pg_cursor, **kwargs)
    if status['status'] != 0:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
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
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
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

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, patient_map, patient_reverse_map, flag_siuid_to_anon

# ============================================================================
def load_shift_epoch_from_db(sql_pid, pg_connection=None, pg_cursor = None, **kwargs):
    """Query the postgres database for phi to anon maps"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'load_shift_epoch_from_db: Must provide both con and cur'}, None

    # Confirm our lookup tables
    status = confirm_or_create_lookup_table_sql(pg_connection=pg_connection, pg_cursor=pg_cursor, **kwargs)
    if status['status'] != 0:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status, None

    # Execute query
    sql_query = "SELECT value FROM shiftepoch WHERE pid=%s"
    try:
        pg_cursor.execute(sql_query, (sql_pid,))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':1, 'error_text':'load_shift_epoch_from_db: Problem querying for shiftepoch table'}, None

    if pg_cursor.rowcount > 0:
        row = pg_cursor.fetchone()
        shift_epoch = int(row[0])
    else:
        shift_epoch = None

    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, shift_epoch
 
# ============================================================================
def log_message(log_bitflag, log_indent_level, message_text, **kwargs):
# ----------------------------------------------------------------------------

    global global_var

    log_message_prefix = '%s: ' % kwargs['log_message_prefix'] if 'log_message_prefix' in kwargs else ''

    # Bit 1 reserved for LogWarning
    if (log_bitflag & 1) == 1:
        message_full = log_message_prefix + ' ' * log_indent_level + message_text
        orthanc.LogWarning(message_full)

    # User log
    if (log_bitflag & 2) == 2 and 'log_user' in kwargs:
        message_full = log_message_prefix + datetime.datetime.now().strftime('(%m/%d %H:%M:%S)') + ' ' * log_indent_level + message_text
        log_user = kwargs['log_user']
        if log_user not in global_var['log_user']:
            global_var['log_user'][log_user] = []
        global_var['log_user'][log_user] += [message_full]

# ============================================================================
def map_uid_old_to_new(orthanc_study_id_new, flag_remap_sop_instance_uid=True, flag_remap_kept_uid = True, **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    uid_map = {}
    uid_type = {}

    # Cycle through anonymized versions to set up one-to-one maps
    # First at the study level
    meta_study_new = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_new))
    study_instance_uid_new = meta_study_new['MainDicomTags']['StudyInstanceUID']

    orthanc_study_id_mod = meta_study_new['AnonymizedFrom']
    meta_study_mod = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_mod))
    study_instance_uid_mod = meta_study_mod['MainDicomTags']['StudyInstanceUID']

    orthanc_study_id_old = meta_study_mod['ModifiedFrom']
    meta_study_old = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id_old))
    study_instance_uid_old = meta_study_old['MainDicomTags']['StudyInstanceUID']

    # Initialize map
    uid_map[study_instance_uid_old] = study_instance_uid_new
    uid_type[study_instance_uid_old] = 'StudyInstanceUID'
    for orthanc_series_id_new in meta_study_new['Series']:

        # Now series
        meta_series_new = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id_new))
        series_instance_uid_new = meta_series_new['MainDicomTags']['SeriesInstanceUID']

        orthanc_series_id_mod = meta_series_new['AnonymizedFrom']
        meta_series_mod = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id_mod))
        series_instance_uid_mod = meta_series_mod['MainDicomTags']['SeriesInstanceUID']

        orthanc_series_id_old = meta_series_mod['ModifiedFrom']
        meta_series_old = json.loads(orthanc.RestApiGet('/series/%s' % orthanc_series_id_old))
        series_instance_uid_old = meta_series_old['MainDicomTags']['SeriesInstanceUID']

        uid_map[series_instance_uid_old] = series_instance_uid_new
        uid_type[series_instance_uid_old] = 'SeriesInstanceUID'

        for orthanc_instance_id_new in meta_series_new['Instances']:
            # Now instances 
            meta_instance_new = json.loads(orthanc.RestApiGet('/instances/%s' % orthanc_instance_id_new))
            sop_instance_uid_new = meta_instance_new['MainDicomTags']['SOPInstanceUID']
            orthanc_instance_id_mod = meta_instance_new['AnonymizedFrom'] 
            try:
                meta_instance_mod = json.loads(orthanc.RestApiGet('/instances/%s' % orthanc_instance_id_mod))
                sop_instance_uid_mod = meta_instance_mod['MainDicomTags']['SOPInstanceUID']
                orthanc_instance_id_old = meta_instance_mod['ModifiedFrom']  if 'ModifiedFrom' in meta_instance_mod else None
                if orthanc_instance_id_old is not None: 
                    meta_instance_old = json.loads(orthanc.RestApiGet('/instances/%s' % orthanc_instance_id_old))
                    sop_instance_uid_old = meta_instance_old['MainDicomTags']['SOPInstanceUID']
                    uid_map[sop_instance_uid_old] = sop_instance_uid_new
                    uid_type[sop_instance_uid_old] = 'SOPInstanceUID'
                    # Delete the Modified intermediate
                    orthanc.RestApiDelete('/instances/%s' % orthanc_instance_id_mod)
            except:
               pass 

            if flag_remap_sop_instance_uid:
                sop_instance_uid_remap = orthanc.RestApiGet('/tools/generate-uid?level=instance').decode('utf-8')
                uid_map[sop_instance_uid_new] = sop_instance_uid_remap
                uid_type[sop_instance_uid_new] = 'SOPInstanceUID'

    # Now check for non-modified UID
    if flag_remap_kept_uid and len(global_var['kept_uid']) > 0:
        for kept_uid_val, kept_uid_type in global_var['kept_uid'].items():

            # We really only care if it does not exist
            if kept_uid_val not in uid_map:

                if kept_uid_type['Name'].find('StudyInstanceUID') >= 0 or kept_uid_type['Name'].find('FrameOfReferenceUID') >= 0:
                    study_instance_uid_new = orthanc.RestApiGet('/tools/generate-uid?level=study').decode('utf-8')
                    uid_map[kept_uid_val] =  study_instance_uid_new
                    uid_type[kept_uid_val] = kept_uid_type['Name']

                if kept_uid_type['Name'].find('SeriesInstanceUID') >= 0:
                    series_instance_uid_new = orthanc.RestApiGet('/tools/generate-uid?level=series').decode('utf-8')
                    uid_map[kept_uid_val] =  series_instance_uid_new
                    uid_type[kept_uid_val] = kept_uid_type['Name']

                if kept_uid_type['Name'].find('SOPInstanceUID') >= 0:
                    sop_instance_uid_remap = orthanc.RestApiGet('/tools/generate-uid?level=instance').decode('utf-8')
                    uid_map[kept_uid_val] = sop_instance_uid_remap
                    uid_type[kept_uid_val] = kept_uid_type['Name']

                if kept_uid_type['Name'].find('SOPClassUID') >= 0 or kept_uid_type['Name'].find('CodingScheme') >= 0: # we keep these
                    uid_map[kept_uid_val] = kept_uid_val
                    uid_type[kept_uid_val] = kept_uid_type['Name']

                # Generic catch all will be a study uid
                if kept_uid_val not in uid_map:
                    study_instance_uid_new = orthanc.RestApiGet('/tools/generate-uid?level=study').decode('utf-8')
                    uid_map[kept_uid_val] = study_instance_uid_new
                    uid_type[kept_uid_val] = kept_uid_type['Name']

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return uid_map, uid_type

# ============================================================================
def on_orthanc(pg_connection=None, pg_cursor=None, **kwargs):
    """Create a dict of what is on Orthanc currently"""
# ----------------------------------------------------------------------------

    global global_var
    python_verbose_local = False
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect to the database
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_connection is not None:
                pg_connection.close()
            if python_verbose_local:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None
    else:
        if pg_connection is None or pg_cursor is None:
            if python_verbose_local:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'on_orthanc:Must provide both con and cur'}, None

    # Confirm our lookup tables
    status = confirm_or_create_lookup_table_sql(pg_connection=pg_connection, pg_cursor=pg_cursor, **kwargs)
    if status['status'] != 0:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if python_verbose_local:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status, None

    # Collect orthanc patientids
    if python_verbose_local:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Assembling all patient ids', **kwargs)
    orthanc_patient_ids = json.loads(orthanc.RestApiGet('/patients'))
    n_patients = len(orthanc_patient_ids)

    # Misc parameters
    flag_split_screen_from_diagnostic = os.getenv('PYTHON_FLAG_SPLIT_SCREEN_DIAG', default='false') == 'true'
    flag_every_accession_a_patient = os.getenv('PYTHON_FLAG_EVERY_ACCESSION_A_PATIENT', default='false') == 'true'
    meta_system = json.loads(orthanc.RestApiGet('/system'))

    # Assemble dict
    if python_verbose_local:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Assembling now_on_orthanc dict', **kwargs)
    now_on_orthanc = {}
    for dict_str in ['ByPatientID', 'StudyInstanceUID2PatientID', 'PatientID2oPatientID', 'StudyUID2oStudyUID']:
        now_on_orthanc[dict_str] = {}
    if python_verbose_local:
        global_var['log_indent_level'] += 3
    i_patient = 0
    n_patients = len(orthanc_patient_ids)
    for orthanc_patient_id in orthanc_patient_ids:
        i_patient += 1
        if python_verbose_local:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Patient %d of %d: %s' % (i_patient, n_patients, orthanc_patient_id), **kwargs)
        row_of_data = {}
        meta_patient = json.loads(orthanc.RestApiGet('/patients/%s' % orthanc_patient_id))
        if 'PatientName' in meta_patient['MainDicomTags'] and len(meta_patient['MainDicomTags']['PatientName'].strip()) > 0:
            row_of_data['PatientName'] = meta_patient['MainDicomTags']['PatientName'].strip()
        else:
            row_of_data['PatientName'] = ''
        patient_id = meta_patient['MainDicomTags']['PatientID']
        patient_id_temp = meta_patient['MainDicomTags']['PatientID']
        sql_query = "SELECT value FROM patientid WHERE pid IN (SELECT parent_pid FROM patientid WHERE value = %s)"
        if python_verbose_local:
            log_message(log_message_bitflag, global_var['log_indent_level']+3,'Querying sql', **kwargs)
        try:
            pg_cursor.execute(sql_query, (patient_id_temp,))
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if python_verbose_local:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 2, 'error_text' : 'on_orthanc:Problem querying pid'}, None
        if python_verbose_local:
            log_message(log_message_bitflag, global_var['log_indent_level']+3,'Examining results', **kwargs)
        row = pg_cursor.fetchone()
        while row is not None:
            patient_id = row[0]
            row = pg_cursor.fetchone()
        if python_verbose_local:
            log_message(log_message_bitflag, global_var['log_indent_level']+3,'Patient ID selected', **kwargs)
        for dict_str in ['StudyDate', 'AccessionNumber', 'StudyInstanceUID']:
            row_of_data[dict_str] = []
        if python_verbose_local:
            log_message(log_message_bitflag, global_var['log_indent_level']+3,'Querying studies', **kwargs)
        meta_studies = json.loads(orthanc.RestApiGet('/patients/%s/studies' % orthanc_patient_id))
        for meta_study in meta_studies:
            orthanc_study_id = meta_study['ID']
            if python_verbose_local:
                log_message(log_message_bitflag, global_var['log_indent_level']+6,'Processing study %s' % orthanc_study_id, **kwargs)
            patient_id_modifier = ''
            if flag_split_screen_from_diagnostic and row_of_data['PatientName'].lower().find(meta_system['Name'].lower()) < 0:
                patient_id_modifier = set_screen_or_diagnostic(orthanc_study_id, **kwargs)
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

    if log_message_bitflag:
        global_var['log_indent_level'] -= 3

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, now_on_orthanc

# ============================================================================
def recursive_find_uid_to_keep(parent, level_in=global_var['max_recurse_depth'], kept_uid={}, top_level_tag_to_keep = {}, parent_key=None):
    """
    PURPOSE: Tunnel down orthanc instance meta data cataloging 
                 UID for processing.
    INPUT:   parent - table/string, points to current parent structure
             level_in - int, default 20, max level of depth considered
             kept_uid - dict, later calls will insert this into the recursion
             top_level_tag_to_keep - dict, later calls insert this
    OUTPUT:  level_out - integer, current depth
             kept_uid, top_level_tag_to_keep - ongoing results
    HISTORY: 20 Apr 2023, John.Roberts@hsc.utah.edu
             Dept Radis, UofU, SLC Utah
             Converted from original Lua
    """
# ----------------------------------------------------------------------------

    type_dict = type({})
    type_list = type([])
    level_out = level_in - 1
    if level_in < 1:
        return level_out, kept_uid, top_level_tag_to_keep, parent_key
    parent_type = type(parent)
    if parent_type not in [type_list, type_dict]:
        return level_out, kept_uid, top_level_tag_to_keep, parent_key
    if parent_type == type_list:
        for child in parent:
            level_out, kept_uid, top_level_tag_to_keep, parent_key = recursive_find_uid_to_keep(child, level_in-1, kept_uid, top_level_tag_to_keep, parent_key)
            if level_out < 0:
                break
        return level_out, kept_uid, top_level_tag_to_keep, parent_key
    if parent_type == type_dict:
        for key, child in parent.items():
            if 'Name' in child and 'Value' in child:
                if type(child['Value']) in [type_dict, type_list] and level_in == global_var['max_recurse_depth']:
                    parent_key = key
                if child['Name'].find('UID') > 0: 
                    kept_uid[child['Value']] = {}
                    kept_uid[child['Value']]['Numeric'] = key
                    kept_uid[child['Value']]['Name'] = child['Name']
                    if level_in < global_var['max_recurse_depth']:
                        top_level_tag_to_keep[parent_key] = True
                    if level_in == global_var['max_recurse_depth'] and child['Name'] not in ['StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID']:
                        top_level_tag_to_keep[key] = True
            level_out, kept_uid, top_level_tag_to_keep, parent_key = \
                recursive_find_uid_to_keep(child['Value'], level_in-1, kept_uid, top_level_tag_to_keep, parent_key)
            if type(child['Value']) in [type_dict, type_list] and level_in == global_var['max_recurse_depth']:
                parent_key = None
            if level_out < 0:
                break
        return level_out, kept_uid, top_level_tag_to_keep, parent_key

# ============================================================================
def recursive_replace_uid(parent, level_entry=None):
# ----------------------------------------------------------------------------

    global global_var 
    log_message_bitflag = python_verbose_logwarning

    type_dict = type({})
    type_list = type([])
    level_in = level_entry if level_entry is not None else global_var['max_recurse_depth']
    level_out = level_in - 1
    if level_entry is None:
        global_var['address_constructor'] = []
        global_var['address_list'] = {}
    if level_in < 1:
         return {}, level_out
    parent_type = type(parent)
    element = {}
    if parent_type not in [type_dict, type_list]:
        return element, level_out
    if 'Value' in parent:
        if type(parent['Value']) == type_list:
            for k in range(len(parent['Value'])):
                child = parent['Value'][k]
                global_var['address_constructor'] += ['%s[%d]' % (parent['Name'],k)]
                value, level_out = recursive_replace_uid(child, level_in-1)
                if level_out < 0:
                    break 
                if value is not None and len(value) > 0:
                    element[k] = value
                global_var['address_constructor'].pop()
        else:
            if parent['Name'].find('UID') >= 0:
                global_var['address_constructor'] += [parent['Name']]
                uid_new = parent['Value']
                while uid_new in global_var['uid_map']:
                    if uid_new == global_var['uid_map'][uid_new]:
                        break
                    uid_new = global_var['uid_map'][uid_new]
                address_entry = ''
                n_address_stub = len(global_var['address_constructor'])
                for k in range(n_address_stub):
                    address_stub = global_var['address_constructor'][k]
                    if k < (n_address_stub-1):
                        address_entry = address_entry + address_stub + '.'
                    else:
                        address_entry = address_entry + address_stub
                global_var['address_list'][address_entry] = uid_new
                parent['Value'] = uid_new
                global_var['address_constructor'].pop()
            return parent['Value'], level_out
    else:
        if parent_type == type_dict:
            for key, child in parent.items():
                value, level_out = recursive_replace_uid(child, level_in-1)
                if level_out < 0:
                    break
                if value is not None and len(value) > 0:
                    element[key] = value
        elif parent_type == type_list:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Should not reach this point\n%s' % json.dumps(parent,indent=3))

    return element, level_out

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
def reset_patient_name_base():
# ----------------------------------------------------------------------------
    global global_var
    global_var['patient_name_base'] = None

# ============================================================================
def save_patient_ids_anon_to_db(sql_pid, orthanc_study_id=None, 
                                meta_study = None,
                                pg_connection=None, pg_cursor=None, **kwargs):
    """
    PURPOSE: Store (anonymized) orthanc_study_id patient_id_anon
    INPUT:   sql_pid - string, associated patientid pid
             orthanc_study_id - string, Orthanc study id of anon study
             meta_study - dict, alternatively, from /studies/orthanc_study_id
             pg_connection, pg_cursor - postgress handles
    OUTPUT:  status (dict) - status of result
             {'status' : 0 success, >0 some error,
              'error_text' : some text if error}
    HISTORY: 20 Apr 2023, John.Roberts@hsc.utah.edu
             Dept Radis, UofU, SLC Utah
             Converted from original Lua
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Get the Study info
    if orthanc_study_id is None and meta_study is None:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 1, 'error_text': 'Insufficient inputs to get_patient_ids'}
    elif meta_study is None:
        meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))
    patient_id_anon = meta_study['PatientMainDicomTags']['PatientID']

    # Connect if necessary
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':2, 'error_text': 'save_patient_ids_anon_to_db: Must provide both con and cur'}

    # Confirm lookup table sql
    status = confirm_or_create_lookup_table_sql(pg_connection, pg_cursor, **kwargs)
    if status['status'] != 0:
        if pg_cursor is not None:
            pg_cursor.close()
        if pg_connection is not None:
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status

    # Insert into database
    sql_statement = "INSERT INTO patientid_anon (value,pid) VALUES(%s,%s)"
    try:
        pg_cursor.execute(sql_statement,(patient_id_anon,sql_pid))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':1, 'error_text':'save_patient_id_anon problem inserting'}

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}

# ============================================================================
def save_patient_ids_to_db(orthanc_study_id=None, 
                           meta_study = None,
                           patient_id_modifier='',
                           pg_connection=None, pg_cursor=None, **kwargs):
    """
    PURPOSE: Store/recall patient ID info to/from database
    INPUT:   orthanc_study_id - string, Orthanc study id used to pull info
             meta_study - dict, alternatively, from /studies/orthanc_study_id
             patient_id_modifier - string
             pg_connection, pg_cursor - postgress handles
    OUTPUT:  status (dict) - status of result
             {'status' : 0 success, >0 some error,
              'error_text' : some text if error}
             flag_new_patient_id - boolean
             sql_pid_unique - new pid in database
             patient_id_anon - assigned internal number
    HISTORY: 18 Apr 2023, John.Roberts@hsc.utah.edu
             Dept Radis, UofU, SLC Utah
             Converted from original Lua
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Get the Study info
    if orthanc_study_id is None and meta_study is None:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 1, 'error_text': 'Insufficient inputs to get_patient_ids'}, None, None, None
    elif meta_study is None:
        meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))

    # Connect if necessary
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':2, 'error_text': 'save_patient_ids_to_db: Must provide both con and cur'}, None, None, None

    # Confirm lookup table sql
    status = confirm_or_create_lookup_table_sql(pg_connection, pg_cursor, **kwargs)
    if status['status'] != 0:
        if pg_cursor is not None:
            pg_cursor.close()
        if pg_connection is not None:
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status, None, None, None

    # Gather initial patient ids
    patient_ids = {}
    status, patient_ids_local = get_patient_ids(meta_study=meta_study, 
                                                patient_id_modifier=patient_id_modifier, **kwargs)
    if status['status'] != 0:
        if pg_cursor is not None:
            pg_cursor.close()
        if pg_connection is not None:
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status, None, None, None
    patient_ids['dicom'] = patient_ids_local

    # Query database for matches to dicom PatientID
    patient_ids['pid'] = {}
    patient_ids['map'] = {}
    j_patient_id = 0
    for i_patient_id, patient_id_local in patient_ids['dicom'].items():
        k_patient_id = 0
        sql_query = "SELECT pid, parent_pid " + \
                    "FROM patientid " + \
                    "WHERE value=%s"
        try:
            pg_cursor.execute(sql_query, (patient_id_local,))
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 3, 'error_text' : 'save_patient_ids_to_db:Problem querying pid, parent_pid'}, None, None, None
        patient_ids['map'][patient_id_local] = {}
        row = pg_cursor.fetchone()
        while row is not None:
            j_patient_id += 1
            k_patient_id += 1
            pid = row[0]
            parent_pid = row[1]
            row = pg_cursor.fetchone()
            if parent_pid is not None:
                patient_ids['pid'][j_patient_id] = parent_pid
            else:
                patient_ids['pid'][j_patient_id] = pid
            patient_ids['map'][k_patient_id] = patient_ids['pid'][j_patient_id]

    # Confirm that there can only be one
    sql_pid_unique = {}
    flag_new_patient_id = len(patient_ids['pid']) == 0
    if not flag_new_patient_id:
        check = {}
        j_pid = 0
        for i_pid, sql_pid_local in patient_ids['pid'].items():
            if sql_pid_local not in check:
                j_pid += 1
                sql_pid_unique[j_pid] = sql_pid_local
                check[sql_pid_local] = True
        if len(sql_pid_unique) != 1:
            error_text = 'Non unique pid: %s' % ','.join(list(check.values())) if len(sql_pid_unique) > 1 else 'Missing pid'
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            status = {'status' : 2, 'error_text' : error_text}
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], error_text, **kwargs)
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None

    # Handle any new PatientIDs that match a previous one
    if not flag_new_patient_id:
        for i_patient_id, patient_id_local in patient_ids['dicom'].items():
            if patient_id_local not in patient_ids['map']:
                sql_statement  = "INSERT INTO patientid " + \
                                 "(value, parent_pid) " + \
                                 "VALUES(%s,%s)"
                try:
                    pg_cursor.execute(sql_statement, (patient_id_local,sql_pid_unique[1]))
                except:
                    pg_connection.rollback()
                    if flag_local_db:
                        pg_cursor.close()
                        pg_connection.close()
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                        global_var['log_indent_level'] = log_indent_level_prev
                    return {'status': 4, 'error_text': 'Problem inserting secondary patient id'}, None, None, None
                patient_ids['map'][patient_id_local][1] = sql_pid_unique[1]
                if len(patient_ids['map'][patient_id_local]) > 1:
                    for j_pid in range(2,len(patient_ids['map'][patient_id_local])+1):
                        del patient_ids['map'][patient_id_local][j_pid]
        pg_connection.commit()
    # Should only be here if this is a brand new patient
    else:
        flag_first_loop = True
        for i_patient_id, patient_id_local in patient_ids['dicom'].items():
            if not flag_first_loop:
                sql_statement = "INSERT INTO patientid " + \
                                "(value, parent_pid) " + \
                                "VALUES(%s, %s)"
                try:
                    pg_cursor.execute(sql_statement, (patient_id_local,sql_pid_unique[1]))
                except:
                    pg_connection.rollback()
                    if flag_local_db:
                        pg_cursor.close()
                        pg_connection.close()
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                        global_var['log_indent_level'] = log_indent_level_prev
                    return {'status': 5, 'error_text': 'Problem inserting secondary patient id'}, None, None, None
            else:
                sql_statement = "INSERT INTO patientid (value) VALUES(%s)"
                try:
                    pg_cursor.execute(sql_statement, (patient_id_local,))
                except:
                    pg_connection.rollback()
                    if flag_local_db:
                        pg_cursor.close()
                        pg_connection.close()
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                        global_var['log_indent_level'] = log_indent_level_prev
                    return {'status': 6, 'error_text': 'Problem inserting secondary patient id'}, None, None, None
                sql_query = "SELECT pid FROM patientid WHERE value=%s"
                try:
                    pg_cursor.execute(sql_query, (patient_id_local,))
                except:
                    pg_connection.rollback()
                    if flag_local_db:
                        pg_cursor.close()
                        pg_connection.close()
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                        global_var['log_indent_level'] = log_indent_level_prev
                    return {'status': 7, 'error_text': 'Problem inserting secondary patient id'}, None, None, None
                row = pg_cursor.fetchone()
                patient_ids['map'][patient_id_local][1] = row[0]
                sql_pid_unique[1] = row[0] 
            flag_first_loop = False
        pg_connection.commit()
        
    # Look for anonymized IDS for this sql_pid
    sql_query = "SELECT value FROM patientid_anon WHERE pid=%s"
    try:
        pg_cursor.execute(sql_query, (sql_pid_unique[1],))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status': 8, 'error_text': 'Problem selecting from patientid_anon'}, None, None, None
    row = pg_cursor.fetchone()
    patient_id_anon = row[0] if row is not None else None
    
    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, flag_new_patient_id, sql_pid_unique[1], patient_id_anon

# ============================================================================
def save_patient_name_anon_to_db(patient_name_anon, sql_siuid,
                                 pg_connection=None, pg_cursor=None, **kwargs):
    """
    PURPOSE: Store (anonymized) orthanc_study_id patient_name_anon
    INPUT:   patient_name_anon - string, anonymized name
             sql_siuid - string, associated siuid from studyinstanceuid table
             pg_connection, pg_cursor - postgress handles
    OUTPUT:  status (dict) - status of result
             {'status' : 0 success, >0 some error,
              'error_text' : some text if error}
    HISTORY: 20 Apr 2023, John.Roberts@hsc.utah.edu
             Dept Radis, UofU, SLC Utah
             Converted from original Lua
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect if necessary
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'save_patient_name_anon_to_db: Must provide both con and cur'}

    # Confirm lookup table sql
    status = confirm_or_create_lookup_table_sql(pg_connection, pg_cursor, **kwargs)
    if status['status'] != 0:
        if pg_cursor is not None:
            pg_cursor.close()
        if pg_connection is not None:
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status

    # Check for the table
    sql_query = "SELECT table_name " + \
                "FROM information_schema.tables " + \
                "WHERE table_name='siuid2patientname_anon'"
    pg_cursor.execute(sql_query)
    if pg_cursor.rowcount == 0:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Tried to insert patientname anon into nonexistent siuid2patientname_anon', **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 0, 'error_text' : 'siuid2patientname_anon does not exist'}

    # Insert into database
    sql_statement = "INSERT INTO siuid2patientname_anon (patientname_anon, timestamp, siuid) VALUES(%s,%s,%s)"
    try:
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pg_cursor.execute(sql_statement,(patient_name_anon,datetime_str,sql_siuid))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':2, 'error_text':'save_patient_name_anon problem inserting'}

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}

# ============================================================================
def save_shift_epoch_to_db(sql_pid, shift_epoch,
                           pg_connection=None, pg_cursor=None, **kwargs):
    """
    PURPOSE: Store shift epoch to the database
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Connect if necessary
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'shave_shift_epoch_to_db: Must provide both con and cur'}

    # Insert 
    sql_statement = "INSERT INTO shiftepoch (value,pid) VALUES(%s,%s)"
    try:
        pg_cursor.execute(sql_statement,(shift_epoch,sql_pid))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':1, 'error_text':'save_shift_epoch_to_db problem inserting'}

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}

# ============================================================================
def save_study_instance_uid_anon_to_db(orthanc_study_id, sql_siuid,
                                       pg_connection=None, pg_cursor=None, **kwargs):
    """
    PURPOSE: Store study anon instance uid to database
    INPUT:   orthanc_study_id - string, Orthanc study id of anon study
             sql_siuid - corresponding siuid from phi studyinstanceuid table
             pg_connection, pg_cursor - postgress handles
    OUTPUT:  status (dict) - status of result
                {'status' : 0 success, >0 some error,
                 'error_text' : some text if error}
    HISTORY: 20 Apr 2023, John.Roberts@hsc.utah.edu
             Dept Radis, UofU, SLC Utah
             Converted from original Lua
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Pull the study data
    meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))
    study_instance_uid_anon = meta_study['MainDicomTags']['StudyInstanceUID']

    # Connect if necessary
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'save_siuid_anon: Must provide both con and cur'}, None, None, None

    # Insert 
    sql_statement = "INSERT INTO studyinstanceuid_anon (value,siuid) VALUES(%s,%s)"
    try:
        pg_cursor.execute(sql_statement,(study_instance_uid_anon,sql_siuid))
    except:
        pg_connection.rollback()
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status':1, 'error_text':'save_siuid_anon problem inserting'}

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}

# ============================================================================
def save_study_instance_uid_to_db(orthanc_study_id, sql_pid, study_instance_uid_modifier='',
                                  pg_connection=None, pg_cursor=None, **kwargs):
    """
    PURPOSE: Store/recall study instance uid to/from database
    INPUT:   orthanc_study_id - string, Orthanc study id used to pull info
             sql_pid - integer, the database pid corresponding to the patientid
             study_instance_uid_modifier - string, optional modifier for creating different
                child studies
             pg_connection, pg_cursor - postgress handles
    OUTPUT:  status (dict) - status of result
                {'status' : 0 success, >0 some error,
                 'error_text' : some text if error}
             flag_new_study_instance_uid - bool, whether this is a new study
             sql_siuid - the table id corresponding to the study instance uid
             study_instance_uid_anon - string, if previously anonymized, the study instance uid assigned to the anonymous data
    HISTORY: 19 Apr 2023, John.Roberts@hsc.utah.edu
             Dept Radis, UofU, SLC Utah
             Converted from original Lua
    """
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    # Pull the study data
    meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % orthanc_study_id))
    study_instance_uid = meta_study['MainDicomTags']['StudyInstanceUID']
    if len(study_instance_uid_modifier.strip()) > 0:
        study_instance_uid += study_instance_uid_modifier

    # Connect if necessary
    flag_local_db = False
    if pg_connection is None and pg_cursor is None:
        status, pg_connection, pg_cursor = connect_to_database(**kwargs)
        flag_local_db = True
        if status['status'] != 0:
            if pg_cursor is not None:
                pg_cursor.close()
            if pg_connection is not None:
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return status, None, None, None
    else:
        if pg_connection is None or pg_cursor is None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status':1, 'error_text': 'save_siuid: Must provide both con and cur'}, None, None, None

    # Check to see if in database
    sql_query = "SELECT pid,siuid FROM studyinstanceuid WHERE value=%s" 
    try:
        pg_cursor.execute(sql_query, (study_instance_uid,))
    except:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status': 2, 'error_text' : 'save_study_instance_uid_to_db:Problem querying siuid'}, None, None, None
    row = pg_cursor.fetchone()
    n_rows = 0
    sql_siuid = None
    while row is not None:
        pid_local = row[0]
        sql_siuid = row[1]
        if pid_local != sql_pid:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 3, 'error_text' : 'Mismatching PID associated with siuid'}, None, None, None
        n_rows += 1
        row = pg_cursor.fetchone()
    if n_rows > 1:
        if flag_local_db:
            pg_cursor.close()
            pg_connection.close()
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return {'status' : 4, 'error_text': 'More than one match in db for siuid'}, None, None, None

    # Check for anonymized studies
    flag_new_study_instance_uid = sql_siuid is None
    study_instance_uid_anon = None
    if sql_siuid is not None:
        sql_query = "SELECT value FROM studyinstanceuid_anon WHERE siuid = %s"
        try:
            pg_cursor.execute(sql_query, (sql_siuid,))
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 5, 'error_text' : 'save_study_instance_uid_to_db:Problem querying anon siuid'}, None, None, None
        row = pg_cursor.fetchone()
        n_rows = 0
        while row is not None:
            study_instance_uid_anon = row[0]
            n_rows += 1
            row = pg_cursor.fetchone()
        if n_rows > 1:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status' : 6, 'error_text': 'More than one anon siuid per phi siuid'}, None, None, None
    else:
        sql_statement = "INSERT INTO studyinstanceuid (value,pid) VALUES(%s,%s)"
        try:
            pg_cursor.execute(sql_statement, (study_instance_uid, sql_pid))
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 7, 'error_text' : 'Problem inserting new siuid'}, None, None, None
        sql_query = "SELECT siuid FROM studyinstanceuid WHERE value=%s"
        try:
            pg_cursor.execute(sql_query, (study_instance_uid,))
        except:
            if flag_local_db:
                pg_cursor.close()
                pg_connection.close()
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                global_var['log_indent_level'] = log_indent_level_prev
            return {'status': 8, 'error_text' : 'Problem querying new siuid'}, None, None, None
        row = pg_cursor.fetchone()
        sql_siuid = row[0]

    pg_connection.commit()
    if flag_local_db:
        pg_cursor.close()
        pg_connection.close()

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, flag_new_study_instance_uid, sql_siuid, study_instance_uid_anon

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

# ============================================================================
def set_patient_name_base(patient_name_base_in, **kwargs):
# ----------------------------------------------------------------------------
    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Old patient name base: %s' % global_var['patient_name_base'], **kwargs)

    global_var['patient_name_base'] = patient_name_base_in

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'New patient name base: %s' % patient_name_base_in, **kwargs)
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

# =======================================================
def set_screen_or_diagnostic(orthanc_study_id, **kwargs):
    """Used only in very specific Winkler/Hologic studies"""
# -------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    flag_screening = False
    meta_instances = json.loads(orthanc.RestApiGet('/studies/%s/instances' % orthanc_study_id))
    dicom_field_bases = ['Study', 'Series', 'PerformedProcedureStep', 'RequestedProcedure']
    for meta_instance in meta_instances:
        orthanc_instance_id = meta_instance['ID']
        meta_instance = json.loads(orthanc.RestApiGet('/instances/%s/simplified-tags' % orthanc_instance_id))
        for dicom_field_base in dicom_field_bases:
            description_field = '%s%s' % (dicom_field_base, 'Description')
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

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return patient_id_modifier
           
# ============================================================================
def shift_date_time_patage_of_instances(meta_instances, shift_epoch, replace_root, **kwargs):
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    type_dict = type({})
    type_list = type([])

    dicom_field_bases = [ 'Study', 'Series', 'Acquisition', 
                          'Content', 'InstanceCreation',
                          'PerformedProcedureStepStart' ]
    date_time_fields = [ 'AcquisitionDateTime' ]
    date_time_fields_radio = [ 'RadiopharmaceuticalStartDateTime', 'RadiopharmaceuticalStopDateTime' ]
    date_time_fields_frame = [ 'FrameAcquisitionDateTime', 'FrameReferenceDateTime' ]
    orthanc_instance_ids_new = []
    n_instances = len(meta_instances)
    ten_percent = n_instances // 10
    
    # Weed out instances that will be held back
    orthanc_instance_ids = []
    for meta_instance in meta_instances:
        orthanc_instance_ids += [meta_instance['ID']]
    flag_by_instance = filter_what_instances_to_keep(orthanc_instance_ids=orthanc_instance_ids, **kwargs)

    i = 0
    m_instance = max(len(flag_by_instance) // 10, 5)
    for orthanc_instance_id, flag_send_to_remote in flag_by_instance.items():

        # Show progress
        i = i + 1
        if log_message_bitflag and i % m_instance == 0:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Progress %d of %d' % (i,n_instances), **kwargs)

        # Assemble the base replacment dict
        replace_dict = {}
        for replace_root_key, replace_root_val in replace_root.items():
            replace_dict[replace_root_key] = replace_root_val
        
        # Gather Dicom meta
        if flag_send_to_remote:
            dicom_tags = json.loads(orthanc.RestApiGet('/instances/%s/simplified-tags' % orthanc_instance_id))
        else:
            dicom_tags = {}
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Shift date will skip non orig/prim /instances/%s/simplified-tags' % orthanc_instance_id, **kwargs)

        # Loop through separate date/time tags looking for fields to update
        for dicom_field_base in dicom_field_bases:
            date_field = '%sDate' % dicom_field_base
            time_field = '%sTime' % dicom_field_base
            if date_field in dicom_tags and len(dicom_tags[date_field].strip()) > 0:
                if time_field in dicom_tags and len(dicom_tags[time_field].strip()) > 0:
                    date_string_new, time_string_new = shift_date_time_string(shift_epoch, dicom_tags[date_field], dicom_tags[time_field])
                    replace_dict[date_field] = date_string_new
                    replace_dict[time_field] = time_string_new
                else:
                    if log_message_bitflag:
                        log_message(log_message_bitflag, global_var['log_indent_level'], 'No matching time for date: %s, %s'  % (date_field, time_field), **kwargs)

        # Loop through combo date/time tags looking for fields to update
        for date_time_field in date_time_fields:
            if date_time_field in dicom_tags and len(dicom_tags[date_time_field].strip()) > 0:
                date_string_new = shift_date_time_string(shift_epoch, dicom_tags[date_time_field])
                replace_dict[date_time_field] = date_string_new

        # Loop over radiopharm fields
        radio_sequence = 'RadiopharmaceuticalInformationSequence'
        if radio_sequence in dicom_tags:
            replace_dict[radio_sequence] = copy.copy(dicom_tags[radio_sequence])
            i_seq_tag = 0
            for seq_tags in dicom_tags[radio_sequence]:
                for date_time_field_radio in date_time_fields_radio:
                    if date_time_field_radio in seq_tags and len(seq_tags[date_time_field_radio].strip()) > 0:
                        date_string_new = shift_date_time_string(shift_epoch, seq_tags[date_time_field_radio])
                        replace_dict[radio_sequence][i_seq_tag][date_time_field_radio] = date_string_new
                i_seq_tag += 1

        # Loop over frame fields
        per_frame_functional_groups_sequence = 'PerFrameFunctionalGroupsSequence'
        frame_content_sequence = 'FrameContentSequence'
        if per_frame_functional_groups_sequence in dicom_tags:
            replace_dict[per_frame_functional_groups_sequence] = copy.copy(dicom_tags[per_frame_functional_groups_sequence])
            i_group = 0
            for functional_group_dict in dicom_tags[per_frame_functional_groups_sequence]:
                if frame_content_sequence in functional_group_dict:
                    i_content = 0
                    for frame_content_dict in functional_group_dict[frame_content_sequence]:
                        for date_time_field_frame in date_time_fields_frame:
                            if date_time_field_frame in frame_content_dict and len(frame_content_dict[date_time_field_frame].strip()) > 0:
                                date_string_new = shift_date_time_string(shift_epoch, frame_content_dict[date_time_field_frame])
                                replace_dict[per_frame_functional_groups_sequence][i_group][frame_content_sequence][i_content][date_time_field_frame] = date_string_new
                        i_content += 1
                i_group += 1

        # Handle birthdate / age
        if 'PatientBirthDate' in dicom_tags:
            date_string_new = shift_date_time_string(shift_epoch, dicom_tags['PatientBirthDate'])
            replace_dict['PatientBirthDate'] = date_string_new
        if 'PatientAge' in dicom_tags:
            age_number = int(dicom_tags['PatientAge'][0:3])
            age_unit = dicom_tags['PatientAge'][3]
            if age_unit == 'Y':
                if age_number > 89:
                    age_number = 90
                    replace_dict['PatientAge'] = '%03dY' %  age_number

        # Handle non-date/time replacements that take place at this stage
        if 'SOPInstanceUID' in dicom_tags:
            sop_instance_uid_new = global_var['uid_map'][dicom_tags['SOPInstanceUID']]
            while sop_instance_uid_new in global_var['uid_map']:
                sop_instance_uid_new = global_var['uid_map'][sop_instance_uid_new]
            replace_dict['SOPInstanceUID'] = sop_instance_uid_new

        # Need to work through numeric tags now
        if flag_send_to_remote:
            dicom_tags = json.loads(orthanc.RestApiGet('/instances/%s/tags' % orthanc_instance_id))
            for tag_key, tag_val in global_var['top_level_tag_to_keep'].items():
                if tag_key in dicom_tags:
                    if type(dicom_tags[tag_key]['Value']) in [type_dict, type_list]:
                        iReplaceValue, lLevelOut = recursive_replace_uid(dicom_tags[tag_key])
                        if global_var['address_list'] is not None:
                            for address_key, address_val in global_var['address_list'].items():
                                replace_dict[address_key] = address_val
                    else:
                        if dicom_tags[tag_key]['Value'] not in global_var['uid_map']:
                            log_message(log_message_bitflag, global_var['log_indent_level'], json.dumps(global_var['uid_map'],indent=3), **kwargs)
                            log_message(log_message_bitflag, global_var['log_indent_level'], json.dumps(dicom_tags,indent=3), **kwargs)
                        uid_new = global_var['uid_map'][dicom_tags[tag_key]['Value']]
                        while uid_new in global_var['uid_map']:
                            if uid_new == global_var['uid_map'][uid_new]:
                                break
                            uid_new = global_var['uid_map'][uid_new]
                        replace_dict[tag_key] = uid_new

        if len(dicom_tags) > 0:
            post_data = {}
            post_data['Replace'] = replace_dict
            # post_data['DicomVersion'] = '2017c'
            # post_data['DicomVersion'] = '2008'
            post_data['Force'] = True
            try:
                modified_dicom_blob = orthanc.RestApiPost('/instances/%s/modify' % orthanc_instance_id, json.dumps(post_data))
            except:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], json.dumps(post_data,indent=3), **kwargs)
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status' : 1, 'error_text' : 'Unable to adjust dates'}, None

            # Upload the modified_dicom_blob (need to confirm this for python post
            try:
                meta_instance_modified = orthanc.RestApiPost('/instances/', modified_dicom_blob)
            except:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Problem uploading new image blob', **kwargs)
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
                    global_var['log_indent_level'] = log_indent_level_prev
                return {'status' : 2, 'error_text' : 'Problem uploading new image blob'}, None
            orthanc_instance_id_new = json.loads(meta_instance_modified)['ID']

            # Store new ID
            orthanc_instance_ids_new += [orthanc_instance_id_new]
    
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}, orthanc_instance_ids_new

# =======================================================
def shift_date_time_string(shift_epoch,incoming_yyyymmdd,incoming_hhmmss=None):
    """Shift time stamp and return shifted values"""
# -------------------------------------------------------
   
    flag_time_found = True
    incoming_yyyymmdd = incoming_yyyymmdd.strip()
    if len(incoming_yyyymmdd) == 14:
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd,'%Y%m%d%H%M%S')
        fraction_str = None
    elif len(incoming_yyyymmdd) > 14 and incoming_yyyymmdd.find('.') == 14:
        fraction_str = incoming_yyyymmdd[14:]
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd[0:14],'%Y%m%d%H%M%S')
    elif len(incoming_yyyymmdd) > 14 and incoming_yyyymmdd.find('.') < 0:
        fraction_str = None
        incoming_datetime = datetime.datetime.strptime(incoming_yyyymmdd[0:14],'%Y%m%d%H%M%S')
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
        incoming_datetime = incoming_datetime.replace(hour=date_local.hour,minute=date_local.minute,second=date_local.second)

    # Shift the dates
    outgoing_datetime = incoming_datetime - datetime.timedelta(seconds=shift_epoch)

    # Preserve the original hour, minute, second
    outgoing_datetime = outgoing_datetime.replace(hour=incoming_datetime.hour, minute=incoming_datetime.minute, second=incoming_datetime.second)

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
def update_lookup_html(**kwargs):
    """ Update the html lookup table  """
# -------------------------------------------------------
    global global_var
    log_message_bitflag = python_verbose_logwarning + (2 if 'log_user' in kwargs else 0)
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name, **kwargs)
        global_var['log_indent_level'] += 3

    flag_keep_original_dates = os.getenv('PYTHON_FLAG_KEEP_ORIGINAL_DATES', default='false') == 'true'

    # Load the map from the sql database
    status, patient_map, patient_reverse_map, flag_siuid_to_anon = load_phi_to_anon_map(**kwargs)
    if status['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], status['error_text'], **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status
    
    # Map what's on Orthanc now
    status, now_on_orthanc = on_orthanc(**kwargs)
    if status['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], status['error_text'], **kwargs)
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return status

    # Check for the main modality that could be queried
    flag_xref_modality, xref_modality = check_xref_modality(**kwargs)

    # Check for existing lookup table
    file_lookup = '/media/html/lookup/master/lookuptable.html'
    answer, lookup_table = load_lookup_table(file_lookup, make_backup=True, **kwargs)
    if answer['status'] != 0:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
            global_var['log_indent_level'] = log_indent_level_prev
        return answer

    # Prepare to output the new
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Preparing to write new lookup file', **kwargs)
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
        now_on_orthanc['StudyInstanceUIDPrinted'] = {}
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
                    now_on_orthanc['StudyInstanceUIDPrinted'][study_instance_uid] = True
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
                    if len(lookup_table) > 0:
                        lookup_match, pacs_data_local  = find_pacs_in_lookup_table(lookup_table,study_instance_uid,type_match='siuid')
                        if pacs_data_local is None:
                            if log_message_bitflag:
                                log_message(log_message_bitflag, global_var['log_indent_level'], 'Not found in lookup: ' + study_instance_uid, **kwargs)
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
                                  ((len(lookup_table) > 0) and \
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
                    now_on_orthanc['StudyInstanceUIDPrinted'][study_instance_uid] = True
                    #compute_times[110]['count'] += 1
                    #compute_times[110]['value'] += time.time() - time0
            lun.flush()
            #for c_id, compute_time in compute_times.items():
            #    if compute_time['value'] == 0 or compute_time['count'] == 0:
            #        continue
            #    log_message(log_message_bitflag, global_var['log_indent_level'], 'Compute time %d %f' % (c_id, compute_time['value'] / compute_time['count']), **kwargs)
        for patient_id, row_of_data in now_on_orthanc['ByPatientID'].items():
            for index_entry in range(len(row_of_data['StudyInstanceUID'])):
                study_instance_uid = row_of_data['StudyInstanceUID'][index_entry]
                if study_instance_uid not in now_on_orthanc['StudyInstanceUIDPrinted']:
                    date_str = row_of_data['StudyDate'][index_entry]
                    accession_number = row_of_data['AccessionNumber'][index_entry]
                    lun.write('<tr>\n')
                    lun.write('<td>\n')
                    lun.write('<a href="../../../app/explorer.html#patient?uuid=' + now_on_orthanc['PatientID2oPatientID'][patient_id] + '">\n')
                    lun.write(now_on_orthanc['ByPatientID'][patient_id]['PatientName'])
                    lun.write('</a>\n')
                    lun.write('</td>\n')
                    lun.write('<td align="right">' + patient_id + '</td>\n')
                    lun.write('<td>&nbsp</td>\n')
                    lun.write('<td>&nbsp</td>\n')
                    lun.write('<td align="center">' + date_str + '</td>\n')
                    lun.write('<td>&nbsp</td>\n')
                    lun.write('<td align="right">' + accession_number + '</td>\n')
                    lun.write('<td>&nbsp</td>\n')
                    lun.write('<td>&nbsp</td>\n')
                    lun.write('<td align="right">\n')
                    lun.write('<a href="../../../app/explorer.html#study?uuid=' + now_on_orthanc['StudyUID2oStudyUID'][study_instance_uid] + '">\n')
                    lun.write(study_instance_uid)
                    lun.write('</a>\n')
                    lun.write('</td>\n')
                    lun.write('<td>&nbsp</td>\n')
                    lun.write('</tr>\n')
                    lun.flush()

        lun.write('</tbody>\n')
        lun.write('</table>\n')
        lun.write('</body>\n')
        lun.write('</html>\n')

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0), **kwargs)
        global_var['log_indent_level'] = log_indent_level_prev

    return {'status': 0}

# =======================================================
def user_permitted(uri, remote_user):
    """ Check remote user against list of permitted users """
# -------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Checking whether remote user (%s) is permitted to act on %s' % (remote_user,uri))
    permissions = os.getenv('PYTHON_X_REMOTE_USER_ALLOWED_TO_TRIGGER')
    if permissions is None:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Rejecting anon due to missing permissions')
        return False
    allowed_to_trigger = []
    for permitted in permissions.split('.'):
        if permitted.strip() not in allowed_to_trigger:
            allowed_to_trigger += [permitted.strip()]
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Allowed users: %s' % ' '.join(allowed_to_trigger))
    if remote_user not in allowed_to_trigger:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Operation not permitted to user: %s %s' % (uri, remote_user))
        return False
    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Remote user is permitted (%s)' % remote_user)

    return True

# ============================================================================
def AnonymizeByLabel(output, uri, **request):
    """API interface to setup anonymization based on Orthanc labels"""
# ----------------------------------------------------------------------------

    global global_var
    if user_permitted(uri, get_remote_user(request['headers'])):
        answer_buffer = anonymize_by_label_init()
        output.AnswerBuffer(answer_buffer, 'text/html')
    else:
        log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Anonymize by label not permitted to user %s' % get_remote_user(request['headers']))
        output.AnswerBuffer('Anonymize by label not permitted to user', 'text/plain')

# ============================================================================
def AnonymizeByLabelRun(output, uri, **request):
    """API interface to run anonymization based on Orthanc labels"""
# ----------------------------------------------------------------------------

    global global_var
    remote_user = get_remote_user(request['headers'])
    if user_permitted(uri, get_remote_user(request['headers'])):
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        t = threading.Timer(0, function=anonymize_by_label_run, kwargs={'remote_user':remote_user, 'log_user':random_string})
        t.start()
        #status = anonymize_by_label_run(remote_user=remote_user)
        #if status['status'] == 0:
        #    output.AnswerBuffer('success', 'text/plain')
        #else:
        #    output.AnswerBuffer(status['error_text'], 'text/plain')
        output.AnswerBuffer('/%s/userlog/%s' % (global_var['website'], random_string), 'text/plain')
    else:
        log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Anonymize by label not permitted to user %s' % get_remote_user(request['headers']))
        output.AnswerBuffer('Anonymize by label not permitted to user', 'text/plain')

# ============================================================================
def ConstructPatientName(output, uri, **request):
    """API interface to construct the patients name"""
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        incoming_data = json.loads(request['body'])
        internal_number = int(float(incoming_data['InternalNumber']))
        patient_name_base_local = incoming_data['PatientNameBase'] if 'PatientNameBase' in incoming_data else None
        patient_name_id_char = incoming_data['PatientNameIDChar'] if 'PatientNameIDChar' in incoming_data else 'ID'
        patient_name = construct_patient_name(internal_number,
                                              patient_name_base_local=patient_name_base_local, 
                                              patient_name_id_char=patient_name_id_char)
        output.AnswerBuffer(patient_name, 'text/plain')
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

# ============================================================================
def GetConfiguration(output, uri, **request):
    """API interface to retrieve the configuration"""
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        configuration = orthanc.GetConfiguration()
        output.AnswerBuffer(configuration, 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def GetPatientNameBase(output, uri, **request):
# ----------------------------------------------------------------------------
    if request['method'] == 'GET':
        patient_name_base_local = get_patient_name_base()
        result = {'PatientNameBase' : patient_name_base_local}
        output.AnswerBuffer(json.dumps(result,indent=3), 'application/json')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
def IncomingFilter(uri, **request):
    """Set up rights based actions"""
# ----------------------------------------------------------------------------

    global global_var
    log_message_bitflag = python_verbose_logwarning
    headers_str = ''
    for key,value in request['headers'].items():
        headers_str = '%s %s.%s' % (headers_str, key, value)
    if not('x-remote-user' in request['headers'] and 'x-forwarded-for' in request['headers']):
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Rejecting incoming access: %s' % headers_str)
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
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], '%s %s %s %s' % (remote_user, remote_ip, method, uri))

    if method in ['DELETE', 'PUT']:
        return user_permitted(uri, remote_user)
        
    if method == 'POST' and \
        uri.find('/set_patient_name_base') >= 0:
        if not user_permitted(uri, remote_user):
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User not permitted to anonymize: %s' % remote_user)
            return False
        else: 
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User permitted to anonymize: %s' % remote_user)
        return True

    if method == 'POST' and uri.find('/execute-script') >= 0:
        if not user_permitted(uri, remote_user):
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User not permitted to execute-script: %s' % remote_user)
            return False
        else: 
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User permitted to execute-script: %s' % remote_user)
            return True

    if method == 'POST' and \
        ((uri.find('/anonymize') >= 0 and (uri.find('/anonymize_by') < 0)) or \
         uri.find('/jsanon') >= 0):

        if not user_permitted(uri, remote_user):
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User not permitted to anonymize: %s' % remote_user)
            return False
        else: 
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User permitted to anonymize: %s' % remote_user)

        # Note that we have to capture anonymize this way as opposed to registering a callback
        # That's because registering a callback would proceed with both OUR anonymization and the standard Orthanc anon
        study_res = None
        if uri.find('/anonymize') >= 0:
            study_res = re.match('.*studies/([^/]+)/anonymize', uri)
            if study_res is None:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'User does not appear to be anonymizing at the series level:\n%s' % uri)
                return False
            flag_js = False
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User triggered web anonymize')
        if uri.find('/jsanon') >= 0:
            study_res = re.match('.*studies/([^/]+)/jsanon', uri)
            if study_res is None:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'User does not appear to be anonymizing at the series level:\n%s' % uri)
                return False
            flag_js = True
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'User triggered form based anonymize')

        if study_res is not None:
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Starting anon')
            orthanc_study_id = study_res.group(1)
            global_var['log_indent_level'] = 0
            status = anonymize_study_init(orthanc_study_id, 
                                          flag_force_anon=True, 
                                          trigger_type='jsanon' if flag_js else 'anonymize', 
                                          remote_user=remote_user)
            if log_message_bitflag:
                log_message(log_message_bitflag, global_var['log_indent_level'], 'Anon returned.')
            if flag_js:
                return True
            else:
                return False

    if uri.find('/extra/lookup/master/updatelookup.html') >= 0:
        if user_permitted(uri, remote_user):
            status = update_lookup_html()
        else:
            return False

    if uri.find('update_lookup_table') >= 0:
        if not user_permitted(uri, remote_user):
            return False

    return True

# ============================================================================
def InspectPythonAPI(output, uri, **request):
    """Print out the api"""
# ----------------------------------------------------------------------------

    if request['method'] == 'GET':
        # Loop over the members of the "orthanc" module
        text_out = ''
        for (name, obj) in inspect.getmembers(orthanc):
            if inspect.isroutine(obj):
                text_out += 'Function %s():\n  Documentation: %s\n' % (name, inspect.getdoc(obj))
        
            elif inspect.isclass(obj):
                text_out += 'Class %s:\n  Documentation: %s\n' % (name, inspect.getdoc(obj))
        
                # Loop over the members of the class
                for (subname, subobj) in inspect.getmembers(obj):
                    if isinstance(subobj, numbers.Number):
                        text_out += '  - Enumeration value %s: %s\n' % (subname, subobj)
                    elif (not subname.startswith('_') and
                          inspect.ismethoddescriptor(subobj)):
                        text_out += '  - Method %s(): %s\n' % (subname, inspect.getdoc(subobj))

        output.AnswerBuffer(text_out, 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

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
    if change_type == orthanc.ChangeType.STABLE_STUDY:

        # Auto anonymization
        flag_anonymize_upon_stable = os.getenv('PYTHON_FLAG_AUTO_ANON_WHEN_STABLE', default='false') == 'true'
        if flag_anonymize_upon_stable:
            global_var['log_indent_level'] = 0
            #status = anonymize_study_init(resource_id, flag_force_anon=False, trigger_type='onchange')
            #if status['status'] != 0:
            #    log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Auto anon failed: %s' % status['error_text'])
            t = threading.Timer(0, function=anonymize_study_init, args=(resource_id,), kwargs={'flag_force_anon':False, 'trigger_type':'onchange'})
            t.start()

        # Email updates
        if os.getenv('PYTHON_MAIL_AUTO', default='false') == 'true':
            status = email_study_report(resource_id)
            if status['status'] != 0:
                if python_verbose_logwarning:
                    log_message(python_verbose_logwarning, global_var['log_indent_level'], status['error_text'])
            else:
                if python_verbose_logwarning:
                    log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Sent onstable study report')

# ============================================================================
def OnChangeThreaded(change_type, level, resource_id):
    """
    PURPOSE: An attempt to use threading to avoid the locks I see when 
                invoking Lua from OnChange.  Subsequent OnChange can break
                previous ongoing Lua calls.
    INPUT:   structures routed by way of the python plugin
    OUTPUT:  Designated action
    """
# ----------------------------------------------------------------------------

    # ------------------------------
    # Stable Study
    if change_type == orthanc.ChangeType.STABLE_STUDY:

        # Invoke the actual "OnChange()" function in a separate thread
        t = threading.Timer(0, function = OnChange, args = (change_type, level, resource_id))
        t.start()

# ============================================================================
def PrepareDataForAnonymizeGUI(output, uri, **request):
    """Setup data for javascript anonymizer."""
# ----------------------------------------------------------------------------

    global global_var
    if request['method'] == 'GET':

        log_message_bitflag = python_verbose_logwarning
        if log_message_bitflag:
            log_indent_level_prev = global_var['log_indent_level']
            time_0 = time.time()
            frame = inspect.currentframe()
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
            global_var['log_indent_level'] += 3

        answer = {'status': 0}

        # Check inputs
        if not global_var['flag']['beautiful_soup']:
            answer['status'] = 1
            answer['error_text'] = 'PrepareDataForAnonymize: No beautiful soup.  Needed to parse lookup.'
            output.AnswerBuffer(json.dumps(answer, indent=3), 'application/json')

        if not global_var['flag']['psycopg2']:
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

        # Assemble map of patient studies
        response_patients = orthanc.RestApiGet('/patients')
        patient_studies = {}
        for opatientid in json.loads(response_patients):
            response_patient = orthanc.RestApiGet('/patients/%s' % opatientid)
            meta_patient = json.loads(response_patient)
            patient_name = meta_patient['MainDicomTags']['PatientName'] if 'PatientName' in meta_patient['MainDicomTags'] else opatientid
            if patient_name not in patient_studies:
                patient_studies[patient_name] = []
            patient_studies[patient_name] += meta_patient['Studies']
        patient_names = list(patient_studies.keys())
        patient_names.sort()
        ostudyids = []
        for patient_name in patient_names:
            ostudyids += patient_studies[patient_name]
 
        # Initialize output
        data_for_anonymize_gui = {'StudyMeta' : {},
                                  'SeriesMeta' : {},
                                  'DB' : {},
                                  'PACS' : {},
                                  'Lookup' : {}}
        study_date = {}

        # DICOM now on Orthanc
        #response_studies = orthanc.RestApiGet('/studies')
        #for ostudyid in json.loads(response_studies):
        for ostudyid in ostudyids:

            flag_first_image = True
            meta_study = json.loads(orthanc.RestApiGet('/studies/%s' % ostudyid))
            patient_id_modifier = ''
            study_instance_uid_modifier = ''
            if not ('AnonymizedFrom' in meta_study or 'ModifiedFrom' in meta_study):
            #if 'AnonymizedFrom' not in meta_study:
        
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

    if log_message_bitflag:
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
        global_var['log_indent_level'] = log_indent_level_prev

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
def SetPatientNameBase(output, uri, **request):
# ----------------------------------------------------------------------------
    if request['method'] == 'POST':
        incoming_data = json.loads(request['body'])
        if 'PatientNameBase' in incoming_data:
            set_patient_name_base(incoming_data['PatientNameBase'].strip())
        if 'Reset' in incoming_data:
            reset_patient_name_base()
        output.AnswerBuffer('Success', 'text/plain')
    else:
        output.SendMethodNotAllowed('POST')

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
def TogglePythonFlagAssumeOriginalPrimary(output, uri, **request):
    """API to trigger setting PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY env variable for lua scripts"""
# ----------------------------------------------------------------------------

    if user_permitted(uri, get_remote_user(request['headers'])):
        try:
            flag_current = os.getenv('PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY', default='true')
            if flag_current == 'true':
                if python_verbose_logwarning:
                    log_message(python_verbose_logwarning, global_var['log_indent_level'], 'PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY is true, turning false...')
                os.environ['PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY'] = 'false'
                output.AnswerBuffer('PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY was true, now false', 'text/plain')
            else:
                if python_verbose_logwarning:
                    log_message(python_verbose_logwarning, global_var['log_indent_level'], 'PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY is false, turning true...')
                os.environ['PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY'] = 'true'
                output.AnswerBuffer('PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY was false, now true', 'text/plain')
        except:
            if python_verbose_logwarning:
                log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Problem getting PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY state')
            output.AnswerBuffer('Problem getting PYTHON_FLAG_ASSUME_ORIGINAL_PRIMARY state', 'text/plain')

# ============================================================================
def TogglePythonMailAuto(output, uri, **request):
    """API to toggle the state of the PYTHON_MAIL_AUTO env variable"""
# ----------------------------------------------------------------------------

    if user_permitted(uri, get_remote_user(request['headers'])) and \
        'PYTHON_MAIL_AUTO' in os.environ:
        python_mail_auto_prev = os.environ['PYTHON_MAIL_AUTO']
        if python_verbose_logwarning:
            log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Previous PYTHON_MAIL_AUTO: %s' % python_mail_auto_prev)
        if python_mail_auto_prev == 'true':
            os.environ['PYTHON_MAIL_AUTO'] = 'false'
        else:
            os.environ['PYTHON_MAIL_AUTO'] = 'true'
        python_mail_auto = os.environ['PYTHON_MAIL_AUTO']
        if python_verbose_logwarning:
            log_message(python_verbose_logwarning, global_var['log_indent_level'], 'Current PYTHON_MAIL_AUTO: %s' % python_mail_auto)
        if python_mail_auto == 'true':
            output.AnswerBuffer('Previous PYTHON_MAIL_AUTO: %s\nCurrent PYTHON_MAIL_AUTO: %s\nYou WILL receive email updates until this setting is reversed.' % (python_mail_auto_prev, python_mail_auto), 'text/plain')
        else:
            output.AnswerBuffer('Previous PYTHON_MAIL_AUTO: %s\nCurrent PYTHON_MAIL_AUTO: %s\nYou will NOT receive email updates until this setting is reversed.' % (python_mail_auto_prev, python_mail_auto), 'text/plain')

# ============================================================================
def TogglePythonVerbose(output, uri, **request):
    """ Api to toggle state of verbose log warnings from python """
# ----------------------------------------------------------------------------

    global python_verbose_logwarning
    if user_permitted(uri, get_remote_user(request['headers'])):
        if python_verbose_logwarning:
            log_message(python_verbose_logwarning, global_var['log_indent_level'], 'python_verbose_logwarning was ON, turning OFF...')
            output.AnswerBuffer('python_verbose_logwarning was ON, now OFF', 'text/plain')
        else:
            log_message(python_verbose_logwarning, global_var['log_indent_level'], 'python_verbose_logwarning was OFF, turning ON...')
            output.AnswerBuffer('python_verbose_logwarning was OFF, now ON', 'text/plain')
        python_verbose_logwarning = not python_verbose_logwarning 

# ============================================================================
def UpdateAnonymizationQueue(output, uri, **request):
    """API interface to update the anonymization queue parameters"""
# ----------------------------------------------------------------------------
    global global_var
    log_message_bitflag = python_verbose_logwarning
    if log_message_bitflag:
        log_indent_level_prev = global_var['log_indent_level']
        global_var['log_indent_level'] = 0
        time_0 = time.time()
        frame = inspect.currentframe()
        log_message(log_message_bitflag, global_var['log_indent_level'], 'Entering %s' % frame.f_code.co_name)
        global_var['log_indent_level'] += 3

    if request['method'] == 'POST':
        orthanc_study_id = request['groups'][0]
        if orthanc_study_id in global_var['anonymization_queue']:
            parameters_incoming = json.loads(request['body'])
            if 'extra' in parameters_incoming:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating extra: %s' % parameters_incoming['extra'])
                extra = parameters_incoming['extra'].strip()
                global_var['anonymization_queue'][orthanc_study_id]['extra'] = extra
            if 'irb_standard' in parameters_incoming:
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Updating irb: %s' % parameters_incoming['irb_standard'])
                parameters_standard = irb_label_regex_map(parameters_incoming['irb_standard'])
                parameters_standard['extra'] = global_var['anonymization_queue'][orthanc_study_id]['extra'] if 'extra' in global_var['anonymization_queue'][orthanc_study_id] else ''
                # First the queue
                global_var['anonymization_queue'][orthanc_study_id] = parameters_standard
                # Then labels
                labels = json.loads(orthanc.RestApiGet('/studies/%s/labels' % orthanc_study_id))
                for label in labels:
                    if global_var['irb_re'].match(label) is not None:
                        if log_message_bitflag:
                            log_message(log_message_bitflag, global_var['log_indent_level'], 'Deleting irb: %s' % label)
                        orthanc.RestApiDelete('/studies/%s/labels/%s' % (orthanc_study_id, label))
                if log_message_bitflag:
                    log_message(log_message_bitflag, global_var['log_indent_level'], 'Putting irb: %s' % parameters_standard['irb_standard'])
                orthanc.RestApiPut('/studies/%s/labels/%s' % (orthanc_study_id, parameters_standard['irb_standard']), json.dumps({}))
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
            global_var['log_indent_level'] = log_indent_level_prev

        output.AnswerBuffer(json.dumps({}, indent = 3), 'application/json')
    else:
        if log_message_bitflag:
            log_message(log_message_bitflag, global_var['log_indent_level'], 'Time spent in %s: %d' % (frame.f_code.co_name, time.time()-time_0))
            global_var['log_indent_level'] = log_indent_level_prev
        output.SendMethodNotAllowed('POST')

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
def UserLog(output, uri, **request):
    """ API to show progress log tied to user """
# ----------------------------------------------------------------------------
    global global_var
    if request['method'] == 'GET':
        log_user = request['groups'][0]
        if log_user in global_var['log_user']:
            output.AnswerBuffer('\n'.join(global_var['log_user'][log_user]), 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

# ============================================================================
# Main
orthanc.RegisterIncomingHttpRequestFilter(IncomingFilter)
orthanc.RegisterOnChangeCallback(OnChangeThreaded)
orthanc.RegisterRestCallback('/anonymize_by_label', AnonymizeByLabel)
orthanc.RegisterRestCallback('/anonymize_by_label_run', AnonymizeByLabelRun)
orthanc.RegisterRestCallback('/construct_patient_name', ConstructPatientName)
orthanc.RegisterRestCallback('/studies/(.*)/email_report', EmailStudyReport)
#orthanc.RegisterRestCallback('/get_configuration', GetConfiguration)
orthanc.RegisterRestCallback('/get_patient_name_base', GetPatientNameBase)
#orthanc.RegisterRestCallback('/inspect_python_api', InspectPythonAPI)
orthanc.RegisterRestCallback('/studies/(.*)/jsanon', JSAnonymizeStudy)
orthanc.RegisterRestCallback('/prepare_data_for_anonymize', PrepareDataForAnonymizeGUI)
orthanc.RegisterRestCallback('/instances/(.*)/group(.*)recursive_search', ScanInstanceForGroupElement)
orthanc.RegisterRestCallback('/instances/(.*)/odd_group_recursive_search', ScanInstanceForOddGroups)
orthanc.RegisterRestCallback('/series/(.*)/group(.*)recursive_search', ScanSeriesForGroupElement)
orthanc.RegisterRestCallback('/series/(.*)/odd_group_recursive_search', ScanSeriesForOddGroups)
orthanc.RegisterRestCallback('/studies/(.*)/group(.*)recursive_search', ScanStudyForGroupElement)
orthanc.RegisterRestCallback('/studies/(.*)/odd_group_recursive_search', ScanStudyForOddGroups)
orthanc.RegisterRestCallback('/set_patient_name_base', SetPatientNameBase)
orthanc.RegisterRestCallback('/studies/(.*)/set_screen_or_diagnostic', SetScreenOrDiagnostic)
orthanc.RegisterRestCallback('/toggle_python_flag_assume_original_primary', TogglePythonFlagAssumeOriginalPrimary)
orthanc.RegisterRestCallback('/toggle_python_mail_auto', TogglePythonMailAuto)
orthanc.RegisterRestCallback('/toggle_python_verbose', TogglePythonVerbose)
orthanc.RegisterRestCallback('/studies/(.*)/update_anonymization_queue', UpdateAnonymizationQueue)
orthanc.RegisterRestCallback('/update_lookup_table', UpdateLookupTable)
orthanc.RegisterRestCallback('/userlog/(.*)', UserLog)

