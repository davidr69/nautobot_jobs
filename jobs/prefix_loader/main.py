from nautobot.apps.jobs import Job, register_jobs, ObjectVar
from nautobot.tenancy.models import Tenant
from nautobot.ipam.models import Prefix, Namespace
from nautobot.extras.models.statuses import Status
from nautobot.ipam.choices import PrefixTypeChoices
from nautobot.extras.models.secrets import SecretsGroup

name = 'IPAM stuff'

class PrefixLoader(Job):
	parent = ObjectVar(
		model = Prefix,
		label = "Parent Prefix",
		required = True
	)

	tenant = ObjectVar(
		model = Tenant,
		label = 'Select a tenant',
		required = True
	)

	class Meta:
		name = "Prefix Loader"
		description = "Load prefixes from a predefined list"
		has_sensitive_variables = False

	def run(self, parent, tenant):
		fake_data = ['10.0.10.0/24', '10.0.20.0/24', '10.0.30.0/24']
		status = Status.objects.get(name = "Active")
		namespace = Namespace.objects.get(name = "Global")

		for prefix in fake_data:
			self.logger.info(f"Can I create prefix {prefix} for tenant {tenant}?")
			pf, created = Prefix.objects.get_or_create(
				prefix = prefix,
				parent = parent,
				namespace = namespace,
				tenant = tenant,
				defaults = {
					'description' : f'parent = {parent}',
					'status' : status,
					'type' : PrefixTypeChoices.TYPE_NETWORK
				}
			)
			if created:
				self.logger.info(f"Created prefix {prefix}")
			else:
				self.logger.info(f"Prefix {prefix} already exists, skipping")

		group = SecretsGroup.objects.get(name = 'container labs ssh')
		user = group.get_secret_value(secret_type='username', access_type='Generic')
		pwd = group.get_secret_value(secret_type='password', access_type='Generic')

		self.logger.info(f"Username from secrets group: {user}, password: {pwd}")

register_jobs(PrefixLoader)
