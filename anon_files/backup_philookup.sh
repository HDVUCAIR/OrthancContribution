#!/bin/bash
set -x
# NOTE: Makes full logical backup of postgres
umask -S u=rwx,g=,o=
dayOfWeek=`date +"%u"`
dayOfMonth=`date +"%d"`
dirOut=/backup/
if [ ! -d "$dirOut" ]; then
   mkdir -p $dirOut
fi
fileOut=$dirOut"full_d"$dayOfWeek".sql.gz"
pg_dumpall | gzip > $fileOut

if [ "$dayOfWeek" = "1" ]; then
   weekOfMonth=$((($(date +%-d)-1)/7+1))
   fileOut=$dirOut"full_w"$weekOfMonth".sql.gz"
   pg_dumpall | gzip > $fileOut
fi

if [ "$dayOfMonth" = "01" ]; then
   monthOfYear=`date +"%m"`
   fileOut=$dirOut"full_m"$monthOfYear".sql.gz"
   pg_dumpall | gzip > $fileOut
fi

