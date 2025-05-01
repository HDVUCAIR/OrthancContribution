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
fileOut=$dirOut"full_d"$dayOfWeek".sql.gz"
pg_dumpall | gzip > $fileOut

if [ "$dayOfWeek" = "1" ]; then
   weekOfMonth=$((($(date +%-d)-1)/7+1))
   fileOut=$dirOut"philookup_w"$weekOfMonth".tar"
   pg_dump --format=tar -f $fileOut philookup
   fileOut=$dirOut"full_w"$weekOfMonth".sql.gz"
   pg_dumpall | gzip > $fileOut
fi

if [ "$dayOfMonth" = "01" ]; then
   monthOfYear=`date +"%m"`
   fileOut=$dirOut"philookup_m"$monthOfYear".tar"
   pg_dump --format=tar -f $fileOut philookup
   fileOut=$dirOut"full_m"$monthOfYear".sql.gz"
   pg_dumpall | gzip > $fileOut
fi

