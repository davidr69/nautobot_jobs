from nautobot.apps.jobs import register_jobs, StringVar, ObjectVar
from nautobot.dcim.models import Location
from nautobot_design_builder.design_job import DesignJob
from .context import MyDesignContext

class MyDeviceDesign(DesignJob):
    # Form fields in Nautobot UI
    site_name = StringVar(default="home")
    mgmt_prefix = StringVar(default="192.168.1.0/24")

    class Meta:
        name = "Deploy Home Devices"
        design_file = "templates/design.yml.j2"
        context_class = MyDesignContext

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.logger.info(f"Management prefix: {self.mgmt_prefix}")

#     def run(self):
#         self.logger.info(f"Management prefix: {self.mgmt_prefix}")
#
# register_jobs(MyDeviceDesign)
