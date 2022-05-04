import serial
import numpy as np 
from datetime import datetime
from datetime import timedelta
from colorama import Fore, Back, Style
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
from twilio.rest import Client

account_sid = "-- ENTER SID HERE --"
auth_token  = "-- ENTER TOKEN HERE -- "
client = Client(account_sid, auth_token)
testMode = False

def seconds_between(d1, d2):
    return abs((d2 - d1).total_seconds())

def sendTextAlert(message, testMode):
     if testMode == False:
          message = client.messages.create(
          to="+18135551212", 
          from_="+12223334444",
          body=message)
    
def logToFile(logfile, msg):
     f = open(logfile, "a")
     f.write(datetime.now().strftime("%x %X") + ": " + msg + "\n")
     f.close()
     
ser = serial.Serial('/dev/ttyS0', 38400)
print ("---------- RPICT4V3 Power Monitor ----------")
logfile = "stove.log"
arrStove = np.float16([0,0,0,0,0,0,0,0,0,0])
arrDryer = np.float16([0,0,0,0,0,0,0,0,0,0])
i = 0
mx = arrStove.size
stoveOnPow = 0.6
stoveOn = False
lastStoveOn = False
stoveOnTime = datetime.now()
alertTime = 60 * 20 # 20 minutes
lastAlertTime = datetime.now()
logToFile(logfile, "Monitor started");
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
          PowDryer = Z[10].decode()
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
          print ("Stove: %s (%s)" % (PowStove, avgStove), end='')
          print (Style.RESET_ALL, end='')
          print ("\tDryer: %s (%s)" % (PowDryer, avgDryer))

     
          if avgStove > stoveOnPow:
               stoveOn = True
               if lastStoveOn == False:
                    # Stove has turned on, save the date/time
                    stoveOnTime = now
                    msg = "Stove turned on. Current/Average power: %s/%s" % (PowStove, avgStove)                        
                    logToFile(logfile, msg)
                    arrUsage = np.float16([avgStove])
               else: # Stove was already on
                    secondsOn = seconds_between(now, stoveOnTime)
                    a = np.append(arrUsage, PowStove)
                    arrUsage = a
                    if secondsOn > alertTime and seconds_between(now, lastAlertTime) > alertTime:
                         print(Fore.RED + "Stove has been on %s seconds!" % (int(secondsOn)))
                         print (Style.RESET_ALL, end='')
                         msg = "Stove has been on %s seconds. Average power: %s" % (int(secondsOn), np.average(arrUsage))                        
                         sendTextAlert("Stove Monitor Alert:" + msg, testMode)
                         logToFile(logfile, msg)
                         lastAlertTime = now
          else:
               stoveOn = False
               if lastStoveOn == True:
                    msg = "Stove turned off"
                    logToFile(logfile, msg)
          
          
               
          lastStoveOn = stoveOn

except KeyboardInterrupt:
     ser.close()
