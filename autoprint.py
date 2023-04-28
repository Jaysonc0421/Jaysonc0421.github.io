from escpos.printer import Usb
from escpos.printer import File

from datetime import datetime
import pytz

def printOrder(docID, data):
    # Set up the printer object
    # printer = Usb(0x0416, 0x5011)
    printer = File('./output.txt')

    # Send the command to initialize the printer
    printer.set(align='center', font='b', height=2, width=2)
    printer.text('*' * 24 + '\n')

    printer.set(align='left', font='b', height=2, width=2)
    printer.text('*')
    printer.set(align='right', font='b', height=2, width=2)
    printer.text('*\n')

    printer.set(align='left', font='b', height=2, width=2)
    printer.text('*')
    printer.set(align='center', font='b', height=2, width=2)
    printer.text('Pizza Shack')
    printer.set(align='right', font='b', height=2, width=2)
    printer.text('*\n')

    printer.set(align='left', font='b', height=2, width=2)
    printer.text('*')
    printer.set(align='right', font='b', height=2, width=2)
    printer.text('*\n')

    printer.set(align='left', font='b', height=2, width=2)
    printer.text('*')
    printer.set(align='center', font='b', height=2, width=2)
    printer.text('(740) 695-4244')
    printer.set(align='right', font='b', height=2, width=2)
    printer.text('*\n')

    printer.set(align='center', font='b', height=2, width=2)
    printer.text('*' * 24 + '\n')

    printer.set(align='center', font='a', height=1, width=1)
    nytz = pytz.timezone('America/New_York')
    time = data['timestamp'].astimezone(nytz).strftime('%m-%d-%Y %H:%M')
    printer.text(time + '\n')

    printer.text(f'Sold To: {data["name"]}\n')
    printer.text(f'PH: {data["phoneNumber"]}\n')

    if data['delivery_method'] == 'Pickup':
        printer.text(f'Pickup Time: {data["pickupTime"]}\n')
        printer.text('\n')
    else:
        printer.text(data['address'])
        printer.text('\n')

    printer.text('+' + '-'*46 + '+\n')

    for item in data['items']:
        text = ''

        if item['size'] != None:
            text += item['size'] + ' '

        text += item['name'] + ' '

        if item['preset'] != None:
            text += f'({item["preset"]})'

        text += ' w/ '

        for option in item['options'].keys():
            if item['options'][option] == bool and item['options'][option] == True:
                text += f'{option},'
            elif item['options'][option] == int and item['options'][option] != 0:
                text += f'{item["options"][option]} {option},'
        
        printer.text(text)

        printer.set(align='right', font='a', height=1, width=1)
        printer.text(f'   ${item["price"]}')
        printer.text('\n')


    printer.cut()
    printer.close()

    data['printed'] = True
    doc_ref = db.collection('orders').document(docID).set(data)





import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate('./serviceAccount.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()

# Create a reference to the collection you want to listen to
collection_ref = db.collection('orders')

# Create a function to handle document changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        if doc.exists:
            if 'printed' not in doc.to_dict() or doc.to_dict()['printed'] == False:
                printOrder(doc.id, doc.to_dict())
        else:
            print(f'Order {doc.id} has been deleted')

# Watch the collection
collection_watch = collection_ref.on_snapshot(on_snapshot)

import requests

import subprocess
import sys

version = '1.1'

def checkForUpdate(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        if doc.to_dict()['printer_version'] != version:
            response = requests.get('https://stcpizzashack.com/autoprint.py')
            with open('app.py', 'wb') as file:
                file.write(response.content)

            subprocess.Popen(["python3", 'app.py'])
            sys.exit()

db.collection('settings').document('administrators').on_snapshot(checkForUpdate)

while True:
    continue
