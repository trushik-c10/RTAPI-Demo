#!/usr/bin/env python3
#WebSocket Client Endpoint in Python
import argparse
import sys
import os
import _thread
import threading
from threading import Lock
import time
import datetime
import requests
#import urllib2

import websocket

import json
import subprocess
from subprocess import Popen
#authToken="fbfe776fac182ce8c034681f26f36ed9ce496b4bfaea2fbff5e2353610de4354"
authToken="eec82673100ecf6d01fd53a7565d8e9f0c6f56883974088b5c059c0e93a4be4d"
def getOptions(args=sys.argv[1:]):
   parser = argparse.ArgumentParser(description="Parses command.")
   parser.add_argument("-r", "--raw", dest='raw',action='store_true', help="output raw data.")
   parser.add_argument("-e", "--epoch",dest='epoch',action='store_true', help="Display EPOCH Time.")
   parser.add_argument("-m", "--mac",dest='mac',action='store_true', help="Display MAC.")
   parser.add_argument("-s", "--sequencenumber",dest='seq',action='store_true', help="Display sequence number.")
   parser.add_argument("-rid", "--recieverid",dest='rid',action='store_true', help="Display Reciever ID.")
   parser.add_argument("-rp", "--recieverplatform",dest='rp',action='store_true', help="Display Reciever Platform(RDK version).")
   parser.add_argument("-p", "--pipe",dest='pipe',action='store_true', help="Display pipe.")
   parser.add_argument("-d", "--description",dest='d',action='store_true', help="Display description.")
   parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode (output everything)")
   parser.add_argument("-i", "--input", help="Subnet (in quotes\" \".)")
   parser.add_argument("-o", "--output", help="Your log file stored in the /logs directory (in quotes\" \").")
   options = parser.parse_args(args)
   return options
def getJSONData(d,key1,key2,defValue):
   if(key2=='.'):
     result = d.get(key1,defValue)
   else:
     result = d.get(key1,{}).get(key2,defValue)
   return result
def on_message(ws, message):
  outputstr=""
  out=str(tdata.messageCount)+","+str(time.time())+","+message+"\n"
  tdata.messageCount=tdata.messageCount+1
# This section will limit the number of messages this will be added to the command line args
#  if(tdata.messageCount>=7000):
#    ws.close()
#    tdata.messageCount=0
################################## 
  line=message
# first two messages from the streaming server are not on JSON format so we just print them as they are and then return
  if(tdata.messageCount<=2):
    print(line)
    return                  
#pull JSON string from message
  jdata=json.loads(line)

# MAC
  if(tdata.mac==1 or tdata.verbose==1):
     res=getJSONData(jdata,'header','estbMac','n/a')
     outputstr=str(res)
#pull EPOCH time from message
  if(tdata.epoch==1 or tdata.verbose==1):
     res=getJSONData(jdata,'metaData','epochTime','n/a')
     outputstr=outputstr+str(res)



#sequence number
  if(tdata.seq==1 or tdata.verbose==1):
     res=getJSONData(jdata,'metaData','sequenceNumber','n/a')
     outputstr=outputstr+", "+str(res)

# pipe
  if(tdata.pipe==1 or tdata.verbose==1):
     res=getJSONData(jdata,'header','pipe','n/a')
     outputstr=outputstr+", "+str(res)

#reciever ID
# receiverId can be empty or "null" in either case it's length is <16 so a string >16 is a Dirty stb
  if(tdata.rid==1 or tdata.verbose==1):
     res=getJSONData(jdata,'header','receiverId','n/a')
     if(len(res)>16):
        outputstr=outputstr+", Dirty"
     else:
        outputstr=outputstr+", Clean"

#reciever Platform (RDX version)
  if(tdata.rp==1 or tdata.verbose==1):
     res=getJSONData(jdata,'header','receiverPlatform','n/a')
     outputstr=outputstr+", "+str(res)

#Description 
  if(tdata.d==1 or tdata.verbose==1):
     res=getJSONData(jdata,'metaData','description','n/a')
     outputstr=outputstr+", "+str(res)

########################################################
# Output data section
# raw message has a "\n\r" at the end remove it to avoid blank lines in csv file
  outputstr=outputstr.strip("\n\r")
# print the collected string of data and send it to the output file
  print(outputstr)
  print("message Count="+str(tdata.messageCount))
  if(tdata.messageCount>2):
    tdata.f.write(outputstr)
#    tdata.f.write("\n\r")
    tdata.f.flush()
#print the raw mwssage and send it to the output file  
##################################
  if(tdata.raw==1 or tdata.verbose==1):
    print("RAW:")
    print(message)
    if(tdata.messageCount>2):
      line=line.replace(",","|")
      tdata.f.write(",")
      tdata.f.write(line)
  tdata.f.write("\n")
  tdata.f.flush()
def on_open(ws):
  ws.send("connection open")
  time.sleep(1)
# use -o=filename arg to select search string
  ws.send(json.dumps({"action": "send-subnet","data": tdata.input}))
#  ws.send(json.dumps({"action": "send-subnet","data": "10:C2:5A:61:E9:1F"}))
  tdata.ApiCallStartTime=time.time()
  if(tdata.startFlag==0):
    tdata.ApiCallStopTime=tdata.ApiCallStopTime-10
    tdata.ApiCallStartTime=tdata.ApiCallStartTime+20

def on_close(ws):
  ws.close()
  if(tdata.startFlag==1):
      tdata.startFlag=0
  print("### closed ###")
  tdata.ApiCallStopTime=time.time()
#  print("thread ",tdata.tn,", ",tdata.ApiCallStartTime,"  ",tdata.ApiCallStopTime," time in min = ",((tdata.ApiCallStopTime-tdata.ApiCallStartTime)/60))
def on_error(ws, message):
  print(message)
def read_API_data(threadName,runtime,i):
  tdata.ApiCallStopTime=time.time()
  time.sleep(2)
  tdata.ApiCallStartTime=time.time()
  tdata.startFlag=0
  tdata.messageCount=0
  startTime="StartTime:"+time.ctime(time.time())
  fileName="logs/"+tdata.output
#  print("filename")
  tdata.f = open(fileName, "a")
#  tdata.f.write("Splunk Timestamp,MAC,Sequence Number,PIPE,Description,RAW\n")
#  print("in read_API_data")

  while(True):
      websocket.enableTrace(True)
      ws = websocket.WebSocketApp("wss://wxre-streaming-api.xre.aws.r53.xcal.tv/v1?authToken="+authToken, on_message = on_message, on_error = on_error, on_close = on_close)
#      ws = websocket.WebSocketApp("wss://wxre-streaming-api.xre.aws.r53.xcal.tv/v1?authToken=728d39959c5fab43bfee2481375b041aa4965005af92abcc4ea206f5a6abf307", on_message = on_message, on_error = on_error, on_close = on_close)
#      ws = websocket.WebSocketApp("wss://wxre-streaming-api.xre.aws.r53.xcal.tv/v1?authToken=9d47627d549db5cccbb87ed4b33bdf79f5964480a001bb93f4dd3be9e0cc4d57", on_message = on_message, on_error = on_error, on_close = on_close)
#      ws = websocket.WebSocketApp("wss://n18r6byomd.execute-api.us-east-1.amazonaws.com/v1?authToken=9d47627d549db5cccbb87ed4b33bdf79f5964480a001bb93f4dd3be9e0cc4d57", on_message = on_message, on_error = on_error, on_close = on_close)
      if(tdata.verbose==1):
          print(ws)
      ws.on_open = on_open
      ws.run_forever()

#      print("restart")

if __name__ == "__main__":
  tdata = threading.local()
  options = getOptions(sys.argv[1:])
  if options.input:
     tdata.input=options.input
  else:
     tdata.input="Wxre_Real_Time_Api"
  if options.output:
     tdata.output=options.output
  else:
     tdata.output="RT_API.log"
  if options.verbose:
     tdata.verbose=1
  else:
     tdata.verbose=0
  if options.epoch:
     tdata.epoch=1
  else:
     tdata.epoch=0
  if options.mac:
     tdata.mac=1
  else:
     tdata.mac=0
  if options.seq:
     tdata.seq=1
  else:
     tdata.seq=0
  if options.pipe:
     tdata.pipe=1
  else:
     tdata.pipe=0
  if options.rid:
     tdata.rid=1
  else:
     tdata.rid=0

  if options.rp:
     tdata.rp=1
  else:
     tdata.rp=0
  if options.d:
     tdata.d=1
  else:
     tdata.d=0
  if options.raw:
     tdata.raw=1
  else:
     tdata.raw=0
  try:
    read_API_data("thread1_long",10,0) 
  except:
    print("Error: unable to start Streaming API")

  time.sleep(20)