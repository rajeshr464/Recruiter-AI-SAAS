from django.contrib import admin

# Register your models here.
from .models import Tenant, Client, RecruiterAI, Candidate, Job, Submission, Interview, Offer, AILearningLog
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(Tenant)
admin.site.register(Client)
admin.site.register(RecruiterAI)
admin.site.register(Candidate)
admin.site.register(Job)
admin.site.register(Submission)
admin.site.register(Interview)
admin.site.register(Offer)
admin.site.register(AILearningLog)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(BaseUserAdmin):
	ordering = ['email']
	list_display = ['email', 'name', 'tenant', 'is_staff', 'is_active']
	search_fields = ['email', 'name']
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Personal info'), {'fields': ('name', 'tenant', 'phone', 'region', 'title')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'name', 'tenant', 'password1', 'password2'),
		}),
	)

admin.site.register(User, CustomUserAdmin)
