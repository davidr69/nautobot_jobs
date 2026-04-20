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

        keys_list = keys.strip().split("\n")
        redis_keys = redis_client.keys("*")

        response = []

        for key in redis_keys:
            key_str = key.decode("utf-8")
            for search in keys_list:
                if key_str.find(search) != -1:
                    response.append(key_str)
                    break

        response.sort()
        self.logger.info("\n".join(response))


register_jobs(GetRedisValues)
