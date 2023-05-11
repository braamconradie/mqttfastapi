
from fastapi import FastAPI
import uvicorn
#from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
import requests
import json
import time
import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import sqlite3
import random
import time
import threading

#run below only once to createn table..
# conn = sqlite3.connect("library.db")
# cursor = conn.cursor()
# cursor.execute("""CREATE TABLE bcsonoff2
#                  (counter INTEGER, voltage INTEGER, power INTEGER, timestamp1 TIMESTAMP)
#              """)


counter2=0
voltage =0
power=0
timestamp = 0
recordcount =0


app = FastAPI()

print("Alive")

#test

origins = [
    "http://localhost.tiangolo.com",
     "https://api-cors-tester-client-side.glitch.me/"
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def main():
    return {"hello": "world"}
  
@app.get("/hello")
async def main():
    global counter2, recordcount, power, voltage  
    counter2 +=1
    # return jsonify([power,voltage, recordcount]) 
    return {"power ":str(power), "voltage": str(voltage) , "count":str(recordcount)}
  
  
# @app.get("/items/{item}")
# async def subpage(item: str):
#     return {"item": item}

open('example.txt', 'w').close()
consumecount = 0 
counter = 1
recentconsume = []
consumecountlist = []
broker = 'broker.emqx.io'
sub_topic = "stat/mospow2/STATUS10"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(sub_topic)
    print("subscribed to ..." + sub_topic)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_message(client, userdata, msg):
    global counter
    global consumecount
    global recentconsume
    global consumecountlist
    global voltage, power, timestamp, recordcount
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    m_in = json.loads(m_decode) #decode json data
    #print(type(m_in))
    voltage = m_in["StatusSNS"]["ENERGY"]["Voltage"]
    power = m_in["StatusSNS"]["ENERGY"]["Power"]
    timestamp = int(time.time())
    print("Voltage = " + str(voltage) + "  Power = " + str(power))
    #append spreadsheet - the big moment!
    #write to text file
    
    with open('example.txt', 'r+') as f:
        lines = f.readlines()
        consumecount +=1
        recentconsume.append(str(power))
        consumecountlist.append(str(consumecount))
        #put number of reads that are OK before starting to scroll
        if consumecount >=30:
            f.seek(0)
            f.truncate()
            f.writelines(lines[1:])
            recentconsume.pop(0)
            consumecountlist.pop(0)
        nuwe = str(counter)+"," + str(power)
        f.write(nuwe)
        f.write('\n')

    
    body=[timestamp, voltage, power] #the values should be a list

    ## TO DO CALL THIS EVERY 15 seconds r
    # thingspeakcall = "https://api.thingspeak.com/update?api_key=ZIPWDOGJTN68PNDL&field1="+str(voltage)
    # thingspeakcall2 = "https://api.thingspeak.com/update?api_key=ZIPWDOGJTN68PNDL&field1="+str(voltage)+"&field2="+str(power)
    # print (thingspeakcall2)
    # x = requests.get(thingspeakcall2)
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    counter = counter + 1
    insertQuery = """INSERT INTO bcsonoff2 VALUES (?, ?, ?, ?);"""
    currentDateTime = datetime.datetime.now()
    cursor.execute(insertQuery, (counter, voltage, power, currentDateTime))
    conn.commit()
    cursor.execute(""" SELECT max(rowid) FROM bcsonoff2 """)
    recordcount = cursor.fetchone()[0]
    print ("number of databse records =  "+str(recordcount))
    #next step retrieve data, maybe from another file
    stats = str(voltage)+"V  "+ str(power)+"W "+str(recordcount)+" recs"
    client.publish("stats", stats)

##exper start 



##exper end g

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883, 60)
client.loop_start()

# if __name__ == "__main__":
#   app.run()

# def record_loop(loop_on):

# this loop is required if STATUS mqtt command is not sent from anywhere else. If it is triggered from another program/API then this is not required
def mqttloop():
    #not sure about the threading timer - it seems to go way faster than every 10 seconds, changing number does not make a diffs. cannot slow it down
    threading.Timer(1000.0, mqttloop).start()
    #client.publish("cmnd/mospow2/STATUS", 10)
    print("mqttloop")

# def print_hello2():
#     threading.Timer(3.0, print_hello2).start()
#     print("hello2")

mqttloop()

# while True:
#   print ("working")
#   time.sleep(3)

uvicorn.run(app, port = 8080, host = "0.0.0.0")
  

  
  
  
