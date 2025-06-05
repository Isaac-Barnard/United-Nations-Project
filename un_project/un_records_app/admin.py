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
    list_display = ['title', 'date', 'proposed_by', 'votes_for', 'votes_against', 'void', 'repealed', 'image_count']
    list_filter = ['void', 'repealed', 'date', 'proposed_by']
    search_fields = ['title', 'body']
    fields = ['title', 'date', 'proposed_by', 'votes_for', 'votes_against', 'body', 'void', 'repealed', 'invalidation_date']
    inlines = [ResolutionImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.ResolutionImage)
class ResolutionImageAdmin(admin.ModelAdmin):
    list_display = ['resolution', 'order']
    list_filter = ['resolution']
    search_fields = ['resolution__title']
    ordering = ['resolution', 'order']