from django.contrib import admin
from . import models

#admin.site.register(models.Resolution)
#admin.site.register(models.Treaty)
admin.site.register(models.Executive_Order)
admin.site.register(models.ResolutionAmendment)
admin.site.register(models.Charter)
admin.site.register(models.CharterAmendment)

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
    
    
    
class TreatyImageInline(admin.TabularInline):
    model = models.TreatyImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Treaty)
class TreatyAdmin(admin.ModelAdmin):
    inlines = [TreatyImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.TreatyImage)
class TreatyImageAdmin(admin.ModelAdmin):
    search_fields = ['treaty__title']
    ordering = ['treaty', 'order']
    
    
    
class AllianceImageInline(admin.TabularInline):
    model = models.AllianceImage
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Alliance)
class AllianceAdmin(admin.ModelAdmin):
    inlines = [AllianceImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.AllianceImage)
class AllianceImageAdmin(admin.ModelAdmin):
    search_fields = ['alliance__title']
    ordering = ['alliance', 'order']