from django.contrib import admin
from admin_realvedic_app.models import admin_login
from admin_realvedic_app.models import actionLogs
# Register your models here.

admin.site.register(admin_login)
admin.site.register(actionLogs)