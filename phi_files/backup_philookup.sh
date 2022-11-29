#!/bin/bash
# NOTE: This script is copied into the postgres
#    machine to provide a regular backup of
#    the philookup table.
umask -S u=rwx,g=,o=
dayOfWeek=`date +"%u"`
dayOfMonth=`date +"%d"`
dirOut=/backup/
if [ ! -d "$dirOut" ]; then
   mkdir -p $dirOut
fi
fileOut=$dirOut"philookup_d"$dayOfWeek".tar"
pg_dump --format=tar -f $fileOut philookup

if [ "$dayOfWeek" = "1" ]; then
   weekOfMonth=$((($(date +%-d)-1)/7+1))
   fileOut=$dirOut"philookup_w"$weekOfMonth".tar"
   pg_dump --format=tar -f $fileOut philookup
fi

if [ "$dayOfMonth" = "01" ]; then
   monthOfYear=`date +"%m"`
   fileOut=$dirOut"philookup_m"$monthOfYear".tar"
   pg_dump --format=tar -f $fileOut philookup
fi

