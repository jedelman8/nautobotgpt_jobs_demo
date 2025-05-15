from nautobot.apps.jobs import Job, register_jobs
import csv
import io
from django.utils import timezone

from nautobot.ipam.models import IPAddress

class CheckDuplicateIPAddresses(Job):
    """
    Job to check for duplicate IP addresses in Nautobot IPAM, exporting results to a CSV file.
    """

    class Meta:
        name = "Check Duplicate IP Addresses"
        description = "Check for duplicate IP addresses and output details to a CSV file."

    def run(self):
        # Gather all IPAddresses, grouped by 'address'
        ip_map = {}
        for ip in IPAddress.objects.all().select_related("status", "tenant"):
            addr_str = str(ip.address)
            ip_map.setdefault(addr_str, []).append(ip)

        duplicates = {addr: ips for addr, ips in ip_map.items() if len(ips) > 1}
        row_count = 0

        if not duplicates:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicates found."

        # Use StringIO for in-memory CSV writing
        output = io.StringIO()
        fieldnames = [
            "IP Address",
            "Status",
            "Assigned Object Type",
            "Assigned Object Name",
            "Tenant",
            "Description",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for addr, ips in duplicates.items():
            for ip in ips:
                assigned_type = (
                    ip.assigned_object_type.model if hasattr(ip, "assigned_object_type") and ip.assigned_object_type else ""
                )
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

        # Write CSV data as bytes
        csv_content = output.getvalue().encode("utf-8")
        output.close()

        now = timezone.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"duplicate_ip_addresses_{now}.csv"
        self.create_file(csv_filename, csv_content)

        self.logger.info("Found %s duplicate IP addresses. Results written to %s", len(duplicates), csv_filename)
        return f"Found {len(duplicates)} duplicate IP addresses. Total rows exported: {row_count}. Download: {csv_filename}"
