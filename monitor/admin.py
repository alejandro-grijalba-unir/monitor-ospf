from django.contrib import admin

# Register your models here.


from .models import LSDB,Router

class RouterAdmin(admin.ModelAdmin):
   list_display = ('ip', 'nombre')
   
class LSDBAdmin(admin.ModelAdmin):
   list_display = ('nombre',)

admin.site.register(LSDB, LSDBAdmin)
admin.site.register(Router, RouterAdmin)
