# Yuyu

Yuyu provide ability to manage openstack billing by listening to every openstack event. Yuyu is a required component to use Yuyu Dashboard. There are 3 main component in Yuyu: API, Cron, Event Monitor 

## Yuyu API
Main component to communicate with Yuyu Dashboard.

## Yuyu Cron
Provide invoice calculation and rolling capabilities that needed to run every month.

## Yuyu Event Monitor
Monitor event from openstack to calculate billing spent.

# System Requirement
- Python 3
- Openstack
- Virtualenv
- Linux environment with Systemd

# Pre-Installation

### Virtualenv
Make sure you installed virtualenv before installing Yuyu

```bash
pip3 install virtualenv
```

### Timezone

Billing is a time sensitive application, please make sure you set a correct time and timezone on you machine.

### Openstack Service Notification
You need to enable notification for this openstack service:
- Nova (nova.conf)
- Cinder (cinder.conf)
- Neutron (neutron.conf)
- Keystone (keystone.conf)

### Nova
Add configuration below on `[oslo_messaging_notifications]`

```
driver = messagingv2 
topics = notifications
```

Add configuration below on `[notifications]`

```
notify_on_state_change = vm_and_task_state
notification_format = unversioned
```

### Cinder & Neutron & Keystone

Add configuration below on `[oslo_messaging_notifications]`

```
driver = messagingv2 
topics = notifications
```

### Kolla Note
If you using Kolla, please add configuration above on all service container. For example on Nova you should put the config on `nova-api`, `nova-scheduler`, etc.

# Installation

Clone the latest source code and put it on any directory you want. Here i assume you put it on `/var/yuyu/`

```bash
cd /var/yuyu/
git clone {repository}
cd yuyu
```

Then create virtualenv and activate it
```bash
virtualenv env --python=python3.8
source env/bin/activate
pip install -r requirements.txt
```

Then create a configuration file, just copy from sample file and modify as your preference.

```bash
cp yuyu/local_settings.py.sample yuyu/local_settings.py
```

Please read [Local Setting Configuration](#local-setting-configuration) to get to know about what configuration you should change.

Then run the database migration

```bash
python manage.py migrate
```

Then create first superuser

```bash
python manage.py createsuperuser
```

## Local Setting Configuration

### YUYU_NOTIFICATION_URL (required)
A Messaging Queue URL that used by Openstack, usually it is a RabbitMQ URL.

Example: 
```
YUYU_NOTIFICATION_URL = "rabbit://openstack:password@127.0.0.1:5672/"
```

### YUYU_NOTIFICATION_TOPICS (required)
A list of topic notification topic that is configured on each openstack service

Example: 
```
YUYU_NOTIFICATION_TOPICS = ["notifications"]
```


### DATABASE
By default, it will use Sqlite. If you want to change it to other database please refer to Django Setting documentation.

- https://docs.djangoproject.com/en/3.2/ref/settings/#databases
- https://docs.djangoproject.com/en/3.2/ref/databases/

## API Installation

To install Yuyu API, you need to execute this command.

```bash
./bin/setup_api.sh
```

This will install `yuyu_api` service

To start the service use this command
```bash
systemctl enable yuyu_api
systemctl start yuyu_api
```

An API server will be open on port `8182`. 

## Event Monitor Installation

To install Yuyu API, you need to execute this command.

```bash
./bin/setup_event_monitor.sh
```


This will install `yuyu_event_monitor` service

To start the service use this command
```bash
systemctl enable yuyu_event_monitor
systemctl start yuyu_event_monitor
```

## Cron Installation

There is a cronjob that needed to be run every month on 00:01 AM. This cronjob will finish all in progress invoice and start new invoice for the next month.

To install it, you can use `crontab -e`.

Put this expression on the crontab

```
1 0 1 * * $yuyu_dir/bin/process_invoice.sh 
```

Replace $yuyu_dir with the directory of where yuyu is located. Example
```
1 0 1 * * /var/yuyu/bin/process_invoice.sh
```

# Updating Yuyu

To update Yuyu manually, you can just pull the latest code

```bash
git pull release/xx.xx
```

Activate the virtualenv.

```bash
source env/bin/activate
```

Change the setting if needed. 

```bash
nano yuyu/local_settings.py
```

Update the python package.

```bash
pip install -r requirements.txt
```

Run database migration

```bash
python manage.py migrate
```

Restart all the service

```bash
systemctl restart yuyu_api
systemctl restart yuyu_event_monitor
```