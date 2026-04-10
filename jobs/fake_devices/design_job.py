from nautobot.apps.jobs import StringVar, register_jobs
from nautobot.dcim.models import Device
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
        has_sensitive_variables = False

    def post_implementation(self, context, design_builder):
        for device_data in context.data["devices"]:
            device = Device.objects.get(name=device_data["hostname"])
            ip = device.interfaces.get(name="GigabitEthernet0/0").ip_addresses.first()
            if ip:
                device.primary_ip4 = ip
                device.save()


register_jobs(MyDeviceDesign)
