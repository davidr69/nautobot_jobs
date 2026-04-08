import json
from pathlib import Path
from nautobot_design_builder.context import Context

_DATA_FILE = Path(__file__).parent.parent / "data" / "device_ips.json"


class MyDesignContext(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(_DATA_FILE, encoding="utf-8") as f:
            self.device_ips = json.load(f)
