# Monitoring Linux Systems With InfluxDB

InfluxDB offers very complete query capabilities, and it is also pretty good at storing time series data. On this article
I will demonstrate how you can use existing performance collection tools with InfluxDB as the storage of the captured metrics.

## What you will require for this tutorial
 
* A Docker or [Podman](https://podman.io/) installation, so you can run the Influxdb; you can also do a bare metal installation, but I won't cover that here and instead will use Podman.
* Influxdb 2.4.0 or better.
* A linux distribution. I used Fedora Linux.
* Python3 and [some experience writing scripts](https://www.redhat.com/sysadmin/python-scripting-intro).

## Running an Influxdb server from a container

This is maybe the easiest way to get you started; We will use an external volume to persist the data across container reboots and upgrades (please check the container page to see [all the possible options](https://hub.docker.com/_/influxdb)):

```shell=
podman pull influxdb:latest
podman run --detach --volume /data/influxdb:/var/lib/influxdb --volumne /data:/data:rw  --name influxdb_raspberrypi --restart always --publish 8086:8086 influxdb:latest
podman logs --follow influxdb_raspberrypi
```

Also, we are mapping an additional volume called /data directory inside the container, to import some CSV files later.


## Integration with Prometheus

What is Prometheus? 

> Prometheus is an open source systems monitoring and alerting toolkit originally built at SoundCloud by ex-Googlers who wanted to monitor metrics on their servers and applications. 

The InfluxDB website has good documentation that explains [how to integrate Prometheus with InfluxDB](https://www.influxdata.com/integration/prometheus-monitoring-tool/) as the database backend/



## Integration with Glances

Prometheus is a great solution to record metrics for your hosts, but what if you are in one of the following scenarios:

1) Cannot deploy a node exporter agent because you lack the privileges
2) Want to get insight on the host performance but for limited time and don't want to deal with a formal deployment



## What is next

* If you are still curious about the Prometheus and InfluxDB overlapping functionalities, [you should read this comparison](https://prometheus.io/docs/introduction/comparison/).
* Source code for the Glances and InfluxDB integration can [be downloaded from here](https://github.com/josevnz/GlancesAndInfluxDB), with examples.