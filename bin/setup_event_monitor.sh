#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR || exit
cd ..


echo "Installing Yuyu Event Monitor Service"
yuyu_dir=`pwd -P`

echo "Yuyu dir is $yuyu_dir"

yuyu_dir_sub=${yuyu_dir//\//\\\/}
sed "s/{{yuyu_dir}}/$yuyu_dir_sub/g" "$yuyu_dir"/script/yuyu_event_monitor.service > /etc/systemd/system/yuyu_event_monitor.service

echo "Yuyu Event Monitor Service Installed on /etc/systemd/system/yuyu_event_monitor.service"
echo "Done! you can enable Yuyu Event Monitor with systemctl start yuyu_event_monitor"