from nautobot.apps.jobs import Job, ObjectVar
from nautobot.dcim.models import Location, Device
import requests

class DeviceUptimeCheckJob(Job):
    class Meta:
        name = "Device Uptime Check"
        description = "Check the uptime of devices in a specific location."

    location = ObjectVar(
        model=Location,
        description="Select the location to filter devices."
    )

    def run(self, location):
        # Query devices in the specified location
        devices = Device.objects.filter(location=location)

        if not devices.exists():
            self.logger.warning("No devices found in the specified location.")
            return

        # Iterate over each device and check uptime
        for device in devices:
            self.logger.info("Checking device %s...", device.name)
            # Here you can implement the actual uptime check logic
            # For example, ping the device or request its uptime via SNMP/SSH
            uptime = self.check_device_uptime(device)
            self.logger.info("Device %s has an uptime of %s.", device.name, uptime)

    def check_device_uptime(self, device):
        # Placeholder for actual uptime check logic
        # You'll likely need to interface with the device using SNMP, SSH, or an API
        # Here, we use a mockup uptime check to demonstrate
        try:
            response = requests.get(f"http://{device.primary_ip4.address}/api/uptime")
            response.raise_for_status()
            return response.json().get("uptime", "Unknown")
        except requests.RequestException as e:
            self.logger.error("Failed to check uptime for %s: %s", device.name, str(e))
            return "Unknown"

# Register the job
from nautobot.apps.jobs import register_jobs
register_jobs(DeviceUptimeCheckJob)