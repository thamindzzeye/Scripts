
import os
import shutil
import subprocess
import requests
import json
import csv
import sys

def get_ip_info(ips):
    url = 'http://ip-api.com/batch'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=json.dumps(ips))
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def read_csv_as_array_of_arrays(file_path):
    data = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return data

def write_array_of_arrays_to_csv(data, file_path):
    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        for row in data:
            csv_writer.writerow(row)



# if __name__ == "__main__":
#     # List of IP addresses to query
#     ips = [
#         "98.176.130.135",
#         "155.133.15.233",
#         "1.1.1.1"
#     ]

#     try:
#         ip_info = get_ip_info(ips)
#         print(json.dumps(ip_info, indent=4))
#     except Exception as e:
#         print(f"Error: {e}")


def doesEmailExistInMasterMailingList(emailAddress, masterData):
    for row in masterData:
        currentEmail = row[1].lower()
        if currentEmail == emailAddress.lower():
            return True
    return False

def convertRafflepress():
    fileLocation = input(' Drop the file here or specify full file location:')
    fileLocation = fileLocation.replace('.csv ', '.csv')
    data = read_csv_as_array_of_arrays(fileLocation)
    # THis is the format from rafflepress
    "['First Name', 'Last Name', 'Email', 'Entries', 'Status', 'Winner', 'Created', 'IP', 'Meta', 'Referred By', 'Terms Consent']"
    # This is the format we need for flodesk
    "['First Name', 'Last Name', 'Email', 'Optin Time', 'Optin IP', 'Confirm Time', 'Confirm IP', 'Last Changed']"
    output = [['First Name', 'Last Name', 'Email', 'Optin Time', 'Optin IP', 'Confirm Time', 'Confirm IP', 'Last Changed']]
    
    for row in data:
        if row[0] == 'First Name':
            continue
        newEntry = [row[0], row[1], row[2], row[6], row[7], row[6], row[7],row[6]]
        output.append(newEntry)

    print(output)
    write_array_of_arrays_to_csv(output, fileLocation.replace('.csv', '_flodesk.csv'))

def mergeRafflepressToFlodesk():
    newEntriesLocation = input(' Drop the newly converted file in the right format :')
    newEntriesLocation = newEntriesLocation.replace('.csv ', '.csv')
    if not 'flodesk.csv' in newEntriesLocation:
        print("This is not a valid file. Please convert it to flodesk format first!")
        sys.exit()
    print("Ok Next we need to pick the master Flodesk email csv")
    flodeskLocation = input(' :')
    flodeskLocation = flodeskLocation.replace('.csv ', '.csv')

    masterData = read_csv_as_array_of_arrays(flodeskLocation)
    newData = read_csv_as_array_of_arrays(newEntriesLocation)

    loop = 0
    uniqueData = [newData[0],['Subscriber First Name','Subscriber Last Name','Subscriber Email Address','Time Subscriber submitted the form','IP Address of form submission','Time Double Optin was confirmed','IP Address if double opt in confirmation','Last date data was recorded for this subscriber']]
    print(uniqueData)
    for entry in newData:
        if loop == 0:
            loop = 1
            continue
        exists = doesEmailExistInMasterMailingList(entry[2], masterData)
        if exists == False:
            uniqueData.append(entry)
            print(uniqueData)

    write_array_of_arrays_to_csv(uniqueData, newEntriesLocation.replace('.csv', '_unique.csv'))


selection = input('''

What would you like to do?

1. Convert rafflepress csv to flodesk
2. Merge New Rafflepress entries into flodesk master    

    :''')


if selection == '1':
    convertRafflepress()
elif selection == '2':
    mergeRafflepressToFlodesk()