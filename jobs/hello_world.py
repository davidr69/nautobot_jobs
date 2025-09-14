from nautobot.apps import jobs

name = 'Examples'       # grouping in UI

class HelloWorldJobs(jobs.Job):
	class Meta:
		name = 'Hello World'    # job name

	who = jobs.StringVar(
		description = 'Identify yourself!',
		default = 'hola!'
	)

	def run(self, *, who):
		self.logger.info('Hello, %s!', who)

jobs.register_jobs(HelloWorldJobs)
