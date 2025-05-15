from nautobot.apps.jobs import Job, register_jobs
from django.utils import timezone
import csv

from nautobot.ipam.models import IPAddress

class CheckDuplicateIPAddresses(Job):
    """
    Job to check for duplicate IP addresses in Nautobot IPAM, exporting results to a CSV file.
    """

    class Meta:
        name = "Check Duplicate IP Addresses"
        description = "Check for duplicate IP addresses and output details to a CSV file."

    def run(self):
        # Gather all IPAddresses, grouped by 'address' field
        ip_map = {}
        for ip in IPAddress.objects.all().select_related("status", "tenant", "assigned_object"):
            ip_map.setdefault(str(ip.address), []).append(ip)

        duplicates = {addr: ips for addr, ips in ip_map.items() if len(ips) > 1}
        row_count = 0

        if not duplicates:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicates found."

        # CSV file setup
        now = timezone.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"duplicate_ip_addresses_{now}.csv"
        csv_file = self.create_file(csv_filename, mode="w", newline="")

        fieldnames = [
            "IP Address",
            "Status",
            "Assigned Object Type",
            "Assigned Object Name",
            "Tenant",
            "Description",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Write the details for each duplicate
        for addr, ips in duplicates.items():
            for ip in ips:
                assigned_type = getattr(ip.assigned_object_type, "model", "") if ip.assigned_object_type else ""
                assigned_name = str(ip.assigned_object) if ip.assigned_object else ""
                writer.writerow({
                    "IP Address": str(ip.address),
                    "Status": str(ip.status),
                    "Assigned Object Type": assigned_type,
                    "Assigned Object Name": assigned_name,
                    "Tenant": str(ip.tenant) if ip.tenant else "",
                    "Description": ip.description or "",
                })
                row_count += 1

        csv_file.close()
        self.logger.info("Found %s duplicate IP addresses. Results written to %s", len(duplicates), csv_filename)
        return f"Found {len(duplicates)} duplicate IP addresses. Total rows exported: {row_count}. Download: {csv_filename}"
