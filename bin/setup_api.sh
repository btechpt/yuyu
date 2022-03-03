#!/bin/bash

echo "Installing Rintik API Service"
rintik_dir=`pwd -P`

echo "Riktik dir is $rintik_dir"

rintik_dir_sub=${rintik_dir//\//\\\/}
sed "s/{{rintik_dir}}/$rintik_dir_sub/g" "$rintik_dir"/script/rintik_api.service > /etc/systemd/system/rintik_api.service

echo "Rintik API Service Installed on /etc/systemd/system/rintik_api.service"
echo "Done! you can enable Rintik API with systemctl start rintik_api"