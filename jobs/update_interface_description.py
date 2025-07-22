from nautobot.apps.jobs import Job, ObjectVar, StringVar, register_jobs
from nautobot.dcim.models import Location, Device, Interface
from netmiko import ConnectHandler

class UpdateIntDescription(Job):
    """Job to update the description of a selected interface on a device."""

    # Location filter to narrow down available devices
    device_location = ObjectVar(
        model=Location,
        description="Select the location to filter the devices."
    )

    # Device filter to narrow down available interfaces
    device = ObjectVar(
        model=Device,
        description="Select a device from the chosen location.",
        query_params={
            "location": "$device_location",
        }
    )

    # Interface chosen from the selected device
    interface = ObjectVar(
        model=Interface,
        description="Select an interface from the chosen device.",
        query_params={
            "device": "$device",
        }
    )

    # The new description text to apply to the interface
    new_description = StringVar(
        description="Enter the new interface description."
    )

    class Meta:
        name = "Update Interface Description"
        description = "Allows updating the description of a specific interface on a selected device."
        has_sensitive_variables = False

    def run(self, device_location, device, interface, new_description):
        """Main job function to update the interface description using netmiko."""
        self.logger.info("Preparing to update interface description on device: %s", device.name)
        try:
            # Define the connection parameters for netmiko
            device_params = {
                "device_type": "cisco_ios",
                "host": str(device.primary_ip4.address),  # Assuming the primary IP is IPv4
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
                    "end"
                ]
                
                # Send command to update the interface description
                net_conn.send_config_set(interface_command)
                self.logger.info("Successfully updated the description of interface %s to '%s' on device %s.", interface.name, new_description, device.name)
        
        except Exception as e:
            self.logger.error("Failed to update the interface description for device %s: %s", device.name, str(e))
