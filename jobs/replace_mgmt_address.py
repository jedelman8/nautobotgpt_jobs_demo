from nautobot.apps.jobs import Job, ObjectVar, StringVar
from nautobot.dcim.models import Device, Location

class SubstituteIPWithMgmt(Job):
    """
    Substitute an input IP address with each device's management (primary IPv4) address
    in the device's 'config_snippet' custom field (string type).
    """

    location = ObjectVar(
        model=Location,
        required=True,
        description="Target devices at this Location."
    )
    input_ip = StringVar(
        required=True,
        description="IPv4 address to replace within the config_snippet custom field."
    )

    class Meta:
        name = "Substitute Input IP with Management IPv4"
        description = (
            "Replaces the provided IP with each device's primary IPv4 address "
            "in the config_snippet custom field."
        )

    def run(self, location, input_ip):
        from nautobot.extras.models import CustomField
        field_name = 'config_snippet'  # adjust if your custom field uses another name
        updated = []
        devices = Device.objects.filter(location=location)
        for device in devices:
            mgmt_ip = device.primary_ip4
            if not mgmt_ip:
                self.logger.warning(
                    "Device %s has no management IPv4 (primary_ip4); skipping.", device.name
                )
                continue
            # Get the string from the custom field
            config_text = device.custom_field_data.get(field_name, "")
            if input_ip in config_text:
                new_text = config_text.replace(input_ip, str(mgmt_ip.address.ip))
                device.custom_field_data[field_name] = new_text
                device.save()
                self.logger.success(
                    "Device %s: substituted %s with %s in custom field '%s'.",
                    device.name, input_ip, mgmt_ip.address.ip, field_name
                )
                updated.append(device.name)
            else:
                self.logger.info(
                    "Device %s: input IP not found in custom field.", device.name
                )

        if not updated:
            return "No devices required substitution."
        return f"IP substituted for {len(updated)} device(s): {', '.join(updated)}"

from nautobot.apps.jobs import register_jobs
register_jobs(SubstituteIPWithMgmt)