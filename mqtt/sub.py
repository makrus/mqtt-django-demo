import paho.mqtt.client as mqtt
import os, django
from django.conf import settings
from django.utils import timezone
from datetime import datetime as dt


os.environ["DJANGO_SETTINGS_MODULE"] = 'project.settings'
django.setup()
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
    client.subscribe([
        ('house/device1/temperature',2),
        ('house/device1/humidity',2),
        ('house/device1/statusled',2),
        ('house/device0/temperature',2),
        ('house/device0/humidity',2),
        ('house/device0/statusled',2),
        ('school/channel10',2)
    ])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = str(msg.payload).rstrip("'").lstrip("b'").split(',')
    # print(msg.topic," ",data)
    if ('temperature' in msg.topic) or ('humidity' in msg.topic):
        record = DigitalChannelData(
            name=msg.topic,
            time_sent=dt.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z"),
            time_recieved=dt.now(tz=timezone.get_current_timezone()),
            value=float(data[1])
        )
    elif 'statusled' in msg.topic:
        record = BooleanChannelData(
            name = msg.topic,
            time_sent = dt.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z"),
            time_recieved = dt.now(tz=timezone.get_current_timezone()),
            value = True if data[1]=='on' else False
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