from nautobot.apps.jobs import Job, register_jobs, JobButtonReceiver


name = "Job Button Receivers"


class HelloWorldJobButton(JobButtonReceiver):

    class Meta:
        name = "This is my first JobButton Receiver"

    def receive_job_button(self, obj):
        self.logger.info("This is my first Nautobot Job Button.", extra={"object": obj})
        self.logger.info(
            "This is my first Nautobot Job Button.", extra={"object": obj.name}
        )
        self.logger.info(
            "This is my first Nautobot Job Button.", extra={"object": obj.status}
        )
        self.logger.info(
            "This is my first Nautobot Job Button.", extra={"object": obj.role}
        )


register_jobs(HelloWorldJobButton)
