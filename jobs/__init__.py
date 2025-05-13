from nautobot.apps.jobs import register_jobs
from .hello_world import HelloWorldJob
from .duplicate_ip_check import CheckDuplicateIPAddresses


register_jobs(
	HelloWorldJob,
	#CheckDuplicateIPAddresses
	)