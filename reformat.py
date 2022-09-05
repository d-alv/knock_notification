# Write your code here :-)
# start

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time


GPIO.setwarnings(False)
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




file_name = 'notifications.txt'


class MainClass():
    
    def __init__(self):
        
        # GPIO stuff
        self.step_total=239
        self.current_step=0
        self.pause=.002
        self.clock_wise=True
        self.sequence = [[1,0,0,1],
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1]]
        self.pins=[gp1, gp2, gp3, gp4]
        # definitions for retrying failed connection
        self.run_flag = True
        self.stime= time.time()
        self.notifications=0
        
        ################################
        #client info
        
        self.client = mqtt.Client()
        
        
        
    def keep_running(self):
        #prepare run variables/methods
        
        self.client.connect("192.168.86.33", 1883, 60)
        self.client.on_connect = self.on_connects
        self.client.on_message = self.on_messages
        
        while self.run_flag:
            self.client.loop(.01)
            self.client.on_message
            
            
            #if self.client.connected_flag:
                # main loop stuff here
                
        
        

    def on_connects(self, client, userdata, flags, rc):
        
        print("connected with result code "+str(rc))
    
        client.subscribe("message")
    
    def on_messages(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
    
        if msg.payload.decode("utf-8") == "notification":
            print("notifies")
            self.notifications += 1
            with open(file_name, 'w') as file_object:
                file_object.write(str(self.notifications))
            #knock()
            
        if msg.payload.decode("utf-8") == "call":
            print("rings")
        
        if msg.payload.decode("utf-8") == "clear":
            print("clears")
            self.notifications=0
            with open(file_name, 'w') as file_object:
                file_object.write('')
        
    def knock():
        # 4096 steps is 360 degrees - only need 239
        for x in range(0,self.step_total*2):
            for gp in range(0, len(self.pins)):
                GPIO.output(self.pins[gp], self.sequence[self.current_step][gp])
            if self.clock_wise:
                self.current_step = (current_step +1) % 8 # only 8 sequences
            else:
                self.current_step = (current_step - 1) % 8
            if x ==self.step_total:
                self.clock_wise=False
            
    def ring():
        """this is the function for when I receive a phone call"""
     
    
        


#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_message = on_message



if __name__ == '__main__':
    mc = MainClass()
    mc.keep_running()