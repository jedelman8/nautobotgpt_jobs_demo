from nautobot.apps.jobs import Job

name = "Tutorial Jobs" 

class HelloWorldJob(Job):

	class Meta:
		name = "Hello World"	#Job Name
		description = "Prints a 'Hello World' log message"

	def run(self):
		self.logger.info("Hello World!") #This is the logic of the job