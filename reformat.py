import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

gp1 = 4# put port
gp2 = 27# put port
gp3 = 22# put port
gp4 = 23# put port

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
# 4096 = 360 degrees

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

file_name = '/home/pi/knock_notif/notifications.txt'


class MainClass():

    def __init__(self):
        # definitions for retrying failed connection
        self.run_flag = True
        self.tot_wait=30
        self.retry=0
        self.retry_delay_fixed=2 #retry delay (seconds)
        self.connected_once=False
        self.count=0
        self.stime = time.time() # start time
        self.retry_wait = self.retry_delay_fixed
        self.elapsed_time = 0
        self.notifications=0
        self.step_total = 0# 239
        self.right_dirr = 390 # or 383, not sure yet
        self.left_dirr = 570 # steps needed for 48.6 degree turn left

        ################################
        #client info

        self.client = mqtt.Client()
        
        self.call_flag = False # flag for receiving call
        
    def keep_running(self):
        #prepare run variables/methods
        retry=0
        self.client.on_connect = self.on_connects
        self.client.on_message = self.on_messages
        self.client.connect("192.168.86.44", 1883, 60)
        with open(file_name) as file_object: 
            data = file_object.read()
            if data=='':
                pass
            else:

                cdata = data.rstrip()
                notifs = int(cdata) #should produce number of notifications
                if notifs>0:
                    self.knock(direction=False, knock_num=notifs)
                                    
                        
        
        while self.run_flag: #when the program runs / 
            self.check_time()
            #print(self.elapsed_time)
            self.client.loop(.1)
            rdelay = time.time() - self.stime
            if self.connect_flag:
                if self.call_flag==True:
                    self.ring()
                    
                
                if self.elapsed_time>=900: # resets program every 15 minutes to display missed messages.

                    self.set_start()
                    self.client.loop_stop()
                    self.client.connect("192.168.86.44", 1883, 60)
                    self.keep_running()
                # any looped command here 
                
            
                
            # if the connection fails, this stuff runs
            if not self.connect_flag and rdelay>self.retry_wait:
                retry_wait = self.retry_wait
                retry_delay_fixed = self.retry_delay_fixed
                        
                try:
                    retry+=1
                    client.connect("192.168.86.33",1883,60) # attempt to reconnect to server again

                    while not self.connect_flag:
                        self.client.loop(.01)
                        time.sleep(1)
                        self.stime = time.time()
                        retry_wait=retry_delay_fixed
                    connected_once=True
                    retry=0 #resets it
                except Exception as e:
                    print("\nConnect failed: ",e)
                    retry_wait=retry_wait**2
                    if retry_wait>100:
                        retry_wait=100
                    print("try delay =", retry_wait)
                    if retry>retry_limit and retry_limit !=0:
                        sys.exit(1)
                        # at this point give up on connection, something may be wrong with WIFI


    def on_connects(self, client, userdata, flags, rc):
        if rc==0:
            self.connect_flag=True #this shows it was success
        else:
            self.connect_flag=False
            sys.exit(1)
        print("connected with result code "+str(rc))

        client.subscribe([("unimportant",1),("important",2)])

    def on_messages(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

        if msg.payload.decode("utf-8") == "notify":
            #print("notifies")
            self.notifications += 1
            with open(file_name, 'w') as file_object:
                file_object.write(str(self.notifications))
            self.knock(direction=True, knock_num=2)
            
            
        if msg.payload.decode("utf-8") == "important":
            print("important message received")
            self.notifications +=1
            with open(file_name, 'w') as file_object:
                file_object.write(str(self.notifications))
            self.knock(direction=True, knock_num=4)
                        

        if msg.payload.decode("utf-8") == "calls":
           # print("rings")
            self.set_start()
            self.call_flag = True
            self.ring()
            #code for this changes
            # rings for 30 seconds if not answered

        if msg.payload.decode("utf-8") == "clearings":
           # print("clears")
            self.notifications=0
            with open(file_name, 'w') as file_object:
                file_object.write('')
                
                
        if msg.payload.decode("utf-8") == "answering":
            # this works for when the phone is answered
            # prompts the robot to stop "notification"
           # print("call answered")
            self.call_flag=False
            
        

    def knock(self, direction=True, knock_num=1):
        # if direction == True, that means it hits right side
        """this is the code to make the robot
           tap the desk, of course this is only
           for one rotation though, if another knock is wanted,
           then the code must be altered, the ring() function could work
           in a manner so that it repeats it several times"""
        # 4096 steps is 360 degrees
        time.sleep(.5)
        current_step=0
        if direction == True:
            self.step_total = self.right_dirr
            
        else:
            self.step_total = self.left_dirr
        total = self.step_total*2
        if knock_num ==1:
            
            
            for x in range(0, total):
                if x == self.step_total:
                    if direction == True:
                        direction = False
                    elif direction == False:
                        direction = True
                for gp in range(0, len(pins)):
                    GPIO.output(pins[gp], sequence[current_step][gp])
                if direction == True:
                    current_step = (current_step +1) % 8 # only 8 sequences
                else:
                    current_step = (current_step - 1) % 8
                time.sleep(.0009)
        
        
                
        if knock_num > 1:
            
            for x in range(0, self.step_total): #handles going down
                for gp in range(0, len(pins)):
                    GPIO.output(pins[gp], sequence[current_step][gp])
                if direction == True:
                    current_step = (current_step +1) % 8 # only 8 sequences
                else:
                    current_step = (current_step - 1) % 8
                time.sleep(.0009)
            # here switches direction
            if direction == True:
                direction = False
            elif direction == False:
                direction = True
                
            for x in range(0, knock_num-1):
                
                
                for x in range(0, int(self.step_total/2)): #handles going up
                    for gp in range(0, len(pins)):
                        GPIO.output(pins[gp], sequence[current_step][gp])
                    if direction == True:
                        current_step = (current_step +1) % 8 # only 8 sequences
                    else:
                        current_step = (current_step - 1) % 8
                    time.sleep(.0009)
                if direction == True:
                    direction = False
                elif direction == False:
                    direction = True
                for x in range(0, int(self.step_total/2)): #handles going down once more
                    for gp in range(0, len(pins)):
                        GPIO.output(pins[gp], sequence[current_step][gp])
                    if direction == True:
                        current_step = (current_step +1) % 8 # only 8 sequences
                    else:
                        current_step = (current_step - 1) % 8
                    time.sleep(.0009)
                
                if direction == True:
                    direction = False
                elif direction == False:
                    direction = True  
                
            for x in range(0, self.step_total): #handles going up final time
                for gp in range(0, len(pins)):
                    GPIO.output(pins[gp], sequence[current_step][gp])
                if direction == True:
                    current_step = (current_step +1) % 8 # only 8 sequences
                else:
                    current_step = (current_step - 1) % 8
                time.sleep(.0009)          
            

    def ring(self):
        """this is the function for when I receive a phone call"""
        
        if self.call_flag == True:
            # repeat for a certain time before checking
            # if the phone is still ringing
            # therefore I don't need to use a while loop
            for n in range(0, 1):
                # make this hit the left side each time.
                self.knock(direction=True)
                self.check_time()
                if self.elapsed_time >= self.tot_wait:
                    self.call_flag = False
            
            
            
                # find way for it to be responsive to input by phone
                # probably add some sort of wait
                # so that motor isn't overrun with values
                
    def check_time(self):
        """method for constantly checking time -
           specifically useful for phone ringing and
           no answer - don't need RTC module since WIFI"""
        self.elapsed_time = time.time() - self.stime
        
        
    def set_start(self):
        """method sets timer to zero for phone call"""
        self.stime = time.time()
        




#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_message = on_message



if __name__ == '__main__':
    mc = MainClass()
    mc.keep_running()
