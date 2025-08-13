from django.contrib import admin

from main.models import *


class ProductAdmin(admin.ModelAdmin):
    list_filter = ['category']
    ordering = ["category"]
    search_fields = ["name"]
    list_display = ('category', 'name', 'active_ingredient', 'presentation')


class VisitItemAdminInline(admin.TabularInline):
    model = VisitItem


class VisitAdmin(admin.ModelAdmin):
    list_filter = ['created_at', 'user']
    list_display = ('name', 'user', 'created_at')
    inlines = [VisitItemAdminInline]


class LocationAdminInline(admin.TabularInline):
    model = Location
    extra = 0


class ClientAdmin(admin.ModelAdmin):
    search_fields = ['ruc', 'name']
    list_display = ('ruc', 'name', 'created_at')
    inlines = [LocationAdminInline]



class VisitItemAdminInline(admin.TabularInline):
    model = VisitItem
    extra = 0


class VisitAdmin(admin.ModelAdmin):
    list_display = ('check_in', 'user', 'location')
    inlines = [VisitItemAdminInline]


class SupervisedUserAdmin(admin.ModelAdmin):
    list_display = ('supervisor_str', 'supervised_user_str', 'created_at')
    search_fields = ['supervisor__first_name', 'supervised_user__first_name']
    filter = ['supervisor']


class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'unit_price', 'quantity_a', 'commission_a', 'quantity_b', 'commission_b', 'valid_from', 'valid_to')
    search_fields = ['product__name']
    filter = ['product']


class ScheduledVisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'check_in', 'user', 'location', 'get_status')
    search_fields = ['user__first_name', 'user__last_name', 'location__name']
    filter = ['user', 'location']
    ordering = ['check_in']


admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(SupervisedUser, SupervisedUserAdmin)
admin.site.register(Distributor)
admin.site.register(ProductPrice, ProductPriceAdmin)
admin.site.register(ScheduledVisit, ScheduledVisitAdmin)
admin.site.register(ClientCategory)
admin.site.register(Location)
admin.site.register(Attendance)
