from nautobot.apps.jobs import (
    Job,
    StringVar,
    register_jobs,
    JobButtonReceiver,
#    MultiChoiceVar,
    ObjectVar,
    TextVar,
    IntegerVar,
)
from nautobot.dcim.models.devices import DeviceType

name = "Examples"  # grouping in UI


class HelloWorldJobs(Job):
    class Meta:
        name = "Hello World"  # job name
        description = "Choose a better description"
        has_sensitive_variables = False
        soft_time_limit = 120
        time_limit = 300
        read_only = True
        is_singleton = True

    who = StringVar(description="Identify yourself!", default="hola!")

    age = IntegerVar(description="Your age", default=30)

    comment = TextVar(description="Any comments?", default="No comments")

    # devices = MultiChoiceVar(
    # 	description = 'Select device type(s)',
    # 	choices = (get_device_types())
    # )
    devices = ObjectVar(model=DeviceType, description="Select device type(s)")

    def run(self, *, who, age, comment, devices):
        self.logger.info("Hello, %s! You are %s years old.", who, age)
        if comment:
            self.logger.info("Comment: %s", comment)
        if devices:
            self.logger.info("Selected device type IDs: %s", devices)


class HelloWorldButtonReceiver(JobButtonReceiver):
    class Meta:
        name = "Hello World Button Receiver"
        description = "A Job Button Receiver example"

    def run(self, context):
        self.log_info("Hello from the Job Button Receiver!")
        self.log_info(f"Context: {context}")


class HelloJobsWithApproval(Job):

    class Meta:
        name = "Hello World with Approval Required"
        approval_required = True
        has_sensitive_variables = False

    def run(self):
        self.logger.debug(
            "Hello, this is my first Nautobot Job that requires approval."
        )


register_jobs(HelloWorldJobs, HelloWorldButtonReceiver, HelloJobsWithApproval)
