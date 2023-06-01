from django.db import models
from apps.mauth.models import CustomUser as User

# Create your models here.


class ActivityTracker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="ActivityTrackerUser", on_delete=models.PROTECT)
    msg = models.CharField(max_length=255, default="NA")
    ref = models.CharField(max_length=255, default="NA")
    url = models.URLField(max_length=255, default="NA")
    type = models.CharField(max_length=64, default="NA")
    is_transaction = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
     return f"{self.msg}"

    class Meta:
        db_table = "notification_app"
