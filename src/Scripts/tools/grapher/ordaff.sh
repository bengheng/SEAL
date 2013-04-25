#!/bin/bash

cat affiliations | \
	awk 'BEGIN{FS=","}{ for (i = 1; i <= NF; i++) print $i }' | \
	awk 'BEGIN{FS="."}{ for (i = 1; i < NF; i++) print $i }' | \
	sort | \
	sed -e '/^com$/Id;/^us$/Id;/^bounce$/Id;/^bounces$/Id;/^co$/Id;/^gov$/Id;/^list$/Id;/^lists$/Id;/^listserv$/Id'
