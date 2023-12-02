# Monitoring Linux Systems With InfluxDB

InfluxDB offers very complete query capabilities, and it is also pretty good at storing time series data. On this article
I will demonstrate how you can use existing performance collection tools with InfluxDB as the storage of the captured metrics.

## What you will require for this tutorial
 
* A Docker or [Podman](https://podman.io/) installation, so you can run and instance of Influxdb; you can also do a bare metal installation, but I won't cover that here and instead will use a container.
* Influxdb 2.7.4 or better.
* A linux distribution. I used Fedora Linux.
* Python3 and [some experience writing scripts](https://www.redhat.com/sysadmin/python-scripting-intro).

## Running an Influxdb server from a container

This is maybe the easiest way to get you started; We will use an external volume to persist the data across container reboots and upgrades (please check the container page to see [all the possible options](https://hub.docker.com/_/influxdb)):

```shell=
podman pull influxdb:latest
podman run --detach --volume /data/influxdb:/var/lib/influxdb --volumne /data:/data:rw  --name influxdb_raspberrypi --restart always --publish 8086:8086 influxdb:latest --reporting-disabled
podman logs --follow influxdb_raspberrypi
```

Also, we are mapping an additional volume called /data directory inside the container, just in case we want to import some custom data later on.


## Integration with Prometheus

What is Prometheus? 

> Prometheus is an open source systems monitoring and alerting toolkit originally built at SoundCloud by ex-Googlers who wanted to monitor metrics on their servers and applications. 

The InfluxDB website has good documentation that explains [how to integrate Prometheus with InfluxDB](https://www.influxdata.com/integration/prometheus-monitoring-tool/) as the database backend/



## Integration with Glances

Prometheus is a great solution to record metrics for your hosts, but what if you are in one of the following scenarios:

1) Cannot deploy a node exporter agent because you lack the privileges
2) Want to get insight on the host performance but for limited time and don't want to deal with a formal deployment
3) You already use Glances for monitoring and want to persist this information for later analysis

### A quick demonstration of Glances

Installation is pretty simple with pip:

```shell
[josevnz@dmaf5 ~]$ python -m venv ~/virtualenv/glances
[josevnz@dmaf5 ~]$ . ~/virtualenv/glances/bin/activate
(glances) [josevnz@dmaf5 ~]$ pip install --upgrade glance
...
Successfully installed glances-3.4.0.3
```

The normally you call glances without any options, to capture stats:

```shell
# Running in standalone mode
(glances) [josevnz@dmaf5 ~]$ glance
```

![](glances-snapshot.png)

If we want to record out activity with Glances, we need to setup a InfluxDB, so it can accept our activity data.

### Creating a Glances bucket to store our activity data

First step is to connect to our InfluxDB instance and create the bucket:

```shell
josevnz@server2:~$ podman exec --tty --interactive mydb /bin/bash
root@cd378ef1f5c3:/# influx setup
> Welcome to InfluxDB 2.4.7!
? Please type your primary username josevnz
? Please type your password *********
? Please type your password again *********
? Please type your primary organization name KodeGeek
? Please type your primary bucket name glances
? Please type your retention period in hours, or 0 for infinite 0
? Setup with these parameters?
  Username:   josevnz
  Organization:KodeGeek
  Bucket:     glances
  Retention Period:  infinite
 Yes
User	Organization	Bucket
josevnz	KodeGeek	glances
root@cd378ef1f5c3:/# 
```

While inside the container we will create an access token that will be used to connect to the database:

```shell
root@cd378ef1f5c3:/# influx auth create \
  --org KodeGeek \
  --read-authorizations \
  --write-authorizations \ 
  --read-buckets \
  --write-buckets \
  --read-dashboards \
  --write-dashboards \
  --read-tasks \
  --write-tasks \
  --read-telegrafs \  
  --write-telegrafs \ 
  --read-users \
  --write-users \ 
  --read-variables \  
  --write-variables \ 
  --read-secrets \
  --write-secrets \
  --read-labels \
  --write-labels \
  --read-views \
  --write-views \
  --read-documents \  
  --write-documents \
  --read-notificationRules \ 
  --write-notificationRules \
  --read-notificationEndpoints \    
  --write-notificationEndpoints \   
  --read-checks \ 
  --write-checks \
  --read-dbrp \ 
  --write-dbrp \
  --read-annotations \
  --write-annotations \
  --read-sources \
  --write-sources \
  --read-scrapers \
  --write-scrapers \
  --read-notebooks \
  --write-notebooks \
  --read-remotes \
  --write-remotes \
  --read-replications \
  --write-replications
ID			Description	Token												User Name	User ID			Permissions
0ae9b2f1ea468000			F8y7eoaPX5gMkWvpxZ-b2LOnJjMO6gdH1ba1HfQV0dXmJm6oBekA7WsPiPk-3zhOxL8Y55_aJB1Ii-kRBDsH6w==	josevnz		0ae9b2131d868000	[read:orgs/b38ef4c091e3eca2/authorizations write:orgs/b38ef4c091e3eca2/authorizations read:orgs/b38ef4c091e3eca2/buckets write:orgs/b38ef4c091e3eca2/buckets read:orgs/b38ef4c091e3eca2/dashboards write:orgs/b38ef4c091e3eca2/dashboards read:orgs/b38ef4c091e3eca2/tasks write:orgs/b38ef4c091e3eca2/tasks read:orgs/b38ef4c091e3eca2/telegrafs write:orgs/b38ef4c091e3eca2/telegrafs read:/users write:/users read:orgs/b38ef4c091e3eca2/variables write:orgs/b38ef4c091e3eca2/variables read:orgs/b38ef4c091e3eca2/secrets write:orgs/b38ef4c091e3eca2/secrets read:orgs/b38ef4c091e3eca2/labels write:orgs/b38ef4c091e3eca2/labels read:orgs/b38ef4c091e3eca2/views write:orgs/b38ef4c091e3eca2/views read:orgs/b38ef4c091e3eca2/documents write:orgs/b38ef4c091e3eca2/documents read:orgs/b38ef4c091e3eca2/notificationRules write:orgs/b38ef4c091e3eca2/notificationRules read:orgs/b38ef4c091e3eca2/notificationEndpoints write:orgs/b38ef4c091e3eca2/notificationEndpoints read:orgs/b38ef4c091e3eca2/checks write:orgs/b38ef4c091e3eca2/checks read:orgs/b38ef4c091e3eca2/dbrp write:orgs/b38ef4c091e3eca2/dbrp read:orgs/b38ef4c091e3eca2/annotations write:orgs/b38ef4c091e3eca2/annotations read:orgs/b38ef4c091e3eca2/sources write:orgs/b38ef4c091e3eca2/sources read:orgs/b38ef4c091e3eca2/scrapers write:orgs/b38ef4c091e3eca2/scrapers read:orgs/b38ef4c091e3eca2/notebooks write:orgs/b38ef4c091e3eca2/notebooks read:orgs/b38ef4c091e3eca2/remotes write:orgs/b38ef4c091e3eca2/remotes read:orgs/b38ef4c091e3eca2/replications write:orgs/b38ef4c091e3eca2/replications]
```


## What is next

* If you are still curious about the Prometheus and InfluxDB overlapping functionalities, [you should read this comparison](https://prometheus.io/docs/introduction/comparison/).
* Source code for the Glances and InfluxDB integration can [be downloaded from here](https://github.com/josevnz/GlancesAndInfluxDB), with examples.