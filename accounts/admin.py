from django.contrib import admin

from accounts.models import EmailOTP, UserProfile

admin.site.register(UserProfile)
admin.site.register(EmailOTP)
