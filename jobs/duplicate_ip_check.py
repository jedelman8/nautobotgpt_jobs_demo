from nautobot.apps.jobs import Job, register_jobs
from nautobot.ipam.models import IPAddress

class CheckDuplicateIPAddresses(Job):

    class Meta:
        name = "Check Duplicate IP Addresses"
        description = "This job checks for duplicate IP addresses in the IPAM."

    def run(self):
        # Dictionary to hold the count of each IP
        ip_count = {}

        # Iterate over all IP addresses
        for ip_address in IPAddress.objects.all():
            ip = ip_address.address
            # Check if IP address already seen
            if ip in ip_count:
                ip_count[ip] += 1
            else:
                ip_count[ip] = 1

        # Check for duplicates and log them
        for ip, count in ip_count.items():
            if count > 1:
                self.logger.warning("Duplicate IP found: %s (Count: %d)", ip, count)

        self.logger.info(message="Check for duplicate IP addresses completed.")