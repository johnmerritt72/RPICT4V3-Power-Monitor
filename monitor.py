import math
import serial
import numpy as np 
from datetime import datetime
from datetime import timedelta
from colorama import Fore, Back, Style
import time
import requests
from twilio.rest import Client
import MySQLdb

account_sid = "-- ENTER SID HERE --"
auth_token  = "-- ENTER TOKEN HERE -- "
client = Client(account_sid, auth_token)
testMode = False
config = {
    'user': '********',
    'password': '********',
    'host': '*******',
    'database': 'dbpower',
    'port': 3306
}
conn = MySQLdb.connect(**config)
cursor = conn.cursor()

def seconds_between(d1, d2):
    return abs((d2 - d1).total_seconds())

def sendTextAlert(message, testMode):
     if testMode == False:
          message = client.messages.create(to="********", from_="********", body=message)
          message2 = client.messages.create(to="********", from_="********", body=message)

def sendAlexaNotification():
     url = "https://api.virtualbuttons.com/v1"
     payload = "{\r\n    \"virtualButton\": 1,\r\n    \"accessCode\": \"********\"\r\n}"
     headers = {
          'Content-Type': 'text/plain'
     }
     response = requests.request("POST", url, headers=headers, data=payload)

def logToFile(logfile, msg):
     f = open(logfile, "a")
     f.write(datetime.now().strftime("%x %X") + ": " + msg + "\n")
     f.close()
     
def updateMonitor():
     cursor.execute("UPDATE MonitorStatus SET DateUpdated=%s WHERE id = 1;",(datetime.now(),))
     conn.commit() 
     
def updateDBDeviceTime():
     cursor.execute("""UPDATE PowerStatus
               SET UpdateTime=%s;""", 
               (datetime.now(),))
     conn.commit()

def updateDBPower(deviceId, curPowerUsage, avgpowerUsage):
     cursor.execute("""UPDATE PowerStatus
               SET CurrentPowerUsage = %s,
               AveragePowerUsage = %s, UpdateTime=%s
               WHERE id = %s;""", 
               (curPowerUsage, avgpowerUsage, datetime.now(), deviceId))
     conn.commit()

def updateDBPowerOn(deviceId, curPowerUsage, avgpowerUsage, TimeOn):
     cursor.execute("""UPDATE PowerStatus 
               SET DeviceOn = 1, CurrentPowerUsage = %s, 
               AveragePowerUsage = %s, LastOnTime = %s, UpdateTime=%s
               WHERE id = %s;""",
               (curPowerUsage, avgpowerUsage, TimeOn, TimeOn, deviceId))
     conn.commit()
          
def updateDBPowerOff(deviceId, curPowerUsage, avgpowerUsage, TimeOff):
     cursor.execute("""UPDATE dbpower.PowerStatus 
               SET DeviceOn = 0, CurrentPowerUsage = %s, 
               AveragePowerUsage = %s, LastOffTime = %s, UpdateTime=%s
               WHERE id = %s;""",
               (curPowerUsage, avgpowerUsage, TimeOff, TimeOff, deviceId))
     conn.commit() 
     
def insertLog(deviceId, msg):
     if deviceId > 0:
          cursor.execute("""INSERT INTO Log (DateAdded, DeviceID, Note)
               VALUES (%s, %s, %s)""", 
               (datetime.now(), deviceId, msg))
     else:
          cursor.execute("""INSERT INTO Log (DateAdded, Note)
               VALUES (%s, %s)""", 
               (datetime.now(), msg))
     conn.commit()

def insertPowerLog(deviceId, power):
     cursor.execute("""INSERT INTO PowerLog (DeviceId, PowerLevel, DateAdded)
          VALUES (%s, %s, %s)""", 
          (deviceId, power, datetime.now()))
     conn.commit()
     
def secondsToMin(sec):
     minutes = math.floor(sec/60)
     seconds = sec - (minutes * 60)
     displaytime = ""
     if minutes > 0:
          displaytime = str(minutes) + " minutes"
          if seconds > 0:
               displaytime = displaytime + ", "
     if seconds > 0:
          displaytime = displaytime + str(seconds) + " seconds"
     return displaytime
     
ser = serial.Serial('/dev/ttyS0', 38400)
print ("---------- RPICT4V3 Power Monitor ----------")
logfile = "stove.log"
arrStove = np.float16([0,0,0,0,0,0,0,0,0,0])
arrDryer = np.float16([0,0,0,0,0,0,0,0,0,0])
i = 0
mx = arrStove.size
stoveOnPow = 0.6
dryerOnPow = 0.6
stoveOn = False
dryerOn = False
lastStoveOn = False
lastDryerOn = False
stoveOnTime = datetime.now()
alertTime = 60 * 30 # 30 minutes
lastAlertTime = datetime.now()
logToFile(logfile, "Monitor started")
insertLog(0, "Monitor started")
StoveDeviceID = 1
DryerDeviceID = 2
try:
     while 1:
          # Read one line from the serial buffer
          line = ser.readline()
          now = datetime.now()
          
          # Remove the trailing carriage return line feed
          line = line[:-2]
          #print (line)
          # Create an array of the data
          Z = line.split()
          PowStove = float(Z[9].decode())
          PowDryer = float(Z[10].decode())
          arrStove[i] = PowStove
          arrDryer[i] = PowDryer
          avgStove = np.average(arrStove)
          avgDryer = np.average(arrDryer)
          i = i + 1
          if i >= mx:
               i = 0

          print ("%s - " % (now.strftime("%x %X")), end='')
          if PowStove > stoveOnPow:
               print (Fore.RED, end='')
          print ("Stove: %s (%s)" % (round(PowStove*100)/100, round(avgStove*100)/100), end='')
          print (Style.RESET_ALL, end='')
          print ("\tDryer: %s (%s)" % (round(PowDryer*100)/100, round(avgDryer*100)/100))
          updateMonitor()
          insertPowerLog(StoveDeviceID, PowStove)
          insertPowerLog(DryerDeviceID, PowDryer)
          updateDBDeviceTime()

          if avgStove > stoveOnPow:
               stoveOn = True
               if lastStoveOn == False:
                    # Stove has turned on, save the date/time
                    stoveOnTime = now
                    updateDBPowerOn(StoveDeviceID, PowStove, avgStove, stoveOnTime)
                    msg = "Stove turned on. Current/Average power: %s/%s" % (PowStove, round(avgStove,2))                        
                    logToFile(logfile, msg)
                    insertLog(StoveDeviceID, msg)
                    arrUsage = np.float16([avgStove])
               else: # Stove was already on
                    secondsOn = seconds_between(now, stoveOnTime)
                    a = np.append(arrUsage, PowStove)
                    arrUsage = a
                    updateDBPower(StoveDeviceID, PowStove, np.average(arrUsage))
                    if secondsOn > alertTime and seconds_between(now, lastAlertTime) > alertTime:
                         print(Fore.RED + "Stove has been on %s!" % (secondsToMin(int(secondsOn))))
                         print(Style.RESET_ALL, end='')
                         msg = "Stove has been on %s. Average power: %s" % (secondsToMin(int(secondsOn)), round(np.average(arrUsage),2))
                         sendTextAlert("Stove Monitor Alert:" + msg, testMode)
                         sendAlexaNotification()
                         logToFile(logfile, msg)
                         insertLog(StoveDeviceID, msg)
                         lastAlertTime = now
          else:
               stoveOn = False
               if lastStoveOn == True:
                    updateDBPowerOff(StoveDeviceID, PowStove, np.average(arrUsage), now)
                    msg = "Stove turned off. Average power %s" % (round(np.average(arrUsage),2))
                    logToFile(logfile, msg)
                    insertLog(StoveDeviceID, msg)
          
          if avgDryer > dryerOnPow:
               dryerOn = True
               if lastDryerOn == False:
                    # Dryer has turned on, save the date/time
                    dryerOnTime = now
                    updateDBPowerOn(DryerDeviceID, PowDryer, avgDryer, dryerOnTime)
                    msg = "Dryer turned on. Current/Average power: %s/%s" % (PowDryer, round(avgDryer,2))                        
                    logToFile(logfile, msg)
                    insertLog(DryerDeviceID, msg)
                    arrUsageDryer = np.float16([avgDryer])
               else: # Dryer was already on
                    secondsOn = seconds_between(now, dryerOnTime)
                    a = np.append(arrUsageDryer, PowDryer)
                    arrUsageDryer = a
                    updateDBPower(DryerDeviceID, PowDryer, np.average(arrUsageDryer))
          else:
               dryerOn = False
               if lastDryerOn == True:
                    updateDBPowerOff(DryerDeviceID, PowDryer, np.average(arrUsageDryer), now)
                    msg = "Dryer turned off. Average power %s" % (round(np.average(arrUsageDryer),2))
                    logToFile(logfile, msg)
                    insertLog(DryerDeviceID, msg)

          lastStoveOn = stoveOn
          lastDryerOn = dryerOn

except KeyboardInterrupt:
     ser.close()
     logToFile(logfile, "Monitor exited")
     insertLog(0, "Monitor exited")
     cursor.close()
     conn.close()
     
