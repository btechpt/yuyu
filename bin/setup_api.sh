#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR || exit
cd ..

echo "Installing Yuyu API Service"
yuyu_dir=`pwd -P`

echo "Yuyu dir is $yuyu_dir"

yuyu_dir_sub=${yuyu_dir//\//\\\/}
sed "s/{{yuyu_dir}}/$yuyu_dir_sub/g" "$yuyu_dir"/script/yuyu_api.service > /etc/systemd/system/yuyu_api.service

echo "Yuyu API Service Installed on /etc/systemd/system/yuyu_api.service"
echo "Done! you can enable Yuyu API with systemctl start yuyu_api"