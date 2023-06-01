from .models import ActivityTracker


class LogService():

    def log(user, msg="NA", url="NA", ref="NA", is_transaction=False):
        user = user
        msg = msg
        is_transaction = is_transaction
        instance = ActivityTracker.objects.create(user=user, msg=msg, is_transaction=is_transaction)
        return print("Created Notification.")

