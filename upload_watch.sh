#!/bin/bash

echo "Start"
inotifywait -m /home/silas/PhotoFrame/Images -e create -e moved_to --include '.*\.jpg$' |
while read -r dictonary action file; do
	echo "Check COPY"
	if [[ "$file" != *shot* ]]; then
		echo "COPY"
		rclone copy "/home/silas/PhotoFrame/Images" "AS_Wedding:album/AS_Wedding"
	else
		echo "No COPY"
	fi
done

