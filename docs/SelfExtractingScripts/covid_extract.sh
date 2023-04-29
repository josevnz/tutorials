#!/bin/bash
# Author: Jose Vicente Nunez
SCRIPT_END=$(/bin/grep --max-count 2 --line-number ___END_OF_SHELL_SCRIPT___ "$0"| /bin/cut --field 1 --delimiter :| /bin/tail -1)|| exit 100
((SCRIPT_END+=1))
basedir=
while test -z "$basedir"; do
    read -r -p "Where do you want to extract the COVID-19 data, relative to $HOME? (example: mydata -> $HOME/mydata. Press CTRL-C to abort):" basedir
done
:<<DOC
Sanitize the user input. This is quite restrictive, so it depends of the real application requirements.
DOC
CLEAN=${basedir//_/}
CLEAN=${CLEAN// /_}
CLEAN=${CLEAN//[^a-zA-Z0-9_]/}
if [ ! -d "$HOME/$CLEAN" ]; then
    echo "[INFO]: Will try to create the directory $HOME/$CLEAN"
    if ! /bin/mkdir --parent --verbose "$HOME/$CLEAN"; then
        echo "[ERROR]: Failed to create $HOME/$CLEAN"
        exit 100
    fi
fi

/bin/tail --lines +"$SCRIPT_END" "$0"| /bin/base64 -d| /bin/tar --file - --extract --gzip --directory "$HOME/$CLEAN"

exit 0
# Here's the end of the script followed by the embedded file
___END_OF_SHELL_SCRIPT___
