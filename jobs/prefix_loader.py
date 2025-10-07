from nautobot.apps.jobs import Job, register_jobs, ObjectVar
from nautobot.tenancy.models import Tenant
from nautobot.ipam.models import Prefix, Namespace
from nautobot.extras.models.statuses import Status
from nautobot.ipam.choices import PrefixTypeChoices

name = 'IPAM stuff'

class PrefixLoader(Job):
	parent = ObjectVar(
		model = Prefix,
		label = "Parent Prefix"
	)

	tenant = ObjectVar(
		model = Tenant,
		required = True
	)

	class Meta:
		name = "Prefix Loader"
		description = "Load prefixes from a predefined list"

	def run(self, parent, tenant):
		fake_data = ['10.0.10.0/24', '10.0.20.0/24', '10.0.30.0/24']
		status = Status.objects.get(name = "Active")
		namespace = Namespace.objects.get(name = "Global")

		for prefix in fake_data:
			self.logger.info(f"Would create prefix {prefix} for tenant {tenant}")
			pf = Prefix(
				prefix = prefix,
				parent = parent,
				description = f'parent = {parent}',
				status = status,
				namespace = namespace,
				tenant = tenant,
				type = PrefixTypeChoices.TYPE_NETWORK
			)
			pf.save()

register_jobs(PrefixLoader)
