import netaddr
from nautobot_design_builder.context import Context

class MyDesignContext(Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Calculate IPs here so the YAML stays clean
        prefix = netaddr.IPNetwork(self.mgmt_prefix)
        self.device_ips = {
            "device1": str(prefix[1]) + f"/{prefix.prefixlen}",
            "device2": str(prefix[2]) + f"/{prefix.prefixlen}",
        }
