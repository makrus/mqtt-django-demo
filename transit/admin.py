from django.contrib import admin
from .models import DigitalChannelData, BooleanChannelData, Channel


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'data_type',)
    list_filter = ('type', 'data_type',)


class BooleanChannelDataAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'time_sent', 'time_recieved', 'value',)


class DigitalChannelDataAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'time_sent', 'time_recieved', 'value',)


admin.site.register(BooleanChannelData, BooleanChannelDataAdmin)
admin.site.register(DigitalChannelData, DigitalChannelDataAdmin)
admin.site.register(Channel, ChannelAdmin)
