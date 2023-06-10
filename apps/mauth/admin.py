from django.contrib import admin

# Register your models here.
# admin.site.register()
from django.contrib import admin  
from django.contrib.auth import authenticate  
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin  
# Register your models here.  
class CustomUserAdmin(UserAdmin):  
    # add_form = CustomUserCreationForm  
    # form = CustomUserChangeForm  
    # model = CustomerUser  
  
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_superuser')  
    list_filter = ('email', 'is_staff', 'is_active', 'role')  
    fieldsets = (  
        (None, {'fields': ('email', 'password')}),  
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),  
    )  
    add_fieldsets = (  
        (None, {  
            'classes': ('wide',),  
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}  
        ),  
    )  
    search_fields = ('email',)  
    ordering = ('email',)  
    filter_horizontal = ()  
  
admin.site.register(CustomUser, CustomUserAdmin)  