"""
Decorators for Nautobot job retry and error handling.
"""

from functools import wraps
from django_redis import get_redis_connection
from nautobot.extras.models.jobs import Job as JobModel
from nautobot.users.models import User


def auto_retry_on_failure(max_retries=3, delay_seconds=300, redis_ttl_buffer=30):
    """
    Decorator that wraps the on_failure() method to automatically reschedule
    a job on failure with exponential or linear retry logic.

    Args:
        max_retries (int): Maximum number of retry attempts. Defaults to 3.
        delay_seconds (int): Delay in seconds before rescheduling. Defaults to 300 (5 minutes).
        redis_ttl_buffer (int): Additional TTL buffer for Redis key to avoid expiration
                               during job execution. Defaults to 30 seconds.

    Usage:
        @auto_retry_on_failure(max_retries=5, delay_seconds=600)
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            # Custom failure logic here (optional)
            pass
    """

    def decorator(on_failure_method):
        @wraps(on_failure_method)
        def wrapper(self, exc, task_id, args, kwargs, einfo):
            # Call the original on_failure method if provided
            try:
                on_failure_method(self, exc, task_id, args, kwargs, einfo)
            except Exception:
                # If custom on_failure logic fails, log but continue with retry logic
                self.logger.exception("Error in custom on_failure handler")

            # Auto-retry logic
            self.logger.error("Job failed! Attempting automatic retry...")
            self.logger.error(f"{exc=}, {task_id=}, {args=}, {kwargs=}, {einfo=}")

            redis_client = get_redis_connection("default")
            job_name = self.__class__.__name__
            redis_key = f"{job_name}.retry_count"
            redis_ttl = delay_seconds + redis_ttl_buffer

            # Get current retry count
            retry_count = redis_client.get(redis_key)

            if retry_count:
                try:
                    num = int(retry_count)
                    if num == 0:
                        redis_client.delete(redis_key)
                        self.logger.error(f"Max retries ({max_retries}) exhausted for {job_name}")
                        return

                    num -= 1
                    redis_client.set(redis_key, num, ex=redis_ttl)
                except ValueError:
                    self.logger.error(f"Invalid retry count in Redis: {retry_count}")
                    return
            else:
                # First failure, initialize retry counter
                redis_client.set(redis_key, max_retries - 1, ex=redis_ttl)
                self.logger.info(f"Initialized retry counter: {max_retries - 1} retries remaining")

            # Get the job model to reschedule
            try:
                retry_job = JobModel.objects.get(name=self.Meta.name)
            except JobModel.DoesNotExist:
                self.logger.error(f"Unable to find Job model for {self.Meta.name}; cannot reschedule.")
                return

            # Prepare arguments for rescheduling
            kwargs = kwargs or {}

            # Get user object for rescheduling
            try:
                job_user = User.objects.get(username=self.user)
            except User.DoesNotExist:
                self.logger.error(f"Unable to find user {self.user}; cannot reschedule.")
                return

            # Reschedule the job with delay
            try:
                self.job_result.enqueue_job(
                    retry_job,
                    user=job_user,
                    celery_kwargs={"countdown": delay_seconds},
                    **kwargs
                )
                retries_left = redis_client.get(redis_key)
                self.logger.info(
                    f"Job rescheduled with {delay_seconds}s delay. "
                    f"Retries remaining: {retries_left}"
                )
            except Exception as e:
                self.logger.error(f"Failed to reschedule job: {e}")

        return wrapper

    return decorator
