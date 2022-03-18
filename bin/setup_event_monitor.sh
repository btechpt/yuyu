#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR || exit
cd ..


echo "Installing Rintik API Service"
yuyu_dir=`pwd -P`

echo "Riktik dir is $yuyu_dir"

yuyu_dir_sub=${yuyu_dir//\//\\\/}
sed "s/{{yuyu_dir}}/$yuyu_dir_sub/g" "$yuyu_dir"/script/yuyu_event_monitor.service > /etc/systemd/system/yuyu_event_monitor.service

echo "Yuyu API Service Installed on /etc/systemd/system/yuyu_event_monitor.service"
echo "Done! you can enable Rintik API with systemctl start yuyu_event_monitor"