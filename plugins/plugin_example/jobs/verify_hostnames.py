from nautobot.apps.jobs import Job, ObjectVar
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models.devices import Device
import re
from django.urls import reverse

HOSTNAME_PATTERN = re.compile(r"[a-z0-1]+\-[a-z]+\-\d+\.infra\.valuemart\.com")

name = "Data Quality Custom Jobs Collection"

class VerifyHostnameJob(Job):
	location_to_check = ObjectVar(
		model=Location,
		query_params={"has_devices": True},
	)

	class Meta:
		name = "Verify Hostname Pattern For Selected Locations Plugin Job"
		description = "Checks all devices at the designated location for hostname pattern conformity"

	def run(self, location_to_check):
		results = []
		for device in Device.objects.filter(location=location_to_check):
			hostname = device.name
			compliance_status = "PASS" if HOSTNAME_PATTERN.match(hostname) else "FAIL"

			if compliance_status == "PASS":
				self.logger.info(f"{hostname} is compliant.", extra={"object": device})
			else:
				self.logger.error(f"{hostname} does NOT match the hostname pattern.", extra={"object": device})

			results.append({
				"hostname": hostname,
				"device_id": device.id,
				"status": compliance_status,
				"device_url": device.get_absolute_url(),
			})

		link_url = reverse("plugins:nautobot_example_plugin:custom_job_result", args=[str(self.job_result.id)])
		self.logger.info(f'<a href="{link_url}" target="_blank">View Detailed Results</a>')

		return {"results": results, "redirect_url": link_url}
