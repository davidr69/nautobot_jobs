import re

from nautobot.apps.jobs import MultiChoiceVar, Job, ObjectVar, register_jobs, StringVar, IntegerVar
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models.devices import Device

name = "Data Quality Jobs Collection"
HOSTNAME_PATTERN = re.compile(r"[a-z0-1]+\-[a-z]+\-\d+\.infra\.valuemart\.com")


class VerifyPlatform(Job):

	location_to_check = ObjectVar(
		model=Location,
		query_params = {
			"has_devices": True
		}
	)

	class Meta:
		name = "Check Platform is defined"
		has_sensitive_variables = False
		description = "Check Platform is defined for devices in selected location"

	def run(self, location_to_check):
		device_query = Device.objects.filter(location=location_to_check)

		for device in device_query:
			self.logger.info(
				"Checking the device %s for Platform specified.",
				device.name,
				extra={"object": device},
			)

			# Verify that the device has a platform set
			if device.platform is None:
				self.logger.fatal(f"{device} does not have platform set.")
				return

			else:
				self.logger.debug(
					"Device %s is of the platform: %s",
					device.name,
					device.platform,
					extra={"object": device},
				)

class VerifySerialNumber(Job):

	location_to_check = ObjectVar(
		model=Location,
		query_params={
			"has_devices": True,
		}
	)

	class Meta:
		name = "Check Serial Numbers"
		has_sensitive_variables = False
		description = "Check serial numbers exist for devices in the selected location"

	def run(self, location_to_check):
		device_query = Device.objects.filter(location=location_to_check)

		for device in device_query:
			self.logger.info(
				"Checking the device %s for a serial number.",
				device.name,
				extra={"object": device},
			)
			if device.serial == "":
				self.logger.error(
					"Device %s does not have serial number defined.",
					device.name,
					extra={"object": device},
				)
			else:
				self.logger.debug(
					"Device %s has serial number: %s",
					device.name,
					device.serial,
					extra={"object": device},
				)


class VerifyPrimaryIP(Job):

	location_to_check = ObjectVar(
		model=Location,
		query_params={
			"has_devices": True,
		}
	)

	class Meta:
		name = "Verify Device has at selected location has Primary IP configured"
		has_sensitive_variables = False
		description = "Check Device at selected location Primary IP configured"

	def run(self, location_to_check):
		device_query = Device.objects.filter(location=location_to_check)

		for device in device_query:
			self.logger.info(
				"Checking the device %s for Primary IP.",
				device.name,
				extra={"object": device},
			)

			# Verify that the device has a primary IP
			if device.primary_ip is None:
				self.logger.fatal(f"{device} does not have a primary IP address configured.")
				return

			else:
				self.logger.debug(
					"Device %s has primary IP: %s",
					device.name,
					device.primary_ip,
					extra={"object": device},
				)


class VerifyHostname(Job):
	location_to_check = ObjectVar(
		model=Location,
		query_params={
			"has_devices": True,
		}
	)

	class Meta:

		name = "Verify Hostname Pattern For Selected Locations"
		description = "Checks all devices at Designated Location for hostname pattern conformation"

	def run(self, location_to_check):
		"""Run method for executing the checks on the devices."""

		# Iterate through each Device object, limited to just the location of choice.
		for device in Device.objects.filter(location=location_to_check):
			hostname = device.name
			self.logger.info(
				f"Checking device hostname compliance: {hostname}",
				extra={"object": device},
			)
			# Check if the hostname matches the expected pattern
			if HOSTNAME_PATTERN.match(hostname):
				self.logger.info(f"{hostname} configured hostname is correct.")
				# Skip to next iteration of the list
				continue

			# Mark the Device as failed in the job results
			self.logger.error(f"{hostname} does Not Match Hostname Pattern.")


register_jobs(
	VerifySerialNumber,
	VerifyPrimaryIP,
	VerifyPlatform,
	VerifyHostname
)
