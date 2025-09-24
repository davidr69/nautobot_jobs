from nautobot.extras.views import JobResultView  # Import the built-in view

class CustomJobResultView(JobResultView):
	"""
	This view customizes Nautobot's built-in JobResultView.
	Since JobResultView already implements ObjectPermissionRequiredMixin,
	we don't need to include it again.
	"""
	template_name = "nautobot_example_plugin/customized_jobresult.html"

	def get_context_data(self, **kwargs):
		# Call the superclass implementation to get the default context.
		context = super().get_context_data(**kwargs)
		# The JobResult object is available in the context as 'object'.
		job_result = context.get("object")
		if job_result and job_result.result:
			context["results"] = job_result.result.get("results", [])
		else:
			context["results"] = []
		# Add any additional context variables here.
		context["custom_message"] = "This is my custom job result view."
		return context

# This dictionary tells Nautobot to use your custom view for job results.
override_views = {
	"extras:jobresult": CustomJobResultView.as_view(),
}
