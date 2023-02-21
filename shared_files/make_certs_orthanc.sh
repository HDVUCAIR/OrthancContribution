#!/bin/bash
CERT_HOST_IP_ADDRESS=`ifconfig | sed -n "s/.*addr:\([0-9\.]\+\).*255.255.*/\1/p"`
cd /media
if [ ! -d external ]; then
   mkdir external
fi
cd external
if [ ! -d certificates ]; then
   mkdir certificates
fi
cd certificates
# Generate a new cert every 350 days or so
if [ -e "certificate.pem" ]; then
   let diffInSeconds=$(date +%s)-$(date -r certificate.pem +%s)
   let diffInDays=$(expr $diffInSeconds / 86400)
   if [ "$diffInDays" -gt 350 ]; then
      rm -f certificate.pem private.key certificate.crt
   fi
fi
if [ ! -e "certificate.pem" ]; then
   if [ ! -e "private.key" ] || [ ! -e "certificate.crt" ] ; then
      rm -f private.key certificate.crt
      (echo $CERT_COUNTRY_CODE; echo $CERT_STATE_REGION; echo $CERT_CITY; echo $CERT_ORGANIZATION; echo $CERT_SURNAME; echo $CERT_HOST_IP_ADDRESS; echo $CERT_CONTACT_EMAIL; echo "") | openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out certificate.crt
   fi
   cat private.key certificate.crt > certificate.pem
fi


