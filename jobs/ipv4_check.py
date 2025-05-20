from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models import Device, Location

class DevicesRequirePrimaryIPv4(Job):
    """Ensure all Devices at a Location have a primary IPv4 Address."""

    location = ObjectVar(
        model=Location,
        required=True,
        description="Select the location to check devices."
    )

    class Meta:
        name = "Devices Require Primary IPv4"
        description = "Ensures all devices at the selected location have a primary IPv4 address populated."
        approval_required = False

    def run(self, location, **kwargs):
        missing = []
        devices = Device.objects.filter(location=location)
        for device in devices:
            if not device.primary_ip4:
                missing.append(device.name)
                self.logger.warning(
                    "Device '%s' does not have a primary IPv4 address set.", device.name
                )
        if missing:
            result = f"Devices missing a primary IPv4 address: {', '.join(missing)}"
        else:
            result = "All devices at this location have a primary IPv4 address."
        return result

register_jobs(DevicesRequirePrimaryIPv4)