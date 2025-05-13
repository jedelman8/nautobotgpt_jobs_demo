from nautobot.apps.jobs import register_jobs
from .hello_world import HelloWorldJob
from .duplicate_ip_check import CheckDuplicateIPAddresses
from .device_uptime_checker import DeviceUptimeCheck


register_jobs(
	HelloWorldJob,
	CheckDuplicateIPAddresses,
	DeviceUptimeCheck
	)