from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(CartographyMap)
class CartographyMapAdmin(admin.ModelAdmin):
    list_display = ("type", "map_date", "slug")
    readonly_fields = ("slug",)
    ordering = ("-map_date",)