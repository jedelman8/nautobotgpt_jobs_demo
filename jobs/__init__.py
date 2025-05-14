from nautobot.apps.jobs import register_jobs
from .hello_world import HelloWorldJob
from .device_uptime_checker import DeviceUptimeCheck


register_jobs(
	HelloWorldJob,
	DeviceUptimeCheck
	)