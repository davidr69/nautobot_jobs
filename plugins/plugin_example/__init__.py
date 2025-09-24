from nautobot.extras.plugins import PluginConfig

class ExampleConfig(PluginConfig):
	"""Plugin configuration for the nautobot_example plugin."""

	name = "nautobot_example_plugin"
	verbose_name = "Simple Project for Example"
	version = "0.1.1"
	author = "Network to Code"
	description = ""
	base_url = "example"
	required_settings = []
	default_settings = {}
	caching_config = {}

config = ExampleConfig  # pylint: disable=invalid-name
