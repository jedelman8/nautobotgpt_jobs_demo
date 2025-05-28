from nautobot.apps.jobs import Job, register_jobs, ObjectVar
from nautobot.dcim.models import Device, Location
import csv
import io

class DevicesPrimaryIPv4Report(Job):
    """
    Ensure that all devices at a selected Location have a primary IPv4 address.
    Generate a CSV report listing compliant and non-compliant devices.
    """

    location = ObjectVar(
        model=Location,
        required=True,
        description="Location to audit for primary IPv4 attribution.",
    )

    class Meta:
        name = "Devices Primary IPv4 Audit and Report"
        description = "Checks all devices in a Location for a primary IPv4, reports, and outputs CSV."

    def run(self, location):
        devices = Device.objects.filter(location=location)
        missing = []
        csv_rows = [("Device Name", "Primary IPv4 Address")]

        for device in devices:
            primary_ip4 = device.primary_ip4.address if device.primary_ip4 else ""
            if not primary_ip4:
                self.logger.warning("Device %s is missing a primary IPv4 address.", device.name)
                missing.append(device.name)
            else:
                self.logger.success("Device %s has primary IPv4: %s.", device.name, primary_ip4)
            csv_rows.append((device.name, primary_ip4))

        # Create CSV in-memory
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(csv_rows)
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        # Correct call: filename, then content
        self.create_file("primary_ipv4_audit.csv", csv_content)

        if not missing:
            self.logger.success("All devices in location %s have a primary IPv4.", location.name)
            result_msg = "All devices compliant."
        else:
            result_msg = f"Devices missing primary IPv4: {', '.join(missing)}"

        return f"{result_msg}\nCSV report generated: primary_ipv4_audit.csv"

register_jobs(DevicesPrimaryIPv4Report)