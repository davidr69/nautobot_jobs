import netaddr
from nautobot_design_builder.context import Context

class MyDesignContext(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Calculate IPs here so the YAML stays clean
        mgmt_prefix = getattr(self, "mgmt_prefix", kwargs.get("mgmt_prefix"))
        prefix = netaddr.IPNetwork(mgmt_prefix)
        self.device_ips = {
            "device1": str(prefix[1]) + f"/{prefix.prefixlen}",
            "device2": str(prefix[2]) + f"/{prefix.prefixlen}",
        }
