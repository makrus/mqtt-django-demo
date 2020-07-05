import paho.mqtt.client as mqtt
import os, django
from django.utils import timezone
from datetime import datetime as dt


os.environ["DJANGO_SETTINGS_MODULE"] = 'project.settings'
django.setup()
from django.conf import settings
from transit.models import *


# логирование, опционально
def on_log(client, userdata, level, buf):
    # print("log: ",buf)
    pass

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    channel_list = [(c.name, 2) for c in Channel.objects.all()]
    client.subscribe(channel_list)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = str(msg.payload).rstrip("'").lstrip("b'").split(',')
    # print(msg.topic," ",data)
    # print('timestamp', msg.timestamp)
    # print('state', msg.state)
    # print('properties', msg.properties)
    # print('info', msg.info)
    # print('payload', msg.payload)
    if Channel.objects.get(name = msg.topic).type:
        record = BooleanChannelData(
            name = msg.topic,
            time_sent = dt.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z"),
            time_recieved = dt.now(tz=timezone.get_current_timezone()),
            value = True if data[1]=='on' else False
        )
    else:
        record = DigitalChannelData(
            name=msg.topic,
            time_sent=dt.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z"),
            time_recieved=dt.now(tz=timezone.get_current_timezone()),
            value=float(data[1])
        )
    record.save()
    # print(dt.now())
    #  dt.strptime('2020-06-06T13:55:32-0000', "%Y-%m-%dT%H:%M:%S%z")

client = mqtt.Client()
client.on_log=on_log
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(settings.MQTT['USER'], settings.MQTT['PASSWORD'])
client.connect(settings.MQTT['SERVER'])

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
