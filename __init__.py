import psutil
import datetime
import logging

from opsdroid.skill import Skill
from opsdroid.matchers import match_always, match_crontab, match_regex

_LOGGER = logging.getLogger(__name__)


def humansize(nbytes):
    """Convert to human size taken from stackoverflow."""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes) -1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def convert_time(td):
    """Convert datetime delta to hours, minutes and seconds."""
    time = str(datetime.timedelta(seconds=td.seconds))
    hours = time.split(":")[0]
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    days = td.days

    return days, hours, minutes, seconds


class Sysanalytics(Skill):
    def __init__(self, opsdroid, config):
        super(Sysanalytics, self).__init__(opsdroid, config)
        self.commands_count = 0

        self.config = config
        self.skills = self.get_configuration('skills')
        self.connectors = self.get_configuration('connectors')
        self.parsers = self.get_configuration('parsers')
        self.databases = self.get_configuration('databases')

    def get_configuration(self, param):
        """Looks into opsdroid config and get all the active things."""
        gathered_names = ''
        if self.opsdroid.config.get(param):
            for active in self.opsdroid.config[param]:
                gathered_names += " {},".format(active['name'])
        else:
            gathered_names = "No {} active with this " \
                             "opsdroid configuration.".format(param)

        return gathered_names

    @match_always()
    async def count_command(self, message):
        """Adds command count."""
        self.commands_count += 1

    @match_regex(r'memory status')
    async def show_memory(self, message):
        """Shows how much memory is being used."""
        mem = psutil.virtual_memory()
        await message.respond(
            """
            Memory Status:
            You have a total of {total} RAM.
            Your system has {available} memory available.
            You are currently using {use} memory.
            You have {free} memory free.
            You are using {percent}% of your memory.
            """.format(
                total=humansize(mem.total),
                available=humansize(mem.available),
                use=humansize(mem.used),
                free=humansize(mem.free),
                percent=mem.percent,
            ))

    @match_regex(r'config status')
    async def show_config(self, message):
        """Shows all available configuration"""
        await message.respond("""Your opsdroid configuration is as follows:
            Logging: {logging}
            Connectors: {connectors}
            Parsers: {parsers}
            Databases: {databases}
            Skills: {skills}
            """.format(
            logging=self.opsdroid.config['logging'],
            connectors=self.connectors,
            parsers=self.parsers,
            databases=self.databases,
            skills=self.skills
        ))

    @match_regex(r'disk status')
    async def show_disk(self, message):
        """Show cpu usage."""
        disk = psutil.disk_usage('/')
        await message.respond(
            """
            Disk Status:
            The main partition on your disk is {total}.
            You have {free} available on your disk.
            You are using {used} on your disk.
            You have used {percent}% of your disk.
            """.format(
                total=humansize(disk.total),
                free=humansize(disk.free),
                used=humansize(disk.used),
                percent=disk.percent
            )
        )

    @match_regex(r'cpu status')
    async def show_cpu(self, message):
        """Show cpu usage."""
        last_boot = datetime.datetime.fromtimestamp(
            psutil.boot_time()).strftime("%d-%m-%Y at %H:%M:%S")
        running_time = datetime.datetime.now() - \
            datetime.datetime.fromtimestamp(psutil.boot_time())

        days, hours, minutes, seconds = convert_time(running_time)

        await message.respond(
            """
            CPU Status:
            Your CPU has {cores} cores.
            You are using {percent}% of your CPU.
            There are currently {processes} processes running. 
            Your machine has been running for {days} days, {hours} hours, {minutes} minutes and {seconds} seconds.
            Last reboot date was on {last_boot}.
            """.format(
                cores=psutil.cpu_count(),
                percent=psutil.cpu_percent(),
                processes=len(psutil.pids()),
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                last_boot=last_boot
            )
        )

    @match_regex(r'net status')
    async def show_net(self, message):
        """Show network status."""
        net = psutil.net_io_counters()
        await message.respond(
            """
            Network Status:
            You have sent {sent} in total.
            You have received {received} in total.
            You have sent {packets_sent} packets in total.
            You have received {packets_received} packets in total.
            """.format(
                sent=humansize(net.bytes_sent),
                received=humansize(net.bytes_recv),
                packets_sent=net.packets_sent,
                packets_received=net.packets_recv
            )
        )

        description = 'Status of each network interface: \n \n'
        networks = psutil.net_io_counters(pernic=True, nowrap=True)
        for interface, details in networks.items():
            description += "{}: Sent: {}, Received: {} \n".format(
                interface,
                humansize(details.bytes_sent),
                humansize(details.bytes_recv))

        await message.respond(description)

    @match_regex(r'all status')
    async def show_status(self, message):
        """Shows collected status."""
        await message.respond("You have run {} commands since opsdroid "
                              "has been running".format(self.commands_count))

        await self.show_config(message)
        await self.show_memory(message)
        await self.show_disk(message)
        await self.show_cpu(message)
        await self.show_net(message)

    @match_crontab('* * * * *', timezone="Europe/London")
    async def minutely_status(self, message):
        """Puts status in db every minute."""
        time = datetime.datetime.now()
        date = "{}-{}-{}".format(time.day, time.month, time.year)
        hours = "{}:{}".format(time.hour, time.minute, )
        mem = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent()
        ram_usage = mem.percent

        if self.opsdroid.config.get('databases'):
            status = await self.opsdroid.memory.get("status")
            if not status:
                status = {}

            if not status.get(date, None):
                status[date] = []
            status[date].append({"Time": hours, "CPU": cpu_usage, "RAM": ram_usage})

            await self.opsdroid.memory.put("status", status)

        if self.config.get('log-usage'):
            _LOGGER.info("{} - CPU usage: {}% | RAM usage: {}%".format(
                hours, cpu_usage, ram_usage))
