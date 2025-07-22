from nautobot.apps.jobs import register_jobs
from .hello_world import HelloWorldJob
from .device_uptime_checker import DeviceUptimeCheck
from .interface_description_search_alpha import InterfaceDescriptionSearch
from .IPv4_check_Clive import DevicesRequirePrimaryIPv4
from .unused_interfaces import UnusedInterfacesReport
from .replace_mgmt_address import SubstituteIPWithMgmt
from .object_interaction import UpdateDeviceSerial
from .update_interface_description import UpdateIntDescription

register_jobs(
	HelloWorldJob,
	DeviceUptimeCheck,
	InterfaceDescriptionSearch,
	DevicesRequirePrimaryIPv4, 
	UnusedInterfacesReport,
	SubstituteIPWithMgmt,
	UpdateDeviceSerial,
	UpdateIntDescription
	)