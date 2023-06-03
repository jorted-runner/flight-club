from server import send_daily_alerts
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='*', hour=3, minute=6)
def scheduled_alert():
    send_daily_alerts()

sched.start()