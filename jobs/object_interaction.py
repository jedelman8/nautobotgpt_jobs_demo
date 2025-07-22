from nautobot.apps.jobs import Job, ObjectVar, StringVar, register_jobs
from nautobot.dcim.models import Location, Device

class UpdateDeviceSerial(Job):
    """Job to update the serial number of a selected device."""

    device_location = ObjectVar(
        model=Location,
        description="Select the location to filter the devices."
    )

    device = ObjectVar(
        model=Device,
        description="Select a device from the chosen location.",
        query_params={
            "location": "$device_location",
        }
    )

    new_serial = StringVar(
        description="Enter the new serial number for the selected device."
    )

    class Meta:
        name = "Update Device Serial Number"
        description = "Allows updating the serial number of a specific device within a selected location."
        has_sensitive_variables = False

    def run(self, device_location, device, new_serial):
        """The main entry point for the job."""
        self.logger.info("Updating serial number for device: %s", device.name)
        try:
            device.serial = new_serial
            device.save()
            self.logger.info("Successfully updated the serial number of device %s to %s.", device.name, new_serial)
        except Exception as e:
            self.logger.error("Failed to update the serial number for device %s: %s", device.name, str(e))

# Ensure the job is registered
register_jobs(UpdateDeviceSerial)