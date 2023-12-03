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

Our running container is called 'influxdb_raspberrypi', and with the `podman logs` command we do a quick check to make sure there are no errors. 


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

First step is to connect to our InfluxDB instance and create a bucket, I called mine `glances`.

Most likely you already have several buckets in your InfluxDB database, we will create a new  bucket.

Get inside the influxdb_raspberrypi running container we will create a bucket, with a retention policy to keep our data forever:

```shell
josevnz@raspberrypi:~$ podman exec --tty --interactive influxdb_raspberrypi /bin/bash
root@raspberrypi:/# influx bucket create --org Kodegeek --name glances  --description 'Glances storage' --retention 0
ID			Name	Retention	Shard group duration	Organization ID		Schema Type
305430cf2f5de6fd	glances	infinite	168h0m0s		c334619ae2cd7b3d	implicit
```

Our bucket has the id '305430cf2f5de6fd'. We will use that to create an authorization token we can use to insert/ read data remotely from Glances:


```shell
josevnz@raspberrypi:~$ podman exec --tty --interactive influxdb_raspberrypi /bin/bash
root@raspberrypi:/# influx auth create --org Kodegeek --description 'Authorization for Glances' --write-bucket 305430cf2f5de6fd --read-bucket 305430cf2f5de6fd --write-buckets --read-buckets
ID			Description			Token												User Name	User ID			Permissions
0c37feccff400000	Authorization for Glances	UnmEgl1HQ7AiZB8_QrCJFYkm2tE_e82_Sd9jnkrMsj1nA0YONpazx2HHuoPK3b_GnP7WX2qNURDnUfvcQyfagw==	josevnz		09ff917433270000	[read:orgs/c334619ae2cd7b3d/buckets/305430cf2f5de6fd write:orgs/c334619ae2cd7b3d/buckets/305430cf2f5de6fd read:orgs/c334619ae2cd7b3d/buckets write:orgs/c334619ae2cd7b3d/buckets]
```

Here we got the authorization token 'UnmEgl1HQ7AiZB8_QrCJFYkm2tE_e82_Sd9jnkrMsj1nA0YONpazx2HHuoPK3b_GnP7WX2qNURDnUfvcQyfagw=='. We will use it in our Glances configuration file:

Then we need to bridge glances with InfluxDB. For that we can add the following to the Glances configuration file:

```shell
mkdir ~/.config/glances/
/bin/cat<<GLANCES>~/.config/glances/glances.conf
[global]
refresh=2
check_update=false
history_size=28800
[influxdb2]
# server2 is where InfluxDB is running
host=raspberrypi
port=8086
protocol=http
org=KodeGeek
bucket=glances
# And here you put the token we generated on the previous step
token=UnmEgl1HQ7AiZB8_QrCJFYkm2tE_e82_Sd9jnkrMsj1nA0YONpazx2HHuoPK3b_GnP7WX2qNURDnUfvcQyfagw==
GLANCES
```

Now we just need to run Glances again:

```shell
. ~/virtualenv/glances/bin/activate
# Refresh every 5 seconds, export to influxdb2
glances --time 5 --export influxdb2
```

Make sure that you have set up your authorization configuration properly. On the InfluxDB container you should not see these:

```shell
podman logs --follow influxdb_raspberrypi
2023-12-03T13:10:49.944038Z	info	Unauthorized	{"log_id": "0lVhMguW000", "error": "authorization not found"}
2023-12-03T13:11:33.357711Z	info	Unauthorized	{"log_id": "0lVhMguW000", "error": "token required"}
```

Optionally you could run [tshark](https://tshark.dev/analyze/packet_hunting/packet_hunting/) and confirm that glances is making POST requests to the InfluxDB endpoint:

```shell
[josevnz@dmaf5 ~]$ tshark -i eno1 -Y http.request -f "host 192.168.68.60 and tcp port 8086"
Capturing on 'eno1'
 ** (tshark:18229) 09:58:47.993686 [Main MESSAGE] -- Capture started.
 ** (tshark:18229) 09:58:47.994375 [Main MESSAGE] -- File: "/var/tmp/wireshark_eno19kN1jG.pcapng"
   11 2.690111928 192.168.68.73 → 192.168.68.60 HTTP 881 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
   24 3.824977400 192.168.68.73 → 192.168.68.60 HTTP 891 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
   37 4.128239147 192.168.68.73 → 192.168.68.60 HTTP 901 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
   51 5.872746588 192.168.68.73 → 192.168.68.60 HTTP 907 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
   71 6.120250641 192.168.68.73 → 192.168.68.60 HTTP 868 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
   91 6.503915790 192.168.68.73 → 192.168.68.60 HTTP 870 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
  104 7.838737858 192.168.68.73 → 192.168.68.60 HTTP 883 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)
  117 8.576475158 192.168.68.73 → 192.168.68.60 HTTP 884 POST /api/v2/write?org=Kodegeek&bucket=glances&precision=ns HTTP/1.1  (text/plain)

```

At 'glance' not much is happening (_pun intended_) but if we go to the InfluxDB data explorer we will see a new bucket there, along with few collections:

![](influxdb-glances-capture.png)

This particular time series shows memory utilization over time, where Glances is running.

## What did we learn

* If you are still curious about the Prometheus and InfluxDB overlapping functionalities, [you should read this comparison](https://prometheus.io/docs/introduction/comparison/).
* We used tshark for troubleshooting. This tool [is a must](https://tshark.dev/) in your back of tricks. 
* Source code for the Glances and InfluxDB integration can [be downloaded from here](https://github.com/josevnz/GlancesAndInfluxDB), with examples.