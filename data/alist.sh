#!/bin/bash

# Fetches all created aliases from the log database, along with their time of creation;

if [ $# -ne 1 ]
then
	echo "Usage: $0 <outfile>"
	exit 0
fi

sqlite3 logdb 'select * from mail where mid in (select mid+1 from mail where rcpttos="getalias@cloak.dyndns-mail.com");' | grep -o "[a-zA-Z0-9]*\.........@cloak.dyndns-mail.com" | sort | uniq > $1

cat /dev/null > /tmp/aliastimestamps.tmp

for alias in `cat $1`;do
	sqlite3 logdb "select timestamp from mail where mid in (select mid+1 from mail where rcpttos='getalias@cloak.dyndns-mail.com') and data like '%$alias%' order by timestamp asc limit 1" >> /tmp/aliastimestamps
done

paste $1 /tmp/aliastimestamps > /tmp/atime.out
#paste $1 /tmp/aliastimestamps | nawk -F'\t' '{ printf("%-55s %s\n", $1, $2) }' > /tmp/atime.out
rm /tmp/aliastimestamps
rm $1
mv /tmp/atime.out ./$1

