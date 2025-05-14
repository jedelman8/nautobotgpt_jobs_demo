from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress
import csv

class FindDuplicateIPAddresses(Job):
    class Meta:
        name = "Find Duplicate IP Addresses"
        description = "Identify and export duplicate IP addresses from IPAM to a CSV file."

    def run(self):
        # Gather all IP addresses, group by address
        ip_map = {}
        for ip in IPAddress.objects.all().select_related("assigned_object_type", "assigned_object_id"):
            ip_map.setdefault(str(ip.address), []).append(ip)

        # Identify duplicates
        duplicates = {k: v for k, v in ip_map.items() if len(v) > 1}

        if not duplicates:
            self.logger.info("No duplicate IP addresses found.")
            return "No duplicates found."

        # Prepare CSV file
        csv_headers = ["IP Address", "Assigned Object Type", "Assigned Object Name", "Assigned Object ID"]
        file_obj = self.create_file("duplicate_ip_addresses.csv")

        with open(file_obj.name, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
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

        self.logger.info("Duplicate IP addresses written to %s", file_obj.name)
        return f"Duplicate IP addresses written to {file_obj.name}"

register_jobs(FindDuplicateIPAddresses)