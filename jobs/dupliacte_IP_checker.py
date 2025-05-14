from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress
import csv
import io

class FindDuplicateIPAddresses(Job):
    class Meta:
        name = "Find Duplicate IP Addresses"
        description = "Identify and export duplicate IP addresses from IPAM to a CSV file."

    def run(self):
        # Gather all IP addresses, group by address
        ip_map = {}
        for ip in IPAddress.objects.all():
            ip_map.setdefault(str(ip.address), []).append(ip)

        # Identify duplicates
        duplicates = {k: v for k, v in ip_map.items() if len(v) > 1}

        if not duplicates:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicates found."

        # Prepare CSV data in memory
        output = io.StringIO()
        csv_headers = ["IP Address", "Assigned Object Type", "Assigned Object Name", "Assigned Object ID"]
        writer = csv.writer(output)
        writer.writerow(csv_headers)

        for ip_addr, ip_objs in duplicates.items():
            for ip in ip_objs:
                assigned_obj = ip.assigned_object
                if assigned_obj:
                    obj_type = assigned_obj._meta.verbose_name.title()
                    obj_name = str(assigned_obj)
                    obj_id = str(assigned_obj.pk)
                else:
                    obj_type = "Unassigned"
                    obj_name = ""
                    obj_id = ""

                writer.writerow([ip_addr, obj_type, obj_name, obj_id])

        # Get CSV data as string
        csv_content = output.getvalue()
        output.close()

        # Save file using Job.create_file
        self.create_file("duplicate_ip_addresses.csv", csv_content)

        self.logger.info("Duplicate IP addresses written to duplicate_ip_addresses.csv")
        return "Duplicate IP addresses written to duplicate_ip_addresses.csv"

register_jobs(FindDuplicateIPAddresses)