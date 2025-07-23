from nautobot.apps.jobs import Job

class HelloWorldJob(Job):

	class Meta:
		name = "Hello World"	#Job Name
		description = "Prints a 'Hello World' log message"
		grouping = "Tutorial Jobs"

	def run(self):
		self.logger.info("Hello World!") #This is the logic of the job