"""
This is a Python application which runs on the IOTIFY. It monitors temperature and humidity values and publishes the readings to IBM IoT service.
"""
import threading
#Python Client for IBM Watson IoT Platform
import ibmiotf.application                                                 # MQTT

#This package provides a class to control the GPIO on a Raspberry Pi.
import RPi.GPIO as GPIO                                                # External module imports                 

#The Twilio REST API lets to you initiate outgoing calls, list previous calls, and much more.
from twilio.rest import Client			                          # twilio module

# read temperature and humidity from SHT21 Sensirion sensor
from sht21 import SHT21                                                  # User defined library

import time									  # Time module
import datetime                                                              # datetime module
import json                                                                    # JSON module
import logging 								   # logging module

LOG_FILENAME = 'HelloIoTBluemix.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

try:
    with open("bluemixCredentials.json") as data_file:    
        data = json.load(data_file)
        
except Exception as ex:
    logging.info("%s"%(type(ex)))
    logging.info("Credentials file not found")

try :
     with open("thresholds.json") as data1_file:    
        threshold_data = json.load(data1_file)
        
except Exception as ex:
    logging.info("%s"%(type(ex)))
    logging.info("thresholds file not found") 

try :
     with open("currentSensorValues.json") as data2_file:    
        current_sensor_data = json.load(data2_file)
        
except Exception as ex:
    logging.info("%s"%(type(ex)))
    logging.info("currentSensorValues  file not found") 


Twilio = data["Credentials"]["Twilio_Account"]                           # Twilio Credentials
Org = data["Credentials"]["Organization"]                                # Organization credentials as registered in IBM Bluemix

account_sid = Twilio["account_sid"]                                       # Your account sid
auth_token  = Twilio["auth_token"]                                       # Your auth token

twilioClient = Client(account_sid, auth_token)                         # Initialize twilioREST client 

twilionumber = Twilio["twilionumber"]                                    # Twilio phone Number got while registration
receivernumber = Twilio["receivernumber"]                              # Your verified phone number

#GPIO set as input that can be used to disable sensor readings
# (0 means readings enabled, 1 means readings disabled)
SENSOR_DISABLE = 14

# GPIO set as output that signals when temperature is above a threshold value
# (0 means temperature below threshold, 1 means temperature above threshold)
TEMP_ALARM = 24

'''****************************************************************************************
Function Name 	:	sensorLoop()
Description		:	Periodically reads temperature and humidity value from the
SHT21 sensor and sends them to IBM Bluemix; sends an alert message when
temperature reaches a critical value
Parameters 		:	-
****************************************************************************************'''
currentCriticalLevelFlag = False
criticalLevelChangeOverFlag = False
sensorReadingTime = 0
criticalLevelReachedTime = 0
currentTemperature = 0
currentHumidity = 0
notificationSentTime = 0

LOOP_SAMPLING_TIME = 2
#CRITICAL_TEMPERATURE = 40
NOTIFICATION_TIME_DELAY = 15


def sensorLoop():
	try:
		global client,deviceType,LOOP_SAMPLING_TIME,NOTIFICATION_TIME_DELAY,CRITICAL_TEMPERATURE,currentCriticalLevelFlag,criticalLevelChangeOverFlag
		"""sht21 = SHT21(1)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(SENSOR_DISABLE, GPIO.IN)
		GPIO.setup(TEMP_ALARM, GPIO.OUT)
		GPIO.output(TEMP_ALARM,False)

		deviceId = "RASPBERRY_PI_001"
		deviceType = "raspberry_pi"
		messageBody = "Critical temperature reached"
		"""
                count =1
                Devices = data["Credentials"]["Devices"].keys()
                for device in Devices:
                    deviceId = data["Credentials"]["Devices"][device]["deviceId"]
                    deviceType = data["Credentials"]["Devices"][device]["deviceType"]
                    device_thresholds = threshold_data["Devices"][device]
                    CRITICAL_AIR_TEMPERATURE =  device_thresholds["air_temperature"]
                    CRITICAL_SOIL_TEMPERATURE = device_thresholds["soil_temperature"]
                    CRITICAL_HUMIDITY_PERCENTAGE = device_thresholds["humidity"]
                    CRITICAL_SOIL_MOISTURE_LEVEL = device_thresholds["soil_moisture"]
                    messageBody = "Critical temperature reached for " + device
                    
            	    while count == 1 :

			#if GPIO.input(SENSOR_DISABLE) == 0:
				time.sleep(LOOP_SAMPLING_TIME)		
				"""currentTemperature = sht21.read_temperature()
				currentHumidity = sht21.read_humidity()"""
                                current = current_sensor_data["Devices"][device]
                                currentAirTemperature  = current["air_temperature"]
                                currentSoilTemperature = current["soil_temperature"]
                                currentHumidity = current["humidity"]    
                                currentSoilMoisture = current["soil_moisture"]
				sensorReadingTime = datetime.datetime.now()

				message = {"ID":1,"Air_temperature": currentAirTemperature, "humidity":currentHumidity, "soil_moisture":currentSoilMoisture , "soil_temperature":currentSoilTemperature , "Description" : "Values from " + device}
				
				try:
					# publish the message to IBM Bluemix
					pubReturn = client.publishEvent(deviceType, deviceId, "status", "json", message)
					if pubReturn == True:
						logging.info("The message successfully sent")
				except Exception  as e:
						logging.info("The sent message Failed")
						logging.error("The publishEvent exception httpcode :%s,message:%s,response:%s"(e.httpcode,e.message,e.response))
				

				if currentAirTemperature >= CRITICAL_AIR_TEMPERATURE:
					#GPIO.output(TEMP_ALARM,True)
					if currentCriticalLevelFlag == False:
						currentCriticalLevelFlag = True
						criticalLevelChangeOverFlag = True
						criticalLevelReachedTime = datetime.datetime.now()
					else:
						criticalLevelChangeOverFlag = False

				else:
					#GPIO.output(TEMP_ALARM,False)
					currentCriticalLevelFlag = False
					criticalLevelChangeOverFlag = False


				#This means that in this measurement loop , the changeover has happend 
				if criticalLevelChangeOverFlag == True:
					message = twilioClient.messages.create(body=messageBody,to=receivernumber,from_=twilionumber)

					notificationSentTime = datetime.datetime.now()
				

				# This means that in this measurement loop the level stays at the critical level
				
				elif (currentCriticalLevelFlag == True):
					#calculate timedifference
					diff = sensorReadingTime - notificationSentTime
	
					day  = diff.days
					hour = (day*24 + diff.seconds/3600)
					diff_minutes = (diff.days *24*60)+(diff.seconds/60)			

					if diff_minutes > NOTIFICATION_TIME_DELAY:
						message = twilioClient.messages.create(body=messageBody,to=receivernumber,from_=twilionumber)
						
						notificationSentTime = datetime.datetime.now()
			
                                count = count -1						
	#except KeyboardInterrupt: 
		#GPIO.cleanup()
	except Exception as e:
		logging.error("Exception is %s,%s"%(e,type(e)))

	

'''****************************************************************************************
Function Name 	:	init()
Description		:	Function which connects to the ibmiotf service
Parameters 		:	-
****************************************************************************************'''

def init():
	global client,deviceType
	
	organization =  Org["Organization_ID"]                                            #Your organization ID as registered in IBM Bluemix
	authKey =  Org["authKey"]                                                           #API key (required if auth-method is apikey).(These you will when you generate the api keys)
	authToken =  Org["authToken"]                                                      #API key token (required if auth-method is apikey).(These you will when you generate the api keys)
	
        Devices = data["Credentials"]["Devices"].keys()
        logging.info("Devices : %s"%Devices)
        for device in Devices:

        	appId = device                                                                  # The IBM Bluemix device you've created
	        authMethod = "apikey"                                                       #Method of authentication (the only value currently supported is apikey)
	        try:
		     options = {"org": organization, "id":appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}       # options require for the connection
		     client = ibmiotf.application.Client(options)
		     client.connect()
                     logging.info("IOTFconnection established for %s"%appId)
	        except ibmiotf.connectionException as e:
		     logging.error("The iotfconnection Exception is %s,%s"%(e,type(e)))	


if __name__ == '__main__':
	init()                                                                                     #Connection establishment with IBM bluemix
        threading.Thread(target=sensorLoop()).start()
	
