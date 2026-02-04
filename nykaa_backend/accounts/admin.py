from django.contrib import admin
from .models import User, UserOTP, Wallet

admin.site.register(User)
admin.site.register(UserOTP)
admin.site.register(Wallet)
