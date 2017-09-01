"""
This is a Python application which runs on the IOTIFY. It monitors temperature and humidity values and publishes the readings to IBM IoT service.
"""
import threading
#Python Client for IBM Watson IoT Platform
import ibmiotf.application                                                 # MQTT

#This package provides a class to control the GPIO on a Raspberry Pi.
#import RPi.GPIO as GPIO                                                # External module imports                 

#The Twilio REST API lets to you initiate outgoing calls, list previous calls, and much more.
from twilio.rest import Client			                          # twilio module

# read temperature and humidity from SHT21 Sensirion sensor
#from sht21 import SHT21                                                  # User defined library

import time									  # Time module
import datetime                                                              # datetime module
import json                                                                    # JSON module
import logging 								   # logging module

LOG_FILENAME = 'HelloIoTBluemix.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')






def loadDataOf(fileName):
    try:
        logging.info("In loadDataOf")
        with open(fileName) as data_file:    
            loadedData = json.load(data_file)
            return loadedData
        
    except Exception as ex:
        logging.info("%s"%(type(ex)))
        logging.info("file %s not found"%fileName)
   
data = loadDataOf("bluemixCredentials.json")
threshold_data = loadDataOf("thresholds.json")
current_sensor_data = loadDataOf("currentSensorValues.json")


Twilio = data["Credentials"]["Twilio_Account"]                           # Twilio Credentials
Org = data["Credentials"]["Organization"]                                # Organization credentials as registered in IBM Bluemix

account_sid = Twilio["account_sid"]                                       # Your account sid
auth_token  = Twilio["auth_token"]                                       # Your auth token

twilioClient = Client(account_sid, auth_token)                         # Initialize twilioREST client 

twilionumber = Twilio["twilionumber"]                                    # Twilio phone Number got while registration
receivernumber = Twilio["receivernumber"]                              # Your verified phone number

#GPIO set as input that can be used to disable sensor readings
# (0 means readings enabled, 1 means readings disabled)
#SENSOR_DISABLE = 14

# GPIO set as output that signals when temperature is above a threshold value
# (0 means temperature below threshold, 1 means temperature above threshold)
#TEMP_ALARM = 24

'''****************************************************************************************
Function Name 	:	sensorLoop()
Description		:	Periodically reads temperature and humidity value from the
SHT21 sensor and sends them to IBM Bluemix; sends an alert message when
temperature reaches a critical value
Parameters 		:	-
****************************************************************************************'''
#currentCriticalLevelFlag = False
#criticalLevelChangeOverFlag = False
sensorReadingTime = 0
criticalLevelReachedTime = 0
#currentTemperature = 0
#currentHumidity = 0
notificationSentTime = 0
#count = 1
LOOP_SAMPLING_TIME = 2
#CRITICAL_TEMPERATURE = 40
NOTIFICATION_TIME_DELAY = 15

def thresholdReached(msg):

        #This means that in this measurement loop , the changeover has happend 
				#if criticalLevelChangeOverFlag == True:
	message = twilioClient.messages.create(body=msg,to=receivernumber,from_=twilionumber)

	notificationSentTime = datetime.datetime.now()
				

				# This means that in this measurement loop the level stays at the critical level
	  
def sensorLoop():
	try:
		global client,count,deviceType,LOOP_SAMPLING_TIME,NOTIFICATION_TIME_DELAY,CRITICAL_TEMPERATURE,currentCriticalLevelFlag,criticalLevelChangeOverFlag
		"""sht21 = SHT21(1)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(SENSOR_DISABLE, GPIO.IN)
		GPIO.setup(TEMP_ALARM, GPIO.OUT)
		GPIO.output(TEMP_ALARM,False)

		deviceId = "RASPBERRY_PI_001"
		deviceType = "raspberry_pi"
		messageBody = "Critical temperature reached"
		"""
                Devices = data["Credentials"]["Devices"].keys()
                for device in Devices:
                    messagebody = ""
                    currentCriticalLevelFlag = False
                    criticalLevelChangeOverFlag = False
                    logging.info("************* %s ******************"%device)
                    deviceId = data["Credentials"]["Devices"][device]["deviceId"]
                    deviceType = data["Credentials"]["Devices"][device]["deviceType"]
                    device_thresholds = threshold_data["Devices"][device]
                    CRITICAL_AIR_TEMPERATURE =  device_thresholds["air_temperature"]
                    CRITICAL_SOIL_TEMPERATURE = device_thresholds["soil_temperature"]
                    CRITICAL_HUMIDITY_PERCENTAGE = device_thresholds["humidity"]
                    CRITICAL_SOIL_MOISTURE_LEVEL = device_thresholds["soil_moisture"]
                    
                    count =1
            	    while count == 1:
                                logging.info("****In while for %s ****"%device)
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
				#	if currentCriticalLevelFlag == False:
				#		currentCriticalLevelFlag = True
				#		criticalLevelChangeOverFlag = True
						criticalLevelReachedTime = datetime.datetime.now()
                                                messageBody = "Critical temperature reached for %s at %s"%(device,criticalLevelReachedTime) 
                                                thresholdReached(messageBody)
					#else:
					#	criticalLevelChangeOverFlag = False

				
                                if currentSoilTemperature >= CRITICAL_SOIL_TEMPERATURE:
					#GPIO.output(TEMP_ALARM,True)
					#if currentCriticalLevelFlag == False:
					#	currentCriticalLevelFlag = True
					#	criticalLevelChangeOverFlag = True
					criticalLevelReachedTime = datetime.datetime.now()
                                        messageBody = "Critical soil temperature reached for %s at %s"%(device,criticalLevelReachedTime) 
                                        thresholdReached(messageBody)
					#else:
					#	criticalLevelChangeOverFlag = False

				
                                if currentHumidity >= CRITICAL_HUMIDITY_PERCENTAGE:
					#GPIO.output(TEMP_ALARM,True)
					#if currentCriticalLevelFlag == False:
					#	currentCriticalLevelFlag = True
					#	criticalLevelChangeOverFlag = True
					criticalLevelReachedTime = datetime.datetime.now()
                                        messageBody = "Critical humidity percentage reached for %s at %s"%(device,criticalLevelReachedTime) 
                                        thresholdReached(messageBody)
					#else:
					#	criticalLevelChangeOverFlag = False


				
                                if currentSoilMoisture <= CRITICAL_SOIL_MOISTURE_LEVEL:
					#GPIO.output(TEMP_ALARM,True)
					#if currentCriticalLevelFlag == False:
					#	currentCriticalLevelFlag = True
					#	criticalLevelChangeOverFlag = True
					criticalLevelReachedTime = datetime.datetime.now()
                                        messageBody = "Critical soil moisture level reached for  %s at %s, Please water the plants"%(device,criticalLevelReachedTime) 
                                        thresholdReached(messageBody)
					#else:
					#	criticalLevelChangeOverFlag = False

				count = count -1		
	#except KeyboardInterrupt: 
		#GPIO.cleanup()
                logging.info("=============================================================================================================")
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
	#sensorLoop()

