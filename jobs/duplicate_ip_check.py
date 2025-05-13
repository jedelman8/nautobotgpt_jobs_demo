from nautobot.apps.jobs import Job
from nautobot.ipam.models import IPAddress

class DuplicateIPCheckJob(Job):
    """Job to identify duplicate IP addresses in IPAM."""

    class Meta:
        name = "Duplicate IP Check"
        description = "Identifies duplicate IP addresses in the IPAM system."
        has_sensitive_variables = False

    def run(self):
        """
        Retrieves all IP addresses from IPAM and identifies duplicates.
        """
        # Using a set to track seen IP addresses
        seen_ips = set()
        duplicates = []

        self.logger.info("Fetching all IP addresses from IPAM...")

        for ip in IPAddress.objects.all():
            if ip.address in seen_ips:
                self.logger.warning("Duplicate IP found: %s", ip.address)
                duplicates.append(ip.address)
            else:
                seen_ips.add(ip.address)

        if duplicates:
            return "Duplicate IP addresses found: " + ", ".join(duplicates)
        else:
            return "No duplicate IP addresses found."

