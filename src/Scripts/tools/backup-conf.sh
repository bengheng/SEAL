#!/bin/bash

DTG=`date +"%y%m%d_%H%M"`

cp /usr/local/etc/dovecot/dovecot.conf $HOME/cloak/conf/dovecot.conf.$DTG
cp /usr/local/etc/dovecot/dovecot-sqlite.conf $HOME/cloak/conf/dovecot-sqlite.conf.$DTG
cp /etc/postfix/main.cf $HOME/cloak/conf/main.cf.$DTG
cp /etc/postfix/master.cf $HOME/cloak/conf/master.cf.$DTG
