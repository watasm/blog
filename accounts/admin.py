from django.contrib import admin
from accounts.models import Profile, Preference, Contact

admin.site.register(Profile)
admin.site.register(Preference)
admin.site.register(Contact)
