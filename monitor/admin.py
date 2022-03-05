from django.contrib import admin

# Register your models here.


from .models import Router

class RouterAdmin(admin.ModelAdmin):
   list_display = ('ip', 'nombre')
   

admin.site.register(Router, RouterAdmin)
