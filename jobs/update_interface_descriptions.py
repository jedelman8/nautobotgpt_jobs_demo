from nautobot.apps.jobs import Job, register_jobs, ObjectVar, MultiObjectVar, StringVar
from nautobot.dcim.models import Device, Interface, Location

class InterfaceDescriptionUpdater(Job):
    """Job to update interface descriptions with filtering options."""

    location = ObjectVar(
        model=Location,
        required=True,
        description="Select a location to filter devices."
    )

    device = ObjectVar(
        model=Device,
        required=True,
        query_params={"location_id": "$location"},
        description="Select a device within the selected location."
    )

    interfaces = MultiObjectVar(
        model=Interface,
        required=True,
        query_params={"device_id": "$device"},
        description="Select one or more interfaces to update."
    )

    description = StringVar(
        required=True,
        description="Description to set on the selected interface(s)."
    )

    class Meta:
        name = "Update Interface Descriptions"
        description = "Update descriptions for selected interfaces with filtering."

    def run(self, location, device, interfaces, description, **kwargs):
        updated = 0

        for interface in interfaces:
            if interface.description != description:
                interface.description = description
                interface.save()
                updated += 1
                self.logger.info("Updated description for interface %s", interface)
            else:
                self.logger.info("Interface %s already has the desired description.", interface)

        result = f"Updated {updated} interface(s) with the new description."
        self.logger.info(result)
        return result

register_jobs(InterfaceDescriptionUpdater)