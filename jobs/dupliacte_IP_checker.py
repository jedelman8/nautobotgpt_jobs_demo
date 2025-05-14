from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress
import csv
import io

class FindDuplicateIPAddresses(Job):
    class Meta:
        name = "Find Duplicate IP Addresses"
        description = "Identify and export duplicate IP addresses from IPAM to a CSV file."

    def run(self):
        ip_map = {}
        for ip in IPAddress.objects.all():
            ip_map.setdefault(str(ip.address), []).append(ip)

        duplicates = {k: v for k, v in ip_map.items() if len(v) > 1}

        if not duplicates:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicates found."

        output = io.StringIO()
        csv_headers = ["IP Address", "Assigned Object Type", "Assigned Object Name", "Assigned Object ID"]
        writer = csv.writer(output)
        writer.writerow(csv_headers)

        for ip_addr, ip_objs in duplicates.items():
            for ip in ip_objs:
                # Check assignment type
                assigned_obj = None
                obj_type = "Unassigned"
                obj_name = ""
                obj_id = ""
                if hasattr(ip, "interface") and ip.interface:
                    assigned_obj = ip.interface
                elif hasattr(ip, "vm_interface") and ip.vm_interface:
                    assigned_obj = ip.vm_interface

                if assigned_obj:
                    obj_type = assigned_obj._meta.verbose_name.title()
                    obj_name = str(assigned_obj)
                    obj_id = str(assigned_obj.pk)

                writer.writerow([ip_addr, obj_type, obj_name, obj_id])

        csv_content = output.getvalue()
        output.close()

        self.create_file("duplicate_ip_addresses.csv", csv_content)

        self.logger.info("Duplicate IP addresses written to duplicate_ip_addresses.csv")
        return "Duplicate IP addresses written to duplicate_ip_addresses.csv"