from nautobot.apps.jobs import Job, register_jobs, TextVar

name = "Redis Management"


class GetRedisValues(Job):
    class Meta:
        name = "Get Values"  # job name
        description = "Get Values from Redis"
        has_sensitive_variables = False
        soft_time_limit = 60
        time_limit = 90
        read_only = True
        is_singleton = False

    keys = TextVar(description="Partial keys allowed", default="openapi_schema_cache")

    def run(self, keys):
        self.logger.info(f"You selected: {keys}")


register_jobs(GetRedisValues)
