from nautobot.apps.jobs import register_jobs
from .hello_world import HelloWorldJob
from .device_uptime_checker import DeviceUptimeCheck
from .interface_description_search_alpha import InterfaceDescriptionSearch
from .ipv4_check import DevicesRequirePrimaryIPv4

register_jobs(
	HelloWorldJob,
	DeviceUptimeCheck,
	InterfaceDescriptionSearch,
	DevicesRequirePrimaryIPv4
	)