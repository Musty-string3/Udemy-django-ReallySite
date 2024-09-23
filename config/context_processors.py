from blog.models import Notification

# SettingsのTEMPLATESの中に記述することでどこでも通知のカウント数を得られる
def notification_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {'notification_count': count}