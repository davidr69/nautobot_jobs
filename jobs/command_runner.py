import os

from django.conf import settings
from nautobot.apps.jobs import (
    MultiChoiceVar,
    Job,
    ObjectVar,
    register_jobs,
    StringVar,
    IntegerVar,
)
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models.devices import Device
from nautobot.dcim.models.device_components import Interface
from netmiko import ConnectHandler
from nautobot.ipam.models import VLAN
from nautobot.apps.jobs import JobButtonReceiver


name = "Network Operations"


COMMAND_CHOICES = (
    ("show ip interface brief", "show ip int bri"),
    ("show ip route", "show ip route"),
    ("show version", "show version"),
    ("show log", "show log"),
    ("show ip ospf neighbor", "show ip ospf neighbor"),
)


class CommandRunner(Job):
    device_location = ObjectVar(model=Location, required=False)

    device = ObjectVar(
        model=Device,
        query_params={
            "location": "$device_location",
        },
    )

    commands = MultiChoiceVar(choices=COMMAND_CHOICES)

    class Meta:
        name = "Command Runner"
        has_sensitive_variables = False
        description = "Command Runner"

    def run(self, device, commands):
        self.logger.info("Device name: %s", device.name)

        # Verify that the device has a primary IP
        if device.primary_ip is None:
            self.logger.fatal("Device does not have a primary IP address set.")
            return

        # Verify that the device has a platform associated
        if device.platform is None:
            self.logger.fatal("Device does not have a platform set.")
            return

        # check for device driver association
        if device.platform.network_driver_mappings.get("netmiko") is None:
            self.logger.fatal("Device mapping for Netmiko is not present, please set.")
            return

        # Connect to the device, get some output - comment this out if you are simulating
        net_connect = ConnectHandler(
            device_type=device.platform.network_driver_mappings["netmiko"],
            host=device.primary_ip.host,  # or device.name if your name is an FQDN
            # username=os.getenv("DEVICE_USERNAME"),  # change to use user_name
            # password=os.getenv("DEVICE_PASSWORD"),
            username="admin",
            password="admin",
        )
        for command in commands:
            output = net_connect.send_command(command)
            self.create_file(f"{device.name}-{command}.txt", output)


class ChangeVLAN(Job):
    device_location = ObjectVar(model=Location, required=False)

    device = ObjectVar(
        model=Device,
        query_params={
            "location": "$device_location",
        },
    )

    interface = ObjectVar(
        model=Interface, query_params={"device_id": "$device", "name__ic": "Ethernet"}
    )

    # Specify a job input VLAN to be implemented
    vlan = IntegerVar()

    class Meta:
        name = "Change VLAN for Port"
        description = "Change VLAN based on Selected Port."

    def run(self, device, interface, vlan):
        """Run method for executing the checks on the device."""
        self.logger.info(f"Device: {device.name}, Interface: {interface}")

        # Verify that the device has a primary IP
        if device.primary_ip is None:
            self.logger.fatal("Device does not have a primary IP address set.")
            return

        # Verify that the device has a platform associated
        if device.platform is None:
            self.logger.fatal("Device does not have a platform set.")
            return

        # check for device driver association
        if device.platform.network_driver_mappings.get("netmiko") is None:
            self.logger.fatal("Device mapping for Netmiko is not present, please set.")
            return

        # Connect to the device, get some output - comment this out if you are simulating
        net_connect = ConnectHandler(
            device_type=device.platform.network_driver_mappings["netmiko"],
            host=device.primary_ip.host,  # or device.name if your name is an FQDN
            username="admin",
            password="admin",
        )

        # Easy mapping of platform to device command
        COMMAND_MAP = {
            "cisco_nxos": [f"interface {interface}", f"switchport access vlan {vlan}"],
            "arista_eos": [f"interface {interface}", f"switchport access vlan {vlan}"]
        }

        commands = COMMAND_MAP[device.platform.network_driver_mappings.get("netmiko")]
        self.logger.info(f"This is the command: {commands}")

        net_connect.enable()
        output = net_connect.send_config_set(commands)
        net_connect.save_config()
        net_connect.disconnect()
        self.logger.info(f"This is the output: {output}")

        # If an exception is not raise the configuration was implemented successfully
        self.logger.info(
            interface, f"Successfully added to {interface.name} on {device.name}!"
        )


class ChangeVlanByFunction(Job):
    device_location = ObjectVar(model=Location, required=False)

    device = ObjectVar(
        model=Device,
        query_params={
            "location": "$device_location",
        },
    )

    interface = ObjectVar(
        model=Interface, query_params={"device_id": "$device", "name__ic": "Ethernet"}
    )

    vlan = ObjectVar(model=VLAN)

    class Meta:
        name = "Change VLAN on Port by existing VLAN"
        description = "Change VLAN on Port by existing VLAN."

    def run(self, device, interface, vlan):
        """Run method for executing the checks on the device."""
        self.logger.info(f"Device: {device.name}, Interface: {interface}")

        # Verify that the device has a primary IP
        if device.primary_ip is None:
            self.logger.fatal("Device does not have a primary IP address set.")
            return

        # Verify that the device has a platform associated
        if device.platform is None:
            self.logger.fatal("Device does not have a platform set.")
            return

        # check for device driver association
        if device.platform.network_driver_mappings.get("netmiko") is None:
            self.logger.fatal("Device mapping for Netmiko is not present, please set.")
            return

        # Connect to the device, get some output - comment this out if you are simulating
        net_connect = ConnectHandler(
            device_type=device.platform.network_driver_mappings["netmiko"],
            host=device.primary_ip.host,  # or device.name if your name is an FQDN
            username="admin",
            password="admin",
        )

        # Easy mapping of platform to device command
        COMMAND_MAP = {
            "cisco_nxos": [
                f"interface {interface}",
                f"switchport access vlan {vlan.vid}",
            ],
            "arista_eos": [
                f"interface {interface}",
                f"switchport access vlan {vlan.vid}",
            ],
        }

        commands = COMMAND_MAP[device.platform.network_driver_mappings.get("netmiko")]
        self.logger.info(f"This is the command: {commands}")

        net_connect.enable()
        output = net_connect.send_config_set(commands)
        net_connect.save_config()
        net_connect.disconnect()
        self.logger.info(f"This is the output: {output}")

        # If an excpetion is not raise the configuration was implemented successfully
        self.logger.info(
            interface,
            f"Successfully added VLAN {vlan.name} to {interface.name} on {device.name}!",
        )


class NotAJob:
    def __init__(self):
        print("This is not a job")


register_jobs(
    ChangeVLAN,
    ChangeVlanByFunction,
    CommandRunner
)
