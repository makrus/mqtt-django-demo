from django.db import models
import paho.mqtt.publish as publish
from django.conf import settings
# from datetime import datetime as dt


class Channel(models.Model):
    name = models.CharField('канал', max_length=256, primary_key=True)
    type =  models.BooleanField('управляющий', default=False)
    data_type = models.CharField('тип данных', max_length=1, choices=[('d', 'числовые'), ('b', 'логические')])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'канал'
        verbose_name_plural = 'каналы'


class ChannelData(models.Model):
    name = models.CharField('канал', max_length=256)
    time_sent = models.DateTimeField('отправлено')
    time_recieved = models.DateTimeField('получено')

    class Meta:
        abstract = True
        get_latest_by = 'time_sent'
        ordering  = ['time_sent']


class DigitalChannelData(ChannelData):
    value = models.FloatField('значение')

    class Meta:
        verbose_name = 'числовые данные'
        verbose_name_plural = 'числовые данные'


class BooleanChannelData(ChannelData):
    value = models.BooleanField('значение')

    def save(self, *args, **kwargs):
        # self.time_sent = dt.now()
        # self.time_recieved = dt.now()
        super().save(*args, **kwargs)  # Call the "real" save() method.
        if self.name[-4:] == '/led':
            payload = 'on' if self.value else 'off'
            publish.single(self.name, payload, qos=2, auth = {'username':settings.MQTT['USER'], 'password':settings.MQTT['PASSWORD']})

    class Meta:
        verbose_name = 'логические данные'
        verbose_name_plural = 'логические данные'
