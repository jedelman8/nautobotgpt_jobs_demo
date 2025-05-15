from nautobot.apps.jobs import Job, ObjectVar, StringVar, register_jobs
from nautobot.dcim.models import Location, Device, Interface

class InterfaceDescriptionSearch(Job):
    """Search device interfaces in a Location for matching description."""

    location = ObjectVar(model=Location, description="Location to search devices in")
    search_text = StringVar(description="Text string to search for in interface descriptions")

    class Meta:
        name = "Interface Description Search"
        description = "Searches interface descriptions for a given text string in a Location"

    def run(self, location, search_text):
        results = []

        devices = Device.objects.filter(location=location)
        self.logger.info(
            "Searching %s devices in location '%s' for description containing '%s'",
            devices.count(), location.name, search_text
        )

        for device in devices:
            interfaces = Interface.objects.filter(device=device)
            for iface in interfaces:
                if iface.description and search_text.lower() in iface.description.lower():
                    self.logger.info(
                        "Match found: Device '%s' Interface '%s': %s",
                        device.name, iface.name, iface.description
                    )
                    results.append({
                        "device": device.name,
                        "interface": iface.name,
                        "description": iface.description,
                    })

        if results:
            return f"Found {len(results)} matching interface descriptions."
        else:
            return "No matching interface descriptions found."