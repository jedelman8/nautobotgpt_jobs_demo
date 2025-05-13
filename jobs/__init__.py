from nautobot.apps.jobs import register_jobs
from .HelloWorldJob import HelloWorldJob


register_jobs(HelloWorldJob)