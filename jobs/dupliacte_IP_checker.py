from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress
import csv

class CheckDuplicateIPAddresses(Job):
    """
    Job to check for duplicate IP addresses in Nautobot IPAM and output to a CSV file.
    """

    class Meta:
        name = "Check Duplicate IP Addresses"
        description = "Scans for duplicate IP addresses in IPAM and outputs results as a CSV."

    def run(self):
        self.logger.info("Starting scan for duplicate IP addresses.")

        # Find duplicates using a values() + annotate/count() aggregation
        ip_counts = (
            IPAddress.objects.values("address")
            .order_by("address")
            .annotate(count_ip=models.Count("id"))
            .filter(count_ip__gt=1)
        )
        duplicate_addrs = set([item['address'] for item in ip_counts])

        if not duplicate_addrs:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicate IP addresses found."

        self.logger.info("Found %s duplicate addresses. Gathering details...", len(duplicate_addrs))

        # Get the details of all duplicate IPs
        duplicate_ips = IPAddress.objects.filter(address__in=duplicate_addrs).order_by("address")

        # Create CSV file for output
        headers = [
            "Address",
            "Status",
            "Tenant",
            "Assigned Object",
            "Description",
            "VRF",
            "Role"
        ]

        file_handle = self.create_file("duplicate_ips.csv")
        writer = csv.writer(file_handle)
        writer.writerow(headers)

        for ip in duplicate_ips:
            writer.writerow([
                ip.address,
                ip.status.name if ip.status else "",
                ip.tenant.name if ip.tenant else "",
                str(ip.assigned_object) if ip.assigned_object else "",
                ip.description,
                ip.vrf.name if ip.vrf else "",
                ip.role.name if ip.role else "",
            ])

        file_handle.close()
        self.logger.info("CSV of duplicate IP addresses created.")

        # Return a message indicating file is available
        return "Duplicate IP addresses written to duplicate_ips.csv in the job results."

register_jobs()