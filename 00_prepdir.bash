#!/usr/bin/bash 
# Load the environment with all our tailored settings
. .env

umask -S u=rwx,g=rx,o=

CERT_HOST_IP_ADDRESS=1.2.3.4

# Shared files
chown $POSTGRES_UID:$POSTGRES_GID ./shared_files/*.conf
chown $ORTHANC_UID:$ORTHANC_GID ./shared_files/make_certs_orthanc.sh
chown $POSTGRES_UID:102 ./shared_files/postgres.cron
chmod 600 ./shared_files/postgres.cron

# ------------------------------------------------------
# Preparation of anon disk
# ------------------------------------------------------
# Make sure data folder exists with correct uid:fid
if test -d "$ANON_HOST_DATA_DIR_ORTHANC"; then
   echo "$ANON_HOST_DATA_DIR_ORTHANC exists."
else
   echo "Creating $ANON_HOST_DATA_DIR_ORTHANC"
   mkdir -p $ANON_HOST_DATA_DIR_ORTHANC/external/certificates
   mkdir -p $ANON_HOST_DATA_DIR_ORTHANC/logs
   pushd .
   cd $ANON_HOST_DATA_DIR_ORTHANC/external/certificates
   (echo $CERT_COUNTRY_CODE; echo $CERT_STATE_REGION; echo $CERT_CITY; echo $CERT_ORGANIZATION; echo $CERT_SURNAME; echo $CERT_HOST_IP_ADDRESS; echo $CERT_CONTACT_EMAIL; echo "") | openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out certificate.crt
   cat private.key certificate.crt > certificate.pem
   popd
   chown -R $ORTHANC_UID:$ORTHANC_GID $ANON_HOST_DATA_DIR_ORTHANC
   chmod -R o-rwx $ANON_HOST_DATA_DIR_ORTHANC
fi
# Make sure data folder exists with correct uid:fid
if test -d "$ANON_HOST_DATA_DIR_POSTGRE"; then
   echo "$ANON_HOST_DATA_DIR_POSTGRE exists."
else
   echo "Creating $ANON_HOST_DATA_DIR_POSTGRE"
   mkdir -p $ANON_HOST_DATA_DIR_POSTGRE/$PG_VERSION_TAG
   mkdir -p $ANON_HOST_DATA_DIR_POSTGRE/backup
   chown -R $POSTGRES_UID:$POSTGRES_GID $ANON_HOST_DATA_DIR_POSTGRE
   chmod -R o-rwx $ANON_HOST_DATA_DIR_POSTGRE
fi

# ------------------------------------------------------
# Preparation of ANON files mapped into containers
# ------------------------------------------------------
chown $ORTHANC_UID:$ORTHANC_GID ./anon_files/mod_rest_api.py
chown $POSTGRES_UID:$POSTGRES_GID ./anon_files/postgresql-create-orthanc-user.sh
chown $POSTGRES_UID:$POSTGRES_GID ./anon_files/backup_philookup.sh
chmod ug+rwx anon_files/backup_philookup.sh
chmod o-rwx anon_files/backup_philookup.sh

# ------------------------------------------------------
# Preparation of phi disk
# ------------------------------------------------------
# Make sure data folder exists with correct uid:fid
if test -d "$PHI_HOST_DATA_DIR_ORTHANC"; then
   echo "$PHI_HOST_DATA_DIR_ORTHANC exists."
else
   echo "Creating $PHI_HOST_DATA_DIR_ORTHANC"
   mkdir -p $PHI_HOST_DATA_DIR_ORTHANC/external/certificates
   mkdir -p $PHI_HOST_DATA_DIR_ORTHANC/logs
   pushd .
   cd $PHI_HOST_DATA_DIR_ORTHANC/external/certificates
   (echo $CERT_COUNTRY_CODE; echo $CERT_STATE_REGION; echo $CERT_CITY; echo $CERT_ORGANIZATION; echo $CERT_SURNAME; echo $CERT_HOST_IP_ADDRESS; echo $CERT_CONTACT_EMAIL; echo "") | openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out certificate.crt
   cat private.key certificate.crt > certificate.pem
   popd
   chown -R $ORTHANC_UID:$ORTHANC_GID $PHI_HOST_DATA_DIR_ORTHANC
   chmod -R o-rwx $PHI_HOST_DATA_DIR_ORTHANC
fi
# Make sure data folder exists with correct uid:fid
if test -d "$PHI_HOST_DATA_DIR_POSTGRE"; then
   echo "$PHI_HOST_DATA_DIR_POSTGRE exists."
else
   echo "Creating $PHI_HOST_DATA_DIR_POSTGRE"
   mkdir -p $PHI_HOST_DATA_DIR_POSTGRE/$PG_VERSION_TAG
   mkdir -p $PHI_HOST_DATA_DIR_POSTGRE/backup
   chown -R $POSTGRES_UID:$POSTGRES_GID $PHI_HOST_DATA_DIR_POSTGRE
   chmod -R o-rwx $PHI_HOST_DATA_DIR_POSTGRE
fi

# Setup the html directory where our lookup table
#    will be written by the anonymize script
if [ ! -e "$PHI_HOST_DATA_DIR_ORTHANC/html/lookup/master" ]; then
   mkdir -p $PHI_HOST_DATA_DIR_ORTHANC/html/lookup/master
   chown -R $ORTHANC_UID:$ORTHANC_GID $PHI_HOST_DATA_DIR_ORTHANC/html
   chmod -R ug+rw,o-rwx $PHI_HOST_DATA_DIR_ORTHANC/html
fi
# Setup the scrubbing page
if [ ! -e "$PHI_HOST_DATA_DIR_ORTHANC/html/scrub" ]; then
   mkdir -p $PHI_HOST_DATA_DIR_ORTHANC/html/scrub
   chown -R $ORTHANC_UID:$ORTHANC_GID $PHI_HOST_DATA_DIR_ORTHANC/html
   chmod -R ug+rw,o-rwx $PHI_HOST_DATA_DIR_ORTHANC/html
fi

# ------------------------------------------------------
# Preparation of PHI files mapped into containers
# ------------------------------------------------------
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/mod_rest_api.py
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/base_anon_profile.json
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/orthanc.secret.json.template
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/CSVQuery.html
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/jquery.tablesorter.combined.min.js
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/style.css
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/theme.blue.min.css
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/updatelookup.html
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/study_anonymize.html
chown $ORTHANC_UID:$ORTHANC_GID ./phi_files/study_anonymize.js
chown $ORTHANC_UID:$ORTHANC_GID ${PHI_ANON_PROFILE_JSON}
chown $POSTGRES_UID:$POSTGRES_GID ./phi_files/postgresql-create-orthanc-user.sh
chown $POSTGRES_UID:$POSTGRES_GID ./phi_files/pg*
chown $POSTGRES_UID:$POSTGRES_GID ./phi_files/backup_philookup.sh
chmod ug+rwx phi_files/backup_philookup.sh
chmod o-rwx phi_files/backup_philookup.sh

# ------------------------------------------------------
# Preparation of DISK disk
# ------------------------------------------------------
# Make sure data folder exists with correct uid:fid
if test -d "$DISK_HOST_DATA_DIR_ORTHANC"; then
   echo "$DISK_HOST_DATA_DIR_ORTHANC exists."
else
   echo "Creating $DISK_HOST_DATA_DIR_ORTHANC"
   mkdir -p $DISK_HOST_DATA_DIR_ORTHANC/external/certificates
   mkdir -p $DISK_HOST_DATA_DIR_ORTHANC/logs
   pushd .
   cd $DISK_HOST_DATA_DIR_ORTHANC/external/certificates
   (echo $CERT_COUNTRY_CODE; echo $CERT_STATE_REGION; echo $CERT_CITY; echo $CERT_ORGANIZATION; echo $CERT_SURNAME; echo $CERT_HOST_IP_ADDRESS; echo $CERT_CONTACT_EMAIL; echo "") | openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out certificate.crt
   cat private.key certificate.crt > certificate.pem
   popd
   chown -R $ORTHANC_UID:$ORTHANC_GID $DISK_HOST_DATA_DIR_ORTHANC
   chmod -R o-rwx $DISK_HOST_DATA_DIR_ORTHANC
fi

# Make sure data folder exists with correct uid:fid
if test -d "$DISK_HOST_DATA_DIR_POSTGRE"; then
   echo "$DISK_HOST_DATA_DIR_POSTGRE exists."
else
   echo "Creating $DISK_HOST_DATA_DIR_POSTGRE"
   mkdir -p $DISK_HOST_DATA_DIR_POSTGRE/$PG_VERSION_TAG
   mkdir -p $DISK_HOST_DATA_DIR_POSTGRE/backup
   chown -R $POSTGRES_UID:$POSTGRES_GID $DISK_HOST_DATA_DIR_POSTGRE
   chmod -R o-rwx $DISK_HOST_DATA_DIR_POSTGRE
fi

# ------------------------------------------------------
# Preparation of DISK files mapped into containers
# ------------------------------------------------------
chown $ORTHANC_UID:$ORTHANC_GID ./disk_files/mod_rest_api.py
chown $POSTGRES_UID:$POSTGRES_GID ./disk_files/postgresql-create-orthanc-user.sh
chown $POSTGRES_UID:$POSTGRES_GID ./disk_files/backup_philookup.sh
chmod ug+rwx disk_files/backup_philookup.sh
chmod o-rwx disk_files/backup_philookup.sh

