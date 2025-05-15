from nautobot.apps.jobs import Job, ObjectVar, StringVar, register_jobs
from nautobot.dcim.models import Location, Device, Interface

class InterfaceDescriptionSearch(Job):
    """A job to search for interfaces by description containing a specific string."""

    location = ObjectVar(
        model=Location,
        description="Select a location to search devices within."
    )
    search_string = StringVar(
        description="Enter the text to search within interface descriptions."
    )

    class Meta:
        name = "Interface Description Search"
        description = "Find interfaces with descriptions containing the specified string."

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
                        "Found match: Device: %s, Interface: %s, Description: %s",
                        device.name, interface.name, interface.description
                    )