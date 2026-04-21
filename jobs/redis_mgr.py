from nautobot.apps.jobs import Job, register_jobs, TextVar
from django_redis import get_redis_connection


name = "Redis Management"


class GetRedisKeys(Job):
    class Meta:
        name = "Get Keys"  # job name
        description = "Get Keys from Redis"
        has_sensitive_variables = False
        soft_time_limit = 60
        time_limit = 90
        read_only = True
        is_singleton = False

    keys = TextVar(description='Partial keys allowed; enter "*" for all keys', default="openapi_schema_cache", required=True)

    def run(self, keys):
        response = []

        redis_client = get_redis_connection("default")
        redis_keys = redis_client.keys("*")

        raw_keys = [ key.decode("utf-8") for key in redis_keys ]

        if keys == "*":
            self.logger.info("Getting all keys")
            response = raw_keys
        else:
            keys_list = keys.replace("\r", "").split("\n")
            self.logger.info(f"Keys list: {keys_list}")

            for key in raw_keys:
                if any(part in key for part in keys_list):
                    response.append(key)

        response.sort()
        self.logger.info('<pre>' + "\n".join(response) + '</pre>')


class DropRedisKeys(Job):
    class Meta:
        name = "Drop Keys"  # job name
        description = "Drop Keys from Redis"
        has_sensitive_variables = False
        soft_time_limit = 60
        time_limit = 90
        read_only = True
        is_singleton = False

    keys = TextVar(description='Partial keys allowed; enter "*" for all keys', required=True)

    def run(self, keys):
        keys_list = []

        redis_client = get_redis_connection("default")
        redis_keys = redis_client.keys("*")

        raw_keys = [ key.decode("utf-8") for key in redis_keys ]

        if keys == "*":
            self.logger.info("Dropping all keys")
        else:
            keys_list = keys.replace("\r", "").split("\n")
            self.logger.info(f"Keys list: {keys_list}")

        for key in raw_keys:
            if keys == '*' or key in keys_list:
                if redis_client.delete(key) == 1:
                    self.logger.info(f"Deleted key: {key}")
                else:
                    self.logger.info(f"Failed to delete key: {key}")


register_jobs(GetRedisKeys, DropRedisKeys)
