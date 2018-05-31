#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import mysql
import sys

import mysql.connector as connector
import datetime

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

def getAuthentication():
    try:
        # connect to local PI DB
        myconn = connector.connect(user='root',password='raspberry',host='localhost',database='eventDBv2')
    except:
        print("Authentication fail !!!")
        pass

    else:
        cursor = myconn.cursor()
        # Retrieve the last record from records in eventDBv2
        cursor.execute("SELECT auth FROM records ORDER BY recordID DESC LIMIT 1;")
        _temp = cursor.fetchone()
        # Get the first position from retrieved data
        _isAuth = _temp[0]
        return _isAuth
        cursor.close()
        myconn.close()


def recordToDB():
    try:
        # connection to local PI DB
        myconn = connector.connect(user='root',password='raspberry',host='localhost',database='eventDBv2')

    except:
        print("Local connection failed !!!")
        pass

    else:
        cursor = myconn.cursor()
        # convert uid into string
        uidasstring = ','.join(str(e) for e in uid)
        room_id = '3'
        # call recordToDb procedure to record room_id and uid
        cursor.execute("CALL recordToDb (%d, %s)" %  (room_id, uidasstring))
        cursor.close()
        myconn.close()
        print("Recorded to Local Database")

def syncDB():
    syncAvalString = ("UPDATE availability set flag = true;")
    syncRecordsString = ("UPDATE records set flag = true;")
    try:
        # connection to local PI DB
        piDB = connector.connect(user='root', password='raspberry', host='localhost', database='eventDBv2')

    except:
        print("Connection fail !!!")
        pass

    else:
        piCur = piDB.cursor()
        # Get all entry from records with flag = false
        piCur.execute("SELECT * from records where flag = false;")
        data = piCur.fetchall()
        # Get all entry from availability with flag = false
        piCur.execute("SELECT * from availability where flag = false;")
        data2 = piCur.fetchall()
        if data is not None:
            try:
                # connection to master db ip address is needed
                masterDB = connector.connect(user='root', password='raspberry', host='IP ADDRESS', database='masterDBv2')

            except:
                print("Master Pi DB connection failed")
                pass

            else:
                masterCur = masterDB.cursor()
                for row in data:
                    syncRec = ("INSERT INTO records(roomID,uid,timecheck,depID,auth)VALUES ("+str(row[1])+",'"+str(row[2])+"','"+str(row[3])+"','"+str(row[4])+"',"+str(row[6])+");")
                    masterCur.execute(syncRec)
                    masterDB.commit()
                if data2 is not None:
                    for row in data2:
                        syncAval = ("INSERT INTO availability(roomID,hca,hsk,timecheck,roomStatus)VALUES ("+str(row[1])+",'"+str(row[2])+"','"+str(row[3])+"','"+str(row[4])+"',"+str(row[6])+");")
                        masterCur.execute(syncAval)
                        masterDB.commit()
                        masterCur.close()
                        masterDB.close()

                piCur.execute(syncAvalString)
                piCur.execute(syncRecordsString)
                piDB.commit()

        piCur.close()
        piDB.close()
        print("Recorded to Master Pi DB All OK!!!! FROM MASTER")

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522\nPlease scan card"
print "Press Ctrl-C to stop."

# This loop keeps checking for RFID chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Set authorization by default to False for Indicator
    _isAuth = False

    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Assign uisasstring iwth uid
        uidasstring = ','.join(str(e) for e in uid)

        # Print UID for scanned card
        # print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])+","+str(uid[4])
        #print "Card read UID: "+(','.join(str(e) for e in uid))
        print "Card read UID: " + uidasstring


        # This is the default key for authentication
        #key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # record to local Pi DB script
        recordToDB()

        # sync to master DB script will not stop if no connection
        syncDB()

        # Authenticate
        _isAuth = getAuthentication()
        #status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check authentication
        if _isAuth:
            # Turn on Led1
            MIFAREReader.myfunc(12, 1)
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            time.sleep(0.3)

        else:
            # Turn on Led2
            MIFAREReader.myfunc(16, 1)
            print "Authentication error"
            time.sleep(0.7)

        # Turn off all LED's
        time.sleep(0.3)
        MIFAREReader.myfunc(12, 0)
           MIFAREReader.myfunc(16, 0)

        # Print message
        print "Scan another card"     
