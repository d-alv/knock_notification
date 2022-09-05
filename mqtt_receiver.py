# start

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time



GPIO.setmode(GPIO.BCM)

gp1 = 0# put port
gp2 = 2# put port
gp3 = 3# put port
gp4 = 4# put port

# GPIO setups as outputs
GPIO.setup(gp1, GPIO.OUT)
GPIO.setup(gp2, GPIO.OUT)
GPIO.setup(gp3, GPIO.OUT)
GPIO.setup(gp4, GPIO.OUT)

# start program with pins low
GPIO.output(gp1, GPIO.LOW)
GPIO.output(gp2, GPIO.LOW)
GPIO.output(gp3, GPIO.LOW)
GPIO.output(gp4, GPIO.LOW)

pause = .002
step_total = 4096 # 4096 = 360 degrees
clock_wise = True

# documentation sequence for driver
sequence = [[1,0,0,1],
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1]]

pins = [gp1, gp2, gp3, gp4]
current_step = 0

file_name = 'notifications.txt'
notifications = 0


def on_connect(client, userdata, flags, rc):
    print("connected with result code "+str(rc))
    
    client.subscribe("message")
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    if msg.payload.decode("utf-8") == "notification":
        print("notifies")
        notifications += 1
        with open(file_name, 'w') as file_object:
            file_object.write(notifications)
        #knock()
            
    if msg.payload.decode("utf-8") == "call":
        print("rings")
        
    if msg.payload.decode("utf-8") == "clear":
        print("clears")
        with open(file_name, 'w') as file_object:
            file_object.write('')
        
def knock():
    # 4096 steps is 360 degrees
    for x in range(step_total):
        for gp in range(0, len(pins)):
            GPIO.output(pins[gp], sequence[current_step][gp])
        if clock_wise:
            current_step = (current_step +1) % 8 # only 8 sequences
        else:
            current_step = (current_step - 1) % 8
            
def ring():
    """this is the function for when I receive a phone call"""
    
    
        


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.86.33", 1883, 60)

client.loop_forever()
GPIO.cleanup()