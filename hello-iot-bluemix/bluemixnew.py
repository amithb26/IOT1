"""
This is a Python application which runs on the IOTIFY. It monitors temperature and humidity values and publishes the readings to IBM IoT service.
"""
import threading
#Python Client for IBM Watson IoT Platform
import ibmiotf.application                                                    # MQTT

#The Twilio REST API lets to you initiate outgoing calls, list previous calls, and much more.
from twilio.rest import Client			                       # twilio module

import time								      # Time module
import datetime                                                               # datetime module
import json                                                                     # JSON module
import logging 								    # logging module

LOG_FILENAME = 'HelloIoTBluemix.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

'''****************************************************************************************
Function Name 	        :	loadDataOf()
Description		:	Loads Data from JSON File
Parameters 		:	Filename - json format
****************************************************************************************'''

def loadDataOf(fileName):
    try:
        with open(fileName) as data_file:    
            return json.load(data_file)
        
    except Exception as ex:
        logging.info("%s"%(type(ex)))
        logging.info("file %s not found"%fileName)
   

data = loadDataOf("bluemixCredentials.json")
threshold_data = loadDataOf("thresholds.json")
current_sensor_data = loadDataOf("currentSensorValues.json")

Twilio = data["Credentials"]["Twilio_Account"]                         # Twilio Credentials
Org = data["Credentials"]["Organization"]                                # Organization credentials as registered in IBM Bluemix

account_sid = Twilio["account_sid"]                                       # Your account sid
auth_token  = Twilio["auth_token"]                                       # Your auth token

twilioClient = Client(account_sid, auth_token)                       # Initialize twilioREST client 

twilionumber = Twilio["twilionumber"]                                    # Twilio phone Number got while registration
receivernumber = Twilio["receivernumber"]                              # Your verified phone number

sensorReadingTime = 0
criticalLevelReachedTime = 0
notificationSentTime = 0
LOOP_SAMPLING_TIME = 2
NOTIFICATION_TIME_DELAY = 15

'''****************************************************************************************
Function Name 	        :	thresholdReached()
Description		:	Sends notification(via twilio SMS service) to user whenever read sensor values are more than the critical value set
Parameters 		:       msg - Message displaying which parameter reached its value above or equal to threshold 
****************************************************************************************'''

def thresholdReached(msg):
    message = twilioClient.messages.create(body=msg,to=receivernumber,from_=twilionumber)
    notificationSentTime = datetime.datetime.now()
				

'''****************************************************************************************
Function Name 	        :	publishMsg()
Description		:	Publish message to IBM Bluemix(Push alerts to IBM Bluemix)
Parameters 		:	deviceType - device type as registered in IBM Bluemix  
                                        deviceID    - ID of device as registered in IBM Bluemix
                                        message     - Data to be published to bluemix
****************************************************************************************'''

def publishMsg(deviceType, deviceId, device,message):
    global client
    try:
        # publish the message to IBM Bluemix
	pubReturn = client.publishEvent(deviceType, deviceId, "status", "json", message)
	if pubReturn == True:
	    logging.info("The message successfully sent from %s"%device)
    except Exception  as e:
            logging.info("The sent message Failed")
            logging.error(e)
	    logging.error("The publishEvent exception httpcode :%s,message:%s,response:%s"(e.httpcode,e.message,e.response))

'''****************************************************************************************
Function Name 	        :	sensorLoop()
Description		:	Periodically reads temperature,humidity,soilmoisture value from the sends an alert message when parameters reaches a critical value
Parameters 		:	-
****************************************************************************************'''

def sensorLoop():
   # try:
        global client,LOOP_SAMPLING_TIME,NOTIFICATION_TIME_DELAY
        Devices = data["Credentials"]["Devices"].keys()
        for device in Devices:
            messageBody = ""
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
		time.sleep(LOOP_SAMPLING_TIME)		
		current = current_sensor_data["Devices"][device]
                currentAirTemperature  = current["air_temperature"]
                currentSoilTemperature = current["soil_temperature"]
                currentHumidity = current["humidity"]    
                currentSoilMoisture = current["soil_moisture"]
		sensorReadingTime = datetime.datetime.now()
		message = {"ID":1,"Air_temperature": currentAirTemperature, "humidity":currentHumidity, "soil_moisture":currentSoilMoisture , "soil_temperature":currentSoilTemperature , "Description" : "Values from " + device}
        	publishMsg(deviceType,deviceId,device,message)
				
                if currentAirTemperature >= CRITICAL_AIR_TEMPERATURE:
		    criticalLevelReachedTime = datetime.datetime.now()
                    messageBody = "Critical temperature reached for %s at %s"%(device,criticalLevelReachedTime) 
                    message = {"Alert" : messageBody} 
                    thresholdReached(messageBody)
                    publishMsg(deviceType,deviceId,device,message)

                if currentSoilTemperature >= CRITICAL_SOIL_TEMPERATURE:
	       	    criticalLevelReachedTime = datetime.datetime.now()
                    messageBody = "Critical soil temperature reached for %s at %s"%(device,criticalLevelReachedTime) 
                    message = {"Alert" : messageBody} 
                    thresholdReached(messageBody)
                    publishMsg(deviceType,deviceId,device,message)

				
                if currentHumidity >= CRITICAL_HUMIDITY_PERCENTAGE:
		    criticalLevelReachedTime = datetime.datetime.now()
                    messageBody = "Critical humidity percentage reached for %s at %s"%(device,criticalLevelReachedTime) 
                    message = {"Alert" : messageBody} 
                    thresholdReached(messageBody)
                    publishMsg(deviceType,deviceId,device,message)

                if currentSoilMoisture <= CRITICAL_SOIL_MOISTURE_LEVEL:
		    criticalLevelReachedTime = datetime.datetime.now()
                    messageBody = "Critical soil moisture level reached for  %s at %s, Please water the plants"%(device,criticalLevelReachedTime)
                    message = {"Alert" : messageBody} 
                    thresholdReached(messageBody)
                    publishMsg(deviceType,deviceId,device,message)
     	        count = count -1		
    #except Exception as e:
      #  logging.info("This Exception")
	#logging.error("Exception is %s,%s"%(e,type(e)))

'''****************************************************************************************
Function Name    	:	init()
Description		:	Function which connects to the ibmiotf service
Parameters 		:	-
****************************************************************************************'''

def init():
    global client
    organization =  Org["Organization_ID"]                                            #Your organization ID as registered in IBM Bluemix
    authKey =  Org["authKey"]                                                            #API key (required if auth-method is apikey).(These you will when you generate the api keys)
    authToken =  Org["authToken"]                                                      #API key token (required if auth-method is apikey).(These you will when you generate the api keys)
    Devices = data["Credentials"]["Devices"].keys()
    logging.info("Devices : %s"%Devices)
    for device in Devices:
        appId = device                                                                         # The IBM Bluemix device you've created
	authMethod = "apikey"                                                             #Method of authentication (the only value currently supported is apikey)
	try:
	    options = {"org": organization, "id":appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}       # options require for the connection
	    client = ibmiotf.application.Client(options)
	    client.connect()
            logging.info("IOTFconnection established for %s"%appId)
	except ibmiotf.connectionException as e:
	    logging.error("The iotfconnection Exception is %s,%s"%(e,type(e)))	


if __name__ == '__main__':
	init()                                                                                         #Connection establishment with IBM bluemix
        threading.Thread(target=sensorLoop()).start()
