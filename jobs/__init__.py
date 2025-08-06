from nautobot.apps.jobs import register_jobs
from .ngpt_demos import (
    DeviceUptimeCheck,
    HelloWorldJob,
    InterfaceDescriptionSearch,
    UpdateIntDescription,
    UnusedInterfacesReport,
    UpdateDeviceSerial,
    DevicesRequirePrimaryIPv4,
    RemediateVulnJob,
)

register_jobs(
    HelloWorldJob,
    DeviceUptimeCheck,
    InterfaceDescriptionSearch,
    DevicesRequirePrimaryIPv4,
    UnusedInterfacesReport,
    UpdateDeviceSerial,
    UpdateIntDescription,
    RemediateVulnJob,
)
