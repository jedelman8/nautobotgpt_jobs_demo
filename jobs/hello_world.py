from nautobot.apps.jobs import Job, register_jobs

class HelloWorldJob(Job):
    def run(self):
        self.logger.info("Hello World!")

register_jobs(HelloWorldJob)