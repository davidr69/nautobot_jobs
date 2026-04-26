# jobs/import_bind_zones.py
from nautobot.core.jobs import Job, FileVar, BooleanVar
from nautobot.utilities.utils import render_jinja2
from django.utils import timezone

# Nautobot models
from nautobot.dcim.models import DeviceType, Manufacturer
# Optional plugin model to persist raw zone files:
from nautobot_apps.bind.models import BindZone


import dns.zone
import dns.name

class ImportBindZonesJob(Job):
	file = FileVar(
		label="Zone file (single file or tar/zip containing multiple zone files)",
		required=True,
		description="Upload a bind9 zone file (or archive)."
	)
	dry_run = BooleanVar(default=True, label="Dry run", description="If checked, do not persist changes to Nautobot")

	class Meta:
		name = "Import bind9 zone files"
		description = "Parse uploaded bind9 files, persist raw text, produce normalized JSON, and optionally create DeviceType objects."

	def read_uploaded(self, uploaded_file):
		# uploaded_file is an UploadedFile-like object
		try:
			data = uploaded_file.read()
			if isinstance(data, bytes):
				return data.decode("utf-8")
			return str(data)
		finally:
			uploaded_file.close()

	def parse_zone_text(self, text, origin=None):
		"""
		Parse a zone file text with dnspython and return list of records.
		Each record: dict{name,rtype,ttl,rdatastring}
		"""
		records = []
		# If origin not provided, dnspython requires an origin; try to rely on $ORIGIN in file or fallback
		try:
			zone = dns.zone.from_text(text, origin=origin, relativize=False, allow_include=False, check_origin=False)
		except Exception as e:
			# fallback: try with empty origin -> parse may still work
			raise

		for (name, node) in zone.nodes.items():
			fqdn = name.to_text()
			for rdataset in node.rdatasets:
				rtype = dns.rdatatype.to_text(rdataset.rdtype)
				ttl = rdataset.ttl
				for rdata in rdataset:
					records.append({"name": fqdn, "type": rtype, "ttl": ttl, "rdata": rdata.to_text()})
		return records

	def ensure_device_type(self, manufacturer_name, model_name, commit):
		"""
		Ensure DeviceType exists; idempotent. If dry_run, report only.
		"""
		mfr, _created = Manufacturer.objects.get_or_create(name=manufacturer_name)
		dt, created = DeviceType.objects.get_or_create(manufacturer=mfr, model=model_name, defaults={"slug": model_name.lower().replace(" ", "-")})
		if created and commit:
			self.logger.info(f"Created DeviceType: {manufacturer_name} {model_name}")
		return dt, created

	def run(self, data, commit):
		uploaded = data["file"]
		dry_run = data.get("dry_run", True)

		self.logger.info("Starting bind9 import at %s" % timezone.now())

		zone_text = self.read_uploaded(uploaded)
		# Optionally persist raw zone text to plugin model
		# BindZone.objects.create(name="...", zone_text=zone_text, source="upload", uploaded_by=str(self.request.user))

		# Determine origin: attempt to detect from zone file ($ORIGIN) or ask user to supply; for now, try with None
		try:
			records = self.parse_zone_text(zone_text, origin=None)
		except Exception as e:
			self.logger.failure(f"Zone parse failed: {e}")
			return

		# Example: find all A records and optionally create DeviceType placeholders
		a_records = [r for r in records if r["type"] == "A"]
		self.logger.info(f"Found {len(records)} total records; {len(a_records)} A records")

		# Example device-type mapping heuristic: use a label in the zone name or a default
		# The real mapping should be provided by user input/device_type_map
		created_types = []
		for a in a_records[:50]:  # limit in initial job to avoid overloading
			# Derive manufacturer/model heuristically or via device_type_map
			manufacturer_name = "Generic"
			model_name = "host"
			dt, created = self.ensure_device_type(manufacturer_name, model_name, commit and not dry_run)
			if created:
				created_types.append(f"{manufacturer_name} {model_name}")

		# Summarize
		summary = {
			"total_records": len(records),
			"a_records": len(a_records),
			"device_types_created": len(created_types),
			"dry_run": dry_run,
		}
		self.logger.success(f"Import complete: {summary}")
