from nautobot.apps.jobs import Job, register_jobs, ObjectVar, IntegerVar, StringVar
from nautobot.dcim.models import Location, Device, Interface
from nautobot.extras.models import Role

from netmiko import ConnectHandler

name = "NautobotGPT Demos"


class UpdateIntDescription(Job):
    """Job to update the description of a selected interface on a device."""

    #####################
    #      FILTERS      #
    #####################

    # Location filter to narrow down available devices
    device_location = ObjectVar(
        model=Location, description="Select the location to filter the devices."
    )

    # Device filter to narrow down available interfaces
    device = ObjectVar(
        model=Device,
        description="Select a device from the chosen location.",
        query_params={
            "location": "$device_location",
        },
    )

    # Interface chosen from the selected device
    interface = ObjectVar(
        model=Interface,
        description="Select an interface from the chosen device.",
        query_params={
            "device": "$device",
        },
    )

    #####################
    #   END OF FILTERS  #
    #####################

    # The new description text to apply to the interface
    new_description = StringVar(description="Enter the new interface description.")

    class Meta:
        name = "Update Interface Description"
        description = "Allows updating the description of a specific interface on a selected device."
        has_sensitive_variables = False

    def run(self, device_location, device, interface, new_description):
        """Main job function to update the interface description using netmiko."""
        self.logger.info(
            "Preparing to update interface description on device: %s", device.name
        )
        try:
            # Define the connection parameters for netmiko
            device_params = {
                "device_type": "cisco_ios",
                "host": str(
                    device.primary_ip4.address.ip
                ),  # Assuming the primary IP is IPv4
                "username": "webinar_user",  # Replace with your device's username
                "password": "webinar_pass",  # Replace with your device's password
            }

            # Establish the connection
            with ConnectHandler(**device_params) as net_conn:
                net_conn.enable()  # Enter enable mode

                # Construct the command
                interface_command = [
                    f"interface {interface.name}",
                    f"description {new_description}",
                    "end",
                ]

                # Send command to update the interface description
                net_conn.send_config_set(interface_command)
                self.logger.info(
                    "Successfully updated the description of interface %s to '%s' on device %s.",
                    interface.name,
                    new_description,
                    device.name,
                )

        except Exception as e:
            self.logger.error(
                "Failed to update the interface description for device %s: %s",
                device.name,
                str(e),
            )


class UnusedInterfacesReport(Job):

    location = ObjectVar(
        model=Location, description="Location to search for devices.", required=True
    )
    role = ObjectVar(
        model=Role, description="Device Role to filter devices.", required=True
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
                "No devices found for role %s in location %s.", role.name, location.name
            )
            return "No devices matched."

        for device in devices:
            unused_interfaces = []
            interfaces = Interface.objects.filter(device=device)

            for iface in interfaces:
                if (
                    iface.lag is None
                    and iface.cable is None
                    and not iface.connected_endpoint
                    and not iface.ip_addresses.exists()
                ):
                    unused_interfaces.append(iface.name)
                    self.logger.info(
                        "Device %s unused interface: %s", device.name, iface.name
                    )

            if unused_interfaces:
                unused_report.append(f"{device.name}: {', '.join(unused_interfaces)}")
            else:
                self.logger.success(
                    "All interfaces in device %s are in use.", device.name
                )

        if unused_report:
            return "Unused interfaces:\n" + "\n".join(unused_report)
        else:
            return "No unused interfaces found in matching devices."


class UpdateDeviceSerial(Job):
    """Job to update the serial number of a selected device."""

    device_location = ObjectVar(
        model=Location, description="Select the location to filter the devices."
    )

    device = ObjectVar(
        model=Device,
        description="Select a device from the chosen location.",
        query_params={
            "location": "$device_location",
        },
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
            self.logger.info(
                "Successfully updated the serial number of device %s to %s.",
                device.name,
                new_serial,
            )
        except Exception as e:
            self.logger.error(
                "Failed to update the serial number for device %s: %s",
                device.name,
                str(e),
            )


class DevicesRequirePrimaryIPv4(Job):
    """
    Ensure every Device in a given Location has its primary_ip4 field set.
    Warn if any do not.
    """

    location = ObjectVar(
        model=Location, required=True, description="Location to audit (acts like site)."
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
                    f"Device {device.name} missing primary IPv4 management address.",
                    extra={"object": device},
                )
        if not missing:
            self.logger.success("All devices have a primary IPv4 management address.")
            return "All devices compliant."
        return f"Devices missing primary IPv4: {', '.join(missing)}"


class InterfaceDescriptionSearch(Job):
    """A job to search for interfaces by description containing a specific string."""

    location = ObjectVar(
        model=Location, description="Select a location to search devices within."
    )
    search_string = StringVar(
        description="Enter the text to search within interface descriptions."
    )

    class Meta:
        name = "Interface Description Search"
        description = (
            "Find interfaces with descriptions containing the specified string."
        )

    def run(self, location, search_string):
        # Query the devices within the given location
        devices = Device.objects.filter(location=location)

        if not devices:
            self.logger.warning("No devices found in the specified location.")
            return

        for device in devices:
            # Get interfaces for each device
            interfaces = Interface.objects.filter(device=device)

            for interface in interfaces:
                # Check if the description contains the search string
                if search_string in interface.description:
                    # Log the found interface
                    self.logger.info(
                        f"Found match: Device: {device.name}, Interface: {interface.name}, Description: {interface.description}",
                        extra={"object": interface},
                    )


class HelloWorldJob(Job):

    class Meta:
        name = "Hello World"  # Job Name
        description = "Prints a 'Hello World' log message"

    def run(self):
        self.logger.info("Hello World!")  # This is the logic of the job


class DeviceUptimeCheck(Job):

    class Meta:
        name = "Device Uptime Check"
        description = "Check the uptime for network devices and flag devices with uptime below a threshold."

    location = ObjectVar(
        model=Location,
        required=False,
        description="Select a location to filter devices by.",
    )
    uptime_threshold = IntegerVar(
        description="Specify the uptime threshold in days.", default=7
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
                    "Device %s has low uptime of %d days.", device.name, uptime_days
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


register_jobs(
    DeviceUptimeCheck,
    HelloWorldJob,
    InterfaceDescriptionSearch,
    UpdateIntDescription,
    UnusedInterfacesReport,
    UpdateDeviceSerial,
    DevicesRequirePrimaryIPv4,
)
