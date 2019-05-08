# opsdroid skill sysanalytics

This skill will keep track of your system while [opsdroid](https://github.com/opsdroid/opsdroid) is running.

## Requirements

- psutils

## Configuration

```yaml
- name: sysanalytics
  log-usage: true #optional

```

## Usage

#### `memory status`

Shows the status of the virtual memory.

> user: memory status
>
> opsdroid: Memory Status:
            You have a total of 8 GB RAM.
            Your system has 2.12 GB memory available.
            You are currently using 4.32 GB memory.
            You have 79.98 MB memory free.
            You are using 73.5% of your memory.

#### `config status`

Shows the current configuration of opsdroid - it will only return the names of 
skills, connectors and databases, all the rest will be hidden.

> user: config status
>
> opsdroid: Your opsdroid configuration is as follows:
            Logging: {'level': 'debug', 'console': True}
            Connectors:  shell, websocket, telegram,
            Parsers:  regex,
            Databases:  sqlite,
            Skills:  sysanalytics, hello, seen, dance, loudnoises,

#### `disk status`

Shows the status of the main partition of the disk. 

_Note: If you would like to get details from all partitions let me know and I'll add it._

> user: disk status
>
> opsdroid: Disk Status:
            The main partition on your disk is 112.2 GB.
            You have 14.26 GB available on your disk.
            You are using 94.29 GB on your disk.
            You have used 86.9% of your disk.

#### `cpu status`

Shows the status of the cpu, how many processes are running at the moment and 
for how long have your machine been running.

_Note: If you would like to get details from all partitions let me know and I'll add it._

> user: cpu status
>
> opsdroid: CPU Status:
            Your CPU has 4 cores.
            You are using 53.6% of your CPU.
            There are currently 448 processes running. 
            Your machine has been running for 12 days, 1 hours, 0 minutes and 14 seconds.
            Last reboot date was on 28-03-2019 at 18:59:12.

#### `net status`

Shows the status for the network. It will show how much have you sent and received through network, 
it will also shows details of every network interface separately.

> user: net status
>
> opsdroid: Network Status:
            You have sent 2.35 GB in total.
            You have received 16.23 GB in total.
            You have sent 7947411 packets in total.
            You have received 13882217 packets in total.
            Status of each network interface: 
            lo0: Sent: 1.28 GB, Received: 1.28 GB 
            ...
            
#### `all status`

Show all status with a single command. It will also tell you how many commands have you sent to opsdroid.

_Note: Since all the skills are being called again, it might take a while for opsdroid to answer._

> user: net status
>
> opsdroid: You have run 1 commands since opsdroid has been running
            Your opsdroid configuration is as follows:
            ...
            Memory Status:
            ...
            Disk Status:
            ...
            CPU Status:
            ...
            Network Status:
            ...

#### Cron job - every minute

A cron job is being run every minute that's meant to work with a database. It will add to
the database the current usage of your CPU and Ram. The data structure will look like this:

```json
{
  "9-4-2019": [
    {"Time": "20:39", "CPU": 26.0, "RAM": 71.7}, 
    {"Time": "20:40", "CPU": 20.0, "RAM": 74.1}, 
    {"Time": "20:41", "CPU": 33.6, "RAM": 73.2}, 
    {"Time": "20:42", "CPU": 23.8, "RAM": 73.4}, 
    {"Time": "20:43", "CPU": 14.3, "RAM": 71.6}, 
    {"Time": "20:44", "CPU": 10.0, "RAM": 66.9}
  ]
}
```

Also, if ou have the flag `log-usage` the cron job will log the current usage of your CPU and RAM like this:

```INFO opsdroid-modules.skill.sysanalytics: 20:18 - CPU usage: 25.7% RAM usage: 77.0%```


#### `daily graph`

Gets details of the day from the database and saves the percentage of the RAM and CPU usage as a graph.


> user: daily graph
>
> opsdroid: Done, saved file Daily_graph_10-4-2019


#### `get graph 8-5-2019`

Saves the graph of a specific date to file. If there is no status available opsdroid will log the attempt 
and show you which ones are available.

> user: get graph 12-4-2019
>
> opsdroid: Done, saved file graph_from_12-4-2019
>
>
> user: get graph 1-4-2019
>
> opsdroid> INFO opsdroid-modules.skill.sysAnalytics: Unable to find details for 1-4-2019, we only have these dates in memory - 10-4-2019 12-4-2019 8-5-2019
