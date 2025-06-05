from django.contrib import admin
from . import models

#admin.site.register(models.Resolution)
admin.site.register(models.Treaty)

class ResolutionImageInline(admin.TabularInline):
    model = models.ResolutionImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    inlines = [ResolutionImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.ResolutionImage)
class ResolutionImageAdmin(admin.ModelAdmin):
    search_fields = ['resolution__title']
    ordering = ['resolution', 'order']