#!/bin/sh -e
# NOTE: This script is provided for running once within
#    the postgres container upon launch to create the
#    orthanc user in the postresql database.

if [ -z ${PG_USER+x} ]; then PG_USER=orthanc; fi
if [ -z ${PG_DB+x} ]; then PG_DB=orthanc; fi
if [ -z ${PG_ORTHANC_PASSWORD+x} ]; then PG_ORTHANC_PASSWORD=orthanc_access; fi

export DEBIAN_FRONTEND=noninteractive

PROVISIONED_ON=/etc/orthanc_provision_on_timestamp
if [ -f "$PROVISIONED_ON" ]
then
  echo "Orthanc database was already provisioned at: $(cat $PROVISIONED_ON)"
  exit
fi

export PGUSER=postgres
psql <<- EOSQL 
CREATE USER $PG_USER WITH PASSWORD '$PG_ORTHANC_PASSWORD';
CREATE DATABASE $PG_DB WITH OWNER=$PG_USER
                                  LC_COLLATE='en_US.utf8'
                                  LC_CTYPE='en_US.utf8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;
CREATE DATABASE philookup WITH OWNER=$PG_USER
                                  LC_COLLATE='en_US.utf8'
                                  LC_CTYPE='en_US.utf8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;

EOSQL

