from django.urls import path
from nautobot_example_plugin.views import CustomJobResultView

urlpatterns = [
	path("verifyhostname-results/<uuid:pk>/", CustomJobResultView.as_view(), name="custom_job_result"),
]
