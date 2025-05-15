from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress
import csv
import io

class DuplicateIPCheckJob(Job):
    class Meta:
        name = "Duplicate IP Address Checker"
        description = "Check for and list all duplicate IP addresses in IPAM, outputting results to a CSV file."

    def run(self):
        # Collect all addresses
        ip_addresses = IPAddress.objects.all().values_list("address", flat=True)

        from collections import Counter
        ip_count = Counter(ip_addresses)
        duplicates = [ip for ip, count in ip_count.items() if count > 1]

        output_rows = []
        # Gather details about each instance of the duplicate
        for dup_ip in duplicates:
            ip_objs = IPAddress.objects.filter(address=dup_ip)
            for ip_obj in ip_objs:
                output_rows.append([
                    ip_obj.address,
                    ip_obj.status,
                    str(ip_obj.assigned_object) if ip_obj.assigned_object else "",
                    ip_obj.description or "",
                ])

        # Create the CSV file
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["IP Address", "Status", "Assigned Object", "Description"])
        for row in output_rows:
            writer.writerow(row)

        csv_bytes = io.BytesIO(output.getvalue().encode("utf-8"))
        self.create_file("duplicate-ips.csv", csv_bytes)

        self.logger.info("Detected %s duplicate IPs.", len(duplicates))
        return f"Duplicate IP Address check completed. {len(duplicates)} unique duplicate IP addresses found. Results written to duplicate-ips.csv."