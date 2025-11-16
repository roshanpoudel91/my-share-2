from django.contrib import admin
from .models import Industry, Company, Contact
# Register your models here.

class ContactAdmin(admin.ModelAdmin):
	readonly_fields=['created_at',]

admin.site.register(Contact, ContactAdmin)
admin.site.register(Industry)
admin.site.register(Company)