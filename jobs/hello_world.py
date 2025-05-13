from nautobot.apps.jobs import Job

class HelloWorldJob(Job):
    def run(self):
        self.logger.info("Hello World!")

