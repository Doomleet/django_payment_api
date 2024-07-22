from django.contrib import admin

from .models import WaterChecker, Flat, Home, Street


class FlatInline(admin.TabularInline):
    model = Home.flats.through
    extra = 1


class HomeAdmin(admin.ModelAdmin):
    inlines = [FlatInline]


admin.site.register(WaterChecker)
admin.site.register(Flat)
admin.site.register(Home, HomeAdmin)
admin.site.register(Street)
