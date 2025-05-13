from nautobot.apps.jobs import Job, register_jobs, ObjectVar, IntegerVar
from nautobot.dcim.models import Device, Location

class DeviceUptimeCheck(Job):

    class Meta:
        name = "Device Uptime Check"
        description = "Check the uptime for network devices and flag devices with uptime below a threshold."

    location = ObjectVar(
        model=Location,
        required=False,
        description="Select a location to filter devices by."
    )
    uptime_threshold = IntegerVar(
        description="Specify the uptime threshold in days.",
        default=7
    )

    def run(self, location, uptime_threshold):
        # Filter devices based on the selected location
        devices = Device.objects.all()
        if location:
            devices = devices.filter(location=location)

        if not devices:
            self.log_info(message="No devices found for the specified location.")
            return "No devices to check."

        # Check and log the uptime of each device
        for device in devices:
            uptime_days = self.get_device_uptime_days(device)
            
            if uptime_days < uptime_threshold:
                self.logger.warning(
                    "Device %s has low uptime of %d days.",
                    device.name, uptime_days
                )
            else:
                self.logger.success(
                    message=f"Device {device.name} has sufficient uptime of {uptime_days} days."
                )

    def get_device_uptime_days(self, device):
        """
        Mock function to simulate getting device uptime.
        In a real-world scenario, this would involve connecting to the device and retrieving its uptime.
        Returning a random value for demonstration purposes.
        """
        # Placeholder: Replace with actual logic to retrieve a device's uptime
        return 10  # Assume 10 days uptime for demonstration

register_jobs(DeviceUptimeCheck)