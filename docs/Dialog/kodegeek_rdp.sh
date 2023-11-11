#!/bin/bash
# author Jose Vicente Nunez
# Do not use this script on a public computer. It is not secure...
# https://invisible-island.net/dialog/
: ${DIALOG_OK=0}
: ${DIALOG_CANCEL=1}
: ${DIALOG_HELP=2}
: ${DIALOG_EXTRA=3}
: ${DIALOG_ITEM_HELP=4}
: ${DIALOG_ESC=255}
declare tmp_file=$(/usr/bin/mktemp 2>/dev/null) || declare tmp_file=/tmp/test$$
trap "/bin/rm -f $tmp_file" 0 1 2 5 15 EXIT INT
/bin/chmod go-wrx ${tmp_file} > /dev/null 2>&1

declare TITLE=$(/usr/bin/jq --compact-output --raw-output '.title' $HOME/.config/scripts/kodegeek_rdp.json)|| exit 100
declare REMOTE_USER=$(/usr/bin/jq --compact-output --raw-output '.remote_user' $HOME/.config/scripts/kodegeek_rdp.json)|| exit 100
declare MACHINES=$(
    declare tmp_file2=$(/usr/bin/mktemp 2>/dev/null) || declare tmp_file2=/tmp/test$$
    # trap "/bin/rm -f $tmp_file2" 0 1 2 5 15 EXIT INT
    declare -a MACHINE_INFO=$(/usr/bin/jq --compact-output --raw-output '.machines[]| join(",")' $HOME/.config/scripts/kodegeek_rdp.json > $tmp_file2)
    declare -i i=0
    while read line; do
        declare machine=$(echo $line| /usr/bin/cut -d',' -f1)
        declare desc=$(echo $line| /usr/bin/cut -d',' -f2)
        declare toggle=off
        if [ $i -eq 0 ]; then
            toggle=on
            ((i=i+1))
        fi
        echo $machine $desc $toggle
    done < $tmp_file2
    /bin/cp /dev/null $tmp_file2
) || exit 100
/usr/bin/dialog \
    --clear \
    --title "$TITLE" \
    --radiolist "Which machine do you want to use?" 20 61 2 \
    $MACHINES 2> ${tmp_file}
return_value=$?

export remote_machine=""
case $return_value in
  $DIALOG_OK)
    export remote_machine=$(/bin/cat ${tmp_file})
    ;;
  $DIALOG_CANCEL)
    echo "Cancel pressed.";;
  $DIALOG_HELP)
    echo "Help pressed.";;
  $DIALOG_EXTRA)
    echo "Extra button pressed.";;
  $DIALOG_ITEM_HELP)
    echo "Item-help button pressed.";;
  $DIALOG_ESC)
    if test -s $tmp_file ; then
      /bin/rm -f $tmp_file
    else
      echo "ESC pressed."
    fi
    ;;
esac

if [ -z "${remote_machine}" ]; then
  /usr/bin/dialog \
  	--clear  \
	--title "Error, no machine selected?" --clear "$@" \
       	--msgbox "No machine was selected!. Will exit now..." 15 30
  exit 100
fi

/bin/ping -c 4 ${remote_machine} >/dev/null 2>&1
if [ $? -ne 0 ]; then
  /usr/bin/dialog \
  	--clear  \
	--title "VPN issues or machine is off?" --clear "$@" \
       	--msgbox "Could not ping ${remote_machine}. Time to troubleshoot..." 15 50
  exit 100
fi

/bin/rm -f ${tmp_file}
/usr/bin/dialog \
  --title "$TITLE" \
  --clear  \
  --insecure \
  --passwordbox "Please enter your Windows password for ${remote_machine}\n" 16 51 2> $tmp_file
return_value=$?
case $return_value in
  $DIALOG_OK)
    /usr/bin/mkdir -p -v $HOME/logs
    /usr/bin/xfreerdp /cert-ignore /sound:sys:alsa /f /u:$REMOTE_USER /v:${remote_machine} /p:$(/bin/cat ${tmp_file})| \
    /usr/bin/tee $HOME/logs/$(/usr/bin/basename $0)-$remote_machine.log
    ;;
  $DIALOG_CANCEL)
    echo "Cancel pressed.";;
  $DIALOG_HELP)
    echo "Help pressed.";;
  $DIALOG_EXTRA)
    echo "Extra button pressed.";;
  $DIALOG_ITEM_HELP)
    echo "Item-help button pressed.";;
  $DIALOG_ESC)
    if test -s $tmp_file ; then
      /bin/rm -f $tmp_file
    else
      echo "ESC pressed."
    fi
    ;;
esac
