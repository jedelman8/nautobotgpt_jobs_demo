from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models import Device, Interface, Location
from nautobot.extras.models import DeviceRole

class UnusedInterfacesReport(Job):
    """
    Generate a report of unused interfaces for all devices of a given
    role within a specified location.

    An "unused" interface is defined as:
      - Not connected to a cable (no .cable or .connected_endpoint)
      - Not a member of a LAG (lag is None)
      - Not assigned any IP address
    """

    location = ObjectVar(
        model=Location,
        description="Location to search for devices.",
        required=True
    )
    role = ObjectVar(
        model=DeviceRole,
        description="Device Role to filter devices.",
        required=True
    )

    class Meta:
        name = "Unused Interfaces Report"
        description = "List all unused interfaces in a location and by device role."

    def run(self, location, role):
        unused_report = []
        # Filter devices by role and location
        devices = Device.objects.filter(role=role, location=location)

        if not devices.exists():
            self.logger.warning(
                "No devices found for role %s in location %s.",
                role.name, location.name
            )
            return "No devices matched."

        for device in devices:
            unused_interfaces = []
            interfaces = Interface.objects.filter(device=device)

            for iface in interfaces:
                if (
                    iface.lag is None and
                    iface.cable is None and
                    not iface.connected_endpoint and
                    not iface.ip_addresses.exists()
                ):
                    unused_interfaces.append(iface.name)
                    self.logger.info(
                        "Device %s unused interface: %s", device.name, iface.name
                    )

            if unused_interfaces:
                unused_report.append(
                    f"{device.name}: {', '.join(unused_interfaces)}"
                )
            else:
                self.logger.success(
                    "All interfaces in device %s are in use.", device.name
                )

        if unused_report:
            return "Unused interfaces:\n" + "\n".join(unused_report)
        else:
            return "No unused interfaces found in matching devices."

register_jobs()