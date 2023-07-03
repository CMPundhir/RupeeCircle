from .models import LogHistory


class LogHistoryService():

    def create(self, user, ip, location, platform):
        self.current_log_session = LogHistory.objects.create(user=user,
                                                        ip=ip,
                                                        location=location,
                                                        platform=platform)
        return print('LogHistory created.')

    def update(self, activity):
        self.current_log_session.activity.add(activity)
        self.current_log_session.save()
        return print('LogHistory saved.')
    