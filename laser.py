import time
from gpiozero import LightSensor
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import json

ldr = LightSensor(4)

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    laser()

host = "a34vyzz000vojq.iot.us-east-1.amazonaws.com"
rootCAPath = "root-CA.crt"
certificatePath = "Lap_Timing_Final_Pi.cert.pem"
privateKeyPath = "Lap_Timing_Final_Pi.private.key"
useWebsocket = False
clientId = "client-1"
subscribedTopic = "startTimingTopic"
publishedTopic = "endTimingTopic"

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(100)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(100)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
#if args.mode == 'both' or args.mode == 'subscribe':
myAWSIoTMQTTClient.subscribe(subscribedTopic, 1, customCallback)
time.sleep(2)

def laser():
    timer = time.time()
    current_lap = 1
    lap_time = 0
    previous_final_time = 0
    final_time = 0
    while True:
        laser = get_laser_value()
        print(laser)
        if laser < 0.75:
            final_time = time.time() - timer
            lap_time = final_time - previous_final_time
            print(lap_time, 's')
            if lap_time > 2:
                previous_final_time = final_time
                send_to_cloud(final_time, current_lap, lap_time)
                current_lap = current_lap + 1
                
        

def get_laser_value():
    return ldr.value


def send_to_cloud(final_time, current_lap, lap_time):
    # figure out how to send to cloud
    print(final_time, "s")
    #laser = get_laser_value()
    #print(laser)
    
    message = {}
    message['Current Lap'] = current_lap
    message['Lap Time'] = round(lap_time, 2)
    message['Overall Time'] = round(final_time, 2)
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish(publishedTopic, messageJson, 1)
    
    return final_time

def test():
    timer = time.time()
    x = 0
    while (time.time() - timer) < 5:
        x = get_laser_value()
        print(x)
    return











