from django.contrib import admin
from .models import Homestays, HomestayImages, Facilities, Rooms


class HomestayImagesInline(admin.TabularInline):
    model = HomestayImages
    extra = 1


class FacilitiesInline(admin.TabularInline):
    model = Facilities
    extra = 1


class RoomsInline(admin.TabularInline):
    model = Rooms
    extra = 1


class HomestaysAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'address', 'price', 'max_capacity', 'status')
    list_filter = ('status', 'max_capacity')
    search_fields = ('name', 'address')
    inlines = [HomestayImagesInline, FacilitiesInline, RoomsInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'area', 'address', 'price', 'discount', 'max_capacity', 'status', 'description', 'map_key')
        }),
    )


admin.site.register(Homestays, HomestaysAdmin)


class HomestayImagesAdmin(admin.ModelAdmin):
    list_display = ('image_key', 'homestay')
    search_fields = ('image_key',)


admin.site.register(HomestayImages, HomestayImagesAdmin)


class FacilitiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_key', 'homestay')
    list_filter = ('homestay',)
    search_fields = ('name',)


admin.site.register(Facilities, FacilitiesAdmin)


class RoomsAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'homestay')
    list_filter = ('homestay',)
    search_fields = ('name',)


admin.site.register(Rooms, RoomsAdmin)
