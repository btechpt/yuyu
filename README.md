
# Rintik

Rintik provide ability to manage openstack billing by listening to every openstack event. Rintik is a required component to use Rintik Dashboard. There are 3 main component in Rintik: API, Cron, Event Monitor 

## Rintik API
Main component to communicate with Rintik Dashboard.

## Rintik Cron
Provide invoice calculation and rolling capabilities that needed to run every month.

## Rintik Event Monitor
Monitor event from openstack to calculate billing spent.

# System Requirement
- Python 3
- Openstack
- Virtualenv
- Linux environment with Systemd

# Pre-Installation

### Virtualenv
Make sure you installed virtualenv before installing Rintik

```bash
pip3 install virtualenv
```

### Openstack Service Notification
You need to enable notification for this openstack service:
- Nova (nova.conf)
- Cinder (cinder.conf)
- Neutron (neutron.conf)

### Nova
Add configuration below on `[oslo_messaging_notifications]`

```
driver = messagingv2 
topics = notifications
```

Add configuration below on `[notifications]`

``
notify_on_state_change = vm_and_task_state
notification_format = unversioned
``

### Cinder & Neutron

Add configuration below on `[oslo_messaging_notifications]`

```
driver = messagingv2 
topics = notifications
```

### Kolla Note
If you using Kolla, please add configuration above on all service container. For example on Nova you should put the config on `nova-api`, `nova-scheduler`, etc.

# Installation

Clone the latest source code and put it on any directory you want. Here i assume you put it on `/var/rintik/`

```bash
cd /var/rintik/
git clone {repository}
cd rintik
```

Then create virtualenv and activate it
```bash
virtualenv env --python=python3.8
source env/bin/activate
pip install -r requirements.txt
```

Then create a configuration file, just copy from sample file and modify as your preference.

```bash
cp core/local_settings.py.sample core/local_settings.py
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

### RINTIK_NOTIFICATION_URL (required)
A Messaging Queue URL that used by Openstack, usually it is a RabbitMQ URL.

Example: 
```
RINTIK_NOTIFICATION_URL = "rabbit://openstack:password@127.0.0.1:5672/"
```

### RINTIK_NOTIFICATION_TOPICS (required)
A list of topic notification topic that is configured on each openstack service

Example: 
```
RINTIK_NOTIFICATION_TOPICS = ["notifications"]
```


### DATABASE
By default, it will use Sqlite. If you want to change it to other database please refer to Django Setting documentation.

- https://docs.djangoproject.com/en/3.2/ref/settings/#databases
- https://docs.djangoproject.com/en/3.2/ref/databases/

## API Installation

To install Rintik API, you need to execute this command.

```bash
./bin/setup_api.sh
```

This will install `rintik_api` service

To start the service use this command
```bash
systemctl enable rintik_api
systemctl start rintik_api
```

An API server will be open on port `8182`. 

## Event Monitor Installation

To install Rintik API, you need to execute this command.

```bash
./bin/setup_event_montor.sh
```


This will install `rintik_event_monitor` service

To start the service use this command
```bash
systemctl enable rintik_event_monitor
systemctl start rintik_event_monitor
```

## Cron Installation

There is a cronjob that needed to be run every month on 00:01 AM. This cronjob will finish all in progress invoice and start new invoice for the next month.

To install it, you can use `crontab -e`.

Put this expression on the crontab

```
1 0 1 * * $rintik_dir/bin/process_invoice.sh 
```

Replace $rintik_dir with the directory of where rintik is located. Example
```
1 0 1 * * /etc/rintik/bin/process_invoice.sh
```