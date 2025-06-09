from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models import Device, Location

class DevicesRequirePrimaryIPv4(Job):
    """
    Ensure every Device in a given Location has its primary_ip4 field set.
    Warn if any do not.
    """

    location = ObjectVar(
        model=Location,
        required=True,
        description="Location to audit (acts like site)."
    )

    class Meta:
        name = "Devices Require IPv4 Management Address"
        description = "Check devices in a Location for a primary IPv4 address."
        approval_required = False

    def run(self, location):
        missing = []
        devices = Device.objects.filter(location=location)

        for device in devices:
            if not device.primary_ip4:
                missing.append(device.name)
                self.logger.warning(
                    "Device %s missing primary IPv4 management address.", device.name
                )
        if not missing:
            self.logger.success("All devices have a primary IPv4 management address.")
            return "All devices compliant."
        return f"Devices missing primary IPv4: {', '.join(missing)}"

register_jobs(DevicesRequirePrimaryIPv4)