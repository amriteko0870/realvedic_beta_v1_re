from datetime import datetime
import pytz
from django.db import models

# Create your models here.

class admin_login(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    phone_code = models.TextField()
    phone_no = models.TextField()
    password = models.TextField()
    token = models.TextField()

class actionLogs(models.Model):
    user = models.TextField()
    log_message = models.TextField()
    date_time = models.TextField(default=str(datetime.now(pytz.timezone("Asia/Kolkata"))))