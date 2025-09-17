from nautobot.apps.jobs import MultiChoiceVar, Job, ObjectVar, register_jobs, StringVar, IntegerVar
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models.devices import Device

name = "Data Quality Jobs Collection"


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

register_jobs(
	VerifyPlatform
)
