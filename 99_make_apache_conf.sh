#!/usr/bin/bash 
# Load the environment with all our tailored settings
. .env

name_phi="${COMMON_BASENAME^^}_PHI_ORTHANC"
file_phi=$COMMON_BASENAME"_phi_orthanc.conf"

# Assuming admin is the first registered user
admin_pwd=`grep PHI_REGISTERED_USERS .env | awk '{split($0,a,"\""); print a[2]":"a[4]}'`
admin_pwd_64=`echo -n $admin_pwd | base64`
echo "" > $file_phi
echo "   SSLProxyEngine On" >> $file_phi
echo "   ProxyRequests Off" >> $file_phi
echo "   SSLProxyCheckPeerCN Off" >> $file_phi
echo "   SSLProxyCheckPeerName Off" >> $file_phi
echo "   SSLProxyCACertificateFile /DATA/orthanc/$COMMON_BASENAME/phi/orthanc/external/certificates/certificate.pem" >> $file_phi
echo "   Include /etc/httpd/conf.d/apache_docker_services.conf.inc" >> $file_phi
echo "" >> $file_phi
echo "   <Location \"/$PHI_ORTHANC_WEBSITE_NAME/\">" >> $file_phi
echo "   " >> $file_phi
echo "      AuthType CAS" >> $file_phi
echo "      AuthName \"$PHI_ORTHANC_WEBSITE_NAME\"" >> $file_phi
echo "      #Require valid-user" >> $file_phi
echo "      #            Privileged       " >> $file_phi
echo "      Require user $PHI_X_REMOTE_USER_ALLOWED_TO_TRIGGER " >> $file_phi
echo "   " >> $file_phi
echo "      Order Deny,Allow" >> $file_phi
echo "      Deny from all" >> $file_phi
echo "      Allow from $PHI_X_REMOTE_IP_ALLOWED_TO_TRIGGER" >> $file_phi
echo "" >> $file_phi
echo "      SSLRequireSSL" >> $file_phi
echo "" >> $file_phi
echo "      <If \"%{REMOTE_ADDR} == '$PHI_X_REMOTE_IP_ALLOWED_TO_TRIGGER'\">" >> $file_phi
echo "         RequestHeader set Authorization \"Basic $admin_pwd_64\"" >> $file_phi
echo "         AllowMethods reset" >> $file_phi
echo "      </If>" >> $file_phi
echo "      <Else>" >> $file_phi
echo "         AllowMethods GET HEAD CONNECT OPTIONS TRACE" >> $file_phi
echo "      </Else>" >> $file_phi
echo "" >> $file_phi
echo "      ProxyPass \"https://\${$name_phi}:8042/\"" >> $file_phi
echo "      ProxyPassReverse \"https://\${$name_phi}:8042/\"" >> $file_phi
echo "   " >> $file_phi
echo "   </Location>" >> $file_phi
echo "" >> $file_phi
echo "" >> $file_phi

name_anon="${COMMON_BASENAME^^}_ANON_ORTHANC"
file_anon=$COMMON_BASENAME"_anon_orthanc.conf"

# Assuming admin is the first registered user
admin_pwd=`grep ANON_REGISTERED_USERS .env | awk '{split($0,a,"\""); print a[2]":"a[4]}'`
admin_pwd_64=`echo -n $admin_pwd | base64`
echo "" > $file_anon
echo "   SSLProxyEngine On" >> $file_anon
echo "   ProxyRequests Off" >> $file_anon
echo "   SSLProxyCheckPeerCN Off" >> $file_anon
echo "   SSLProxyCheckPeerName Off" >> $file_anon
echo "   SSLProxyCACertificateFile /DATA/orthanc/$COMMON_BASENAME/anon/orthanc/external/certificates/certificate.pem" >> $file_anon
echo "   Include /etc/httpd/conf.d/apache_docker_services.conf.inc" >> $file_anon
echo "" >> $file_anon
echo "   <Location \"/$ANON_ORTHANC_WEBSITE_NAME/\">" >> $file_anon
echo "   " >> $file_anon
echo "      AuthType CAS" >> $file_anon
echo "      AuthName \"$ANON_ORTHANC_WEBSITE_NAME\"" >> $file_anon
echo "      #Require valid-user" >> $file_anon
echo "      #            Privileged       " >> $file_anon
echo "      Require user $ANON_X_REMOTE_USER_ALLOWED_TO_TRIGGER " >> $file_anon
echo "   " >> $file_anon
echo "      Order Deny,Allow" >> $file_anon
echo "      Deny from all" >> $file_anon
echo "      Allow from $ANON_X_REMOTE_IP_ALLOWED_TO_TRIGGER" >> $file_anon
echo "" >> $file_anon
echo "      SSLRequireSSL" >> $file_anon
echo "" >> $file_anon
echo "      <If \"%{REMOTE_ADDR} == '$ANON_X_REMOTE_IP_ALLOWED_TO_TRIGGER'\">" >> $file_anon
echo "         RequestHeader set Authorization \"Basic $admin_pwd_64\"" >> $file_anon
echo "         AllowMethods reset" >> $file_anon
echo "      </If>" >> $file_anon
echo "      <Else>" >> $file_anon
echo "         AllowMethods GET HEAD CONNECT OPTIONS TRACE" >> $file_anon
echo "      </Else>" >> $file_anon
echo "" >> $file_anon
echo "      ProxyPass \"https://\${$name_anon}:8042/\"" >> $file_anon
echo "      ProxyPassReverse \"https://\${$name_anon}:8042/\"" >> $file_anon
echo "   " >> $file_anon
echo "   </Location>" >> $file_anon
echo "" >> $file_anon
echo "" >> $file_anon

name_disk="${COMMON_BASENAME^^}_DISK_ORTHANC"
file_disk=$COMMON_BASENAME"_disk_orthanc.conf"

# Assuming admin is the first registered user
admin_pwd=`grep DISK_REGISTERED_USERS .env | awk '{split($0,a,"\""); print a[2]":"a[4]}'`
admin_pwd_64=`echo -n $admin_pwd | base64`
echo "" > $file_disk
echo "   SSLProxyEngine On" >> $file_disk
echo "   ProxyRequests Off" >> $file_disk
echo "   SSLProxyCheckPeerCN Off" >> $file_disk
echo "   SSLProxyCheckPeerName Off" >> $file_disk
echo "   SSLProxyCACertificateFile /DATA/orthanc/$COMMON_BASENAME/disk/orthanc/external/certificates/certificate.pem" >> $file_disk
echo "   Include /etc/httpd/conf.d/apache_docker_services.conf.inc" >> $file_disk
echo "" >> $file_disk
echo "   <Location \"/$DISK_ORTHANC_WEBSITE_NAME/\">" >> $file_disk
echo "   " >> $file_disk
echo "      AuthType CAS" >> $file_disk
echo "      AuthName \"$DISK_ORTHANC_WEBSITE_NAME\"" >> $file_disk
echo "      #Require valid-user" >> $file_disk
echo "      #            Priveleged       " >> $file_disk
echo "      Require user $DISK_X_REMOTE_USER_ALLOWED_TO_TRIGGER " >> $file_disk
echo "   " >> $file_disk
echo "      Order Deny,Allow" >> $file_disk
echo "      Deny from all" >> $file_disk
echo "      Allow from $DISK_X_REMOTE_IP_ALLOWED_TO_TRIGGER" >> $file_disk
echo "" >> $file_disk
echo "      SSLRequireSSL" >> $file_disk
echo "" >> $file_disk
echo "      <If \"%{REMOTE_ADDR} == '$DISK_X_REMOTE_IP_ALLOWED_TO_TRIGGER'\">" >> $file_disk
echo "         RequestHeader set Authorization \"Basic $admin_pwd_64\"" >> $file_disk
echo "         AllowMethods reset" >> $file_disk
echo "      </If>" >> $file_disk
echo "      <Else>" >> $file_disk
echo "         AllowMethods GET HEAD CONNECT OPTIONS TRACE" >> $file_disk
echo "      </Else>" >> $file_disk
echo "" >> $file_disk
echo "      ProxyPass \"https://\${$name_disk}:8042/\"" >> $file_disk
echo "      ProxyPassReverse \"https://\${$name_disk}:8042/\"" >> $file_disk
echo "   " >> $file_disk
echo "   </Location>" >> $file_disk
echo "" >> $file_disk
echo "" >> $file_disk

