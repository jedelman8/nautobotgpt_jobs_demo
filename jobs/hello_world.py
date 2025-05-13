from nautobot.apps.jobs import Job

name = "Examples"

class HelloWorldJob(Job):
	class Meta:
		name = "Hello World"	#Job Name

    def run(self):
        self.logger.info("Hello World!") #This is the logic of the job
        
jobs.register_jobs(HelloWorldJob)