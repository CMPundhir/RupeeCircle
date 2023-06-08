from .models import ActivityTracker
from apps.wallet.models import Transaction


class LogService():

    def log(user, msg="NA", url="NA", ref="NA", is_transaction=False):
        user = user
        msg = msg
        is_transaction = is_transaction
        instance = ActivityTracker.objects.create(user=user, msg=msg, is_transaction=is_transaction)
        return print("Notification Created.")
    
    def transaction_log(owner, wallet, amount, url="NA", ref="NA"):
        owner=owner
        wallet=wallet
        amount=amount
        instance = Transaction.objects.create(wallet=wallet, owner=owner, amount=amount)
        return print('Transaction Created')


