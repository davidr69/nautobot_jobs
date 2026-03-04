from nautobot.apps.jobs import register_jobs, JobButtonReceiver


name = "Job Button Receivers"


class HelloWorldJobButton(JobButtonReceiver):

    class Meta:
        name = "This is my first JobButton Receiver"

    def receive_job_button(self, obj):
        self.logger.info("This is my first Nautobot Job Button.", extra={"object": obj})


register_jobs(HelloWorldJobButton)
