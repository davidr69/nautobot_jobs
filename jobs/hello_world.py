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
from django_redis import get_redis_connection

name = "Examples"


class HelloWorldJob(Job):
    class Meta:
        name = "Hello World"  # job name
        description = "It's what you would expect!"
        has_sensitive_variables = False
        soft_time_limit = 600
        time_limit = 900
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
        redis_client = get_redis_connection("default")
        self.logger.info(f"{self.natural_slug=}")
        countdown = redis_client.get(f"{self.natural_slug}.countdown")
        self.logger.info(f"countdown? {countdown}")

        if comment:
            self.logger.info("Comment: %s", comment)
        if devices:
            self.logger.info("Selected device type IDs: %s", devices)

    def on_failure(self, exc, task_id, args, kwargs):
        self.logger.error("Job failed!")
        self.logger.error(f"{exc=}, {task_id=}, {args=}, {kwargs=}")


class Noop(Job):
    class Meta:
        name = "Noop"
        description = "If you know, you know"
        has_sensitive_variables = False
        soft_time_limit = 600
        time_limit = 900
        read_only = True
        is_singleton = True

    def run(self):
        self.logger.info("I do absolutely nothing!")


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
        self.logger.debug("Hello, this is my first Nautobot Job that requires approval.")


register_jobs(HelloWorldJob, Noop, HelloWorldButtonReceiver, HelloJobsWithApproval)
