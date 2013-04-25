#!/bin/bash

# Fetches all messages to the passed alias address, returning their timestamps and subjects;

if [ $# -ne 2 ]
then
	echo "Usage: $0 <recipient address> <outfile>"
	exit 0
fi

mkfifo /tmp/cloakfifo 2>/dev/null

sqlite3 logdb "select timestamp, data from mail where data like '%Using hacked smtplib.py%' and data like '%$1%' and data not like '%getalias@cloak.dyndns-mail.com%'" | tee /tmp/cloakfifo | grep -Eo "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\|" | sed -e 's/\(.*\)|/\1/' > /tmp/tstamp.out &

#sqlite3 logdb "select timestamp, data from mail where rcpttos LIKE '%$1%';" | tee /tmp/cloakfifo | grep -Eo "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\|" | sed -e 's/\(.*\)|/\1/' > /tmp/tstamp.out &
#sed -e '{:main /[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}|/ s/^Subject: \(.*\)/\1/\n b main}' < /tmp/cloakfifo > /tmp/msgsubj.out
sed -nre '
/[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\|/ x
/\\nSubject: .*\\r\\n/ x
s/[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\|//
t dosub
b

:dosub
x
s/^Subject: (.*)/\1/p
s/.*//
x
' < /tmp/cloakfifo > /tmp/msgsubj.out

# Wait for bg proc to finish
while grep -q "Running" <(jobs %+)
do
	sleep 1
done

rm /tmp/cloakfifo

if [ -c /tmp/tstamp2.out ]
then
	rm /tmp/tstamp2.out
fi

echo -e "\c" > /tmp/tstamp2.out

TEMPIFS=$IFS
IFS=$'\n'
for cur in `cat /tmp/tstamp.out`
do
	date -d "$cur UTC" +'%d-%b-%Y %k:%M:%S' >> /tmp/tstamp2.out
done
IFS=$TEMPIFS

echo -e "Correspondence results for address '$1':\n" > $2
paste /tmp/tstamp2.out /tmp/msgsubj.out >> $2

#create the daycounts file
echo -e "\c" > /tmp/daycounts.out #-e "Alias: '$1'\n" > /tmp/daycounts.out


i=0
#sdate=`grep -oE -m1 "[0-9]{2}-.*-[0-9]{4}" /tmp/tstamp2.out`
sdate='20-Jul-2011'
while [ `date -d "$sdate + $i day" +"%d-%b-%Y"` != `date -d "today" +"%d-%b-%Y"` ]
do
	#echo -e "`date -d "$sdate + $i day" +"%d-%b-%Y"`\t\c" >> /tmp/daycounts.out
	grep -c `date -d "$sdate + $i day" +"%d-%b-%Y"` /tmp/tstamp2.out | sed -re "s/([0-9]*)/\1, /" | tr -d '\n' >> /tmp/daycounts.out
	(( i += 1 ))
done

#echo -e "`date -d "$sdate + $i day" +"%d-%b-%Y"`\t\c" >> /tmp/daycounts.out
grep -c `date -d "$sdate + $i day" +"%d-%b-%Y"` /tmp/tstamp2.out | sed -re "s/([0-9]*)/\1, /" | tr -d '\n' >> /tmp/daycounts.out

echo -e "" >> /tmp/daycounts.out

cat /tmp/daycounts.out >> ./daycounts.out
#mv /tmp/daycounts.out ./daycounts.out

rm /tmp/tstamp.out /tmp/tstamp2.out /tmp/msgsubj.out

