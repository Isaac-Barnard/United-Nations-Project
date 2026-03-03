from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(CartographyMap)
class CartographyMapAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "map_date")
    ordering = ("-map_date",)