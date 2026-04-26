# plugins/nbot_bind/models.py
from django.db import models
from nautobot.core.models.generics import PrimaryModel

class BindZone(PrimaryModel):
	name = models.CharField(max_length=255)   # e.g., "db.lavacro.net" or filename
	zone_text = models.TextField()
	source = models.CharField(max_length=255, blank=True, null=True)  # repo or uploader
	uploaded_by = models.CharField(max_length=255, blank=True, null=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name
