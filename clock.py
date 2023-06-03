from server import send_daily_alerts
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='*', hour=9)
def scheduled_alert():
    send_daily_alerts()

sched.start()