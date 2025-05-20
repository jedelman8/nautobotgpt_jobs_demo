from nautobot.apps.jobs import Job, StringVar, MultiObjectVar, register_jobs
from nautobot.dcim.models import Interface

class UpdateInterfaceDescriptionsJob(Job):
    description = StringVar(
        description="Enter the interface description to apply to the selected interface(s)."
    )
    interfaces = MultiObjectVar(
        model=Interface,
        required=True,
        description="Select one or more interfaces to update."
    )

    class Meta:
        name = "Update Interface Descriptions"
        description = "Update description of one or more interfaces."
        approval_required = False

    def run(self, description, interfaces, **kwargs):
        updated_interfaces = []
        for interface in interfaces:
            old_description = interface.description or ''
            interface.description = description
            interface.save()
            updated_interfaces.append(interface.display)
            self.logger.info(
                "Interface '%s' updated: description changed from '%s' to '%s'.",
                interface.display, old_description, description
            )
        return f"Updated descriptions for {len(updated_interfaces)} interface(s): " + ", ".join(updated_interfaces)