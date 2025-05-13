from nautobot.apps.jobs import register_jobs
from .hello_world import HelloWorldJob


register_jobs(
	HelloWorldJob,
	)