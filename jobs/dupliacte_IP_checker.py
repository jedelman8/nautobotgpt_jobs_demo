from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress

class CheckDuplicateIPAddresses(Job):
    class Meta:
        name = "Check Duplicate IP Addresses"
        description = "Identifies duplicate IP addresses in Nautobot IPAM."

    def run(self):
        # Build a dict mapping IP addresses to their associated objects
        ip_map = {}
        duplicates = []

        # Iterate over all IP addresses
        for ip in IPAddress.objects.all():
            key = str(ip.address)
            if key not in ip_map:
                ip_map[key] = []
            ip_map[key].append(ip)

        # Find all addresses with >1 instance
        for address, ip_objs in ip_map.items():
            if len(ip_objs) > 1:
                details = []
                for ip_obj in ip_objs:
                    assigned_obj = ip_obj.assigned_object  # Can be interface, VM interface, etc.
                    details.append(
                        f"{ip_obj} (status: {ip_obj.status}, assigned to: {assigned_obj or 'Unassigned'})"
                    )
                duplicates.append(
                    f"Duplicate IP: {address} - {len(ip_objs)} instances:\n" + "\n".join(details)
                )

        if duplicates:
            self.logger.info("Found %s duplicate IP addresses.", len(duplicates))
            for dup in duplicates:
                self.logger.info("%s", dup)
            return "\n\n".join(duplicates)
        else:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicate IP addresses found."

register_jobs(CheckDuplicateIPAddresses)