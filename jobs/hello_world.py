from nautobot.apps.jobs import Job, StringVar, register_jobs, JobButtonReceiver, MultiChoiceVar, ObjectVar, TextVar, IntegerVar
from nautobot.dcim.models.devices import DeviceType

name = 'Examples'       # grouping in UI

class HelloWorldJobs(Job):
	class Meta:
		name = 'Hello World'    # job name
		description = 'Update this description'

	who = StringVar(
		description = 'Identify yourself!',
		default = 'hola!'
	)

	age = IntegerVar(
		description = 'Your age',
		default = 30
	)

	comment = TextVar(
		description = 'Any comments?',
		default = 'No comments'
	)

	devices = MultiChoiceVar(
		description = 'Select device type(s)',
		choices = (self.GetDeviceTypes())
	)

	def run(self, *, who):
		self.logger.info('Hello, %s!', who)


	def GetDeviceTypes(self):
		devices = DeviceType.objects.all()
		return [(str(device.pk), str(device)) for device in devices]


class HelloWorldButtonReceiver(JobButtonReceiver):
	class Meta:
		name = 'Hello World Button Receiver'
		description = 'A Job Button Receiver example'

	def run(self, context):
		self.log_info("Hello from the Job Button Receiver!")
		self.log_info(f"Context: {context}")

register_jobs(HelloWorldJobs, HelloWorldButtonReceiver)
