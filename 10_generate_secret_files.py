#!/bin/python3
import os
import sys
import json
import re
import stat

re_parameter = re.compile('^([A-Z_0-9]+) *= *(.*)[ \n]*')
parameters = {}
if not os.path.exists('.env'):
    sys.exit('No .env found.  You might need to copy (and edit!) default.dot.env')
lun = open('.env','r')
lines_of_text = lun.readlines()
lun.close()
for line_of_text in lines_of_text:
    res_parameter = re_parameter.match(line_of_text)
    if res_parameter is not None:
        line_split = line_of_text.split('=')
        parameter_name = res_parameter.group(1)
        parameter_value = res_parameter.group(2)
        parameters[parameter_name] = parameter_value

for root, subdirs, files in os.walk('.'):

    for file_template in files:
        if re.match('.*.template$', file_template) is not None:
            file_out = '%s/%s' % (root, file_template[0:-9])
            lun_in = open('%s/%s' % (root, file_template), 'r')
            lines_of_text = lun_in.readlines()
            lun_in.close()
            with open(file_out, 'w') as lun_out:
                for line_of_text_in in lines_of_text:
                    line_of_text_out = '%s' % line_of_text_in
                    for parameter_name, parameter_value in parameters.items():
                        if line_of_text_out.find(parameter_name) >= 0:
                            line_of_text_out=line_of_text_out.replace(parameter_name, parameter_value)
                    lun_out.write('%s' % line_of_text_out)

            stat_original = os.stat('%s/%s' % (root, file_template))
            uid = stat_original.st_uid
            gid = stat_original.st_gid
            os.chmod(file_out, stat.S_IRUSR)
            os.chown(file_out, uid, gid)
        
