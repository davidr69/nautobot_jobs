from nautobot.apps.jobs import Job, register_jobs, TextVar
from django_redis import get_redis_connection

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

        redis_client = get_redis_connection("default")

        keys_list = keys.strip().split(",")
        redis_keys = redis_client.keys("*")

        response = {}

        for key in redis_keys:
            key_str = key.decode("utf-8")
            if any(part in key_str for part in keys_list):
                value = redis_client.get(key).decode("utf-8")
                response[key_str] = value

        self.logger.info(f"Result: {response}")


register_jobs(GetRedisValues)
