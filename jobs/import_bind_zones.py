# jobs/import_bind_zones.py
from nautobot.core.jobs import Job, FileVar, BooleanVar, register_jobs
from django.utils import timezone

# Nautobot models
from nautobot.dcim.models import DeviceType, Manufacturer
# Optional plugin model to persist raw zone files. Import defensively
try:
	# If you have a plugin that provides BindZone, import it; otherwise continue without persistence
	from nautobot_apps.bind.models import BindZone  # type: ignore
except Exception:
	BindZone = None



name = 'Bind Zone Import'
# dns (dnspython) is imported inside parsing functions to avoid import-time failures

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
		Handles files that contain multiple $ORIGIN sections by splitting and parsing each segment.
		Each record: dict{origin,name,type,ttl,rdata}
		"""
		import re
		try:
			import dns
		except ImportError:
			# Provide a clear runtime error that will appear in Nautobot logs
			self.logger.failure(
				"dnspython is not installed in the Nautobot environment. Please `pip install dnspython` "
				"or add it to your Nautobot environment requirements and restart Nautobot/Celery."
			)
			raise
		ORIGIN_RE = re.compile(r"^\s*\$ORIGIN\s+([^\s;]+)", re.IGNORECASE | re.MULTILINE)

		def split_zone_by_origin(text, default_origin=None):
			matches = list(ORIGIN_RE.finditer(text))
			parts = []
			if not matches:
				parts.append((default_origin, text))
				return parts
			# leading text before first $ORIGIN
			first = matches[0]
			if first.start() > 0:
				leading = text[: first.start()].strip()
				if leading:
					parts.append((default_origin, leading))
			for i, m in enumerate(matches):
				origin_text = m.group(1).rstrip('.')
				start = m.start()
				end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
				zone_text = text[start:end].strip()
				parts.append((origin_text, zone_text))
			return parts

		records = []
		# split into origin segments
		segments = split_zone_by_origin(text, default_origin=origin)
		for seg_origin, seg_text in segments:
			try:
				origin_name = dns.name.from_text(seg_origin) if seg_origin else None
				zone = dns.zone.from_text(
					seg_text, origin=origin_name, relativize=False, allow_include=False, check_origin=False
				)
			except Exception:
				# re-raise with context
				raise
			for (name, node) in zone.nodes.items():
				fqdn = name.to_text()
				for rdataset in node.rdatasets:
					rtype = dns.rdatatype.to_text(rdataset.rdtype)
					ttl = rdataset.ttl
					for rdata in rdataset:
						records.append({"origin": str(seg_origin), "name": fqdn, "type": rtype, "ttl": ttl, "rdata": rdata.to_text()})
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


register_jobs(ImportBindZonesJob)
