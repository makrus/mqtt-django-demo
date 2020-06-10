# from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from json_views.views import JSONListView, PaginatedJSONListView
from transit.models import BooleanChannelData, DigitalChannelData, Channel
from datetime import datetime as dt
from django.utils import timezone


class ChannelListJSON(JSONListView):
    model = Channel


class ChannelDataListJSON(PaginatedJSONListView):
    paginate_by = 1440
    count_query = 'count'
    count_only  = False

    def get_queryset(self):
        channel_name = self.kwargs['location'] + '/' + self.kwargs['device'] + '/' + self.kwargs['sensor']
        channel = Channel.objects.get(name=channel_name)
        if channel.data_type == 'd':
            return DigitalChannelData.objects.filter(name=channel_name).order_by('-time_sent')
        else:
            return BooleanChannelData.objects.filter(name=channel_name).order_by('-time_sent')


class ChannelDataLatestJSON(JSONListView):
    def get_queryset(self):
        channel_name = self.kwargs['location'] + '/' + self.kwargs['device'] + '/' + self.kwargs['sensor']
        channel = Channel.objects.get(name=channel_name)
        if channel.data_type == 'd':
            return DigitalChannelData.objects.filter(name=channel_name).order_by('-time_sent').latest('time_sent')
        else:
            return BooleanChannelData.objects.filter(name=channel_name).order_by('-time_sent').latest('time_sent')


class SetChannelData(View):
    def get(self, request, *args, **kwargs):
        channel_name = self.kwargs['location'] + '/' + self.kwargs['device'] + '/' + self.kwargs['sensor']
        if Channel.objects.get(name = channel_name).type:
            record = BooleanChannelData(
                name = channel_name,
                time_sent = dt.now(tz=timezone.get_current_timezone()),
                time_recieved = dt.now(tz=timezone.get_current_timezone()),
                value = True if self.kwargs['state']=='on' else False
            )
            try:
                record.save()
            except Exception as e:
                return HttpResponse(e.msg)
            else:
                return HttpResponse('ok')
        return HttpResponse('read-only channel')
