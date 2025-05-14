from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress

class CheckDuplicateIPAddresses(Job):
    class Meta:
        name = "Check Duplicate IP Addresses"
        description = "Identifies duplicate IP addresses in Nautobot IPAM."

    def run(self):
        ip_map = {}
        duplicates = []

        # Build mapping of addresses to IP objects
        for ip in IPAddress.objects.all():
            address_key = str(ip.address)
            ip_map.setdefault(address_key, []).append(ip)

        # Find duplicates
        for address, ip_objs in ip_map.items():
            if len(ip_objs) > 1:
                details = []
                for ip_obj in ip_objs:
                    # assigned_object is a GenericForeignKey (can be None)
                    assigned_obj = getattr(ip_obj, "assigned_object", None)
                    details.append(
                        f"{ip_obj} (status: {ip_obj.status}, assigned to: {assigned_obj or 'Unassigned'})"
                    )
                duplicates.append(
                    f"Duplicate IP: {address} ({len(ip_objs)} instances):\n" + "\n".join(details)
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