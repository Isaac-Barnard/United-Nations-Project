from django.contrib import admin
from . import models

#admin.site.register(models.Resolution)
#admin.site.register(models.Treaty)
admin.site.register(models.Executive_Order)
admin.site.register(models.Resolution_Amendment)
admin.site.register(models.Charter)
admin.site.register(models.Charter_Amendment)
admin.site.register(models.Declaration_Of_War)
admin.site.register(models.National_Constitution)
admin.site.register(models.National_Constitution_Amendment)

class ResolutionImageInline(admin.TabularInline):
    model = models.Resolution_Image
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    inlines = [ResolutionImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.Resolution_Image)
class ResolutionImageAdmin(admin.ModelAdmin):
    search_fields = ['resolution__title']
    ordering = ['resolution', 'order']
    
    
    
class TreatyImageInline(admin.TabularInline):
    model = models.Treaty_Image
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Treaty)
class TreatyAdmin(admin.ModelAdmin):
    inlines = [TreatyImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.Treaty_Image)
class TreatyImageAdmin(admin.ModelAdmin):
    search_fields = ['treaty__title']
    ordering = ['treaty', 'order']
    
    
    
class AllianceImageInline(admin.TabularInline):
    model = models.Alliance_Image
    extra = 1
    fields = ['image', 'order']
    ordering = ['order']

@admin.register(models.Alliance)
class AllianceAdmin(admin.ModelAdmin):
    inlines = [AllianceImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

@admin.register(models.Alliance_Image)
class AllianceImageAdmin(admin.ModelAdmin):
    search_fields = ['alliance__title']
    ordering = ['alliance', 'order']