
import os
import shutil
import subprocess
import requests
import json
import csv
import sys
from datetime import datetime

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

def days_since(date_string):
    # Check if the string is empty
    if not date_string:
        return 1000
    
    # Define the date format that matches the input string
    date_format = "%Y-%m-%d %H:%M:%S"
    
    try:
        # Convert the input string to a datetime object
        input_date = datetime.strptime(date_string, date_format)
    except ValueError:
        # Return an empty string if the format is incorrect or parsing fails
        return 1000
    
    # Get the current date and time
    current_date = datetime.now()
    
    # Calculate the difference between the current date and the input date
    delta = current_date - input_date
    
    # Return the number of days (use delta.days to get the days part)
    return delta.days

def convertMemberIdToInt(input):
    try:
        # Convert the input string to a datetime object
            ans = int(input)
            return ans

    except ValueError:
    # Return an empty string if the format is incorrect or parsing fails
        return 0


def convertMemberpress():

    producerExceptionList = ['bearhugs124@yahoo.com', 'trush0119@gmail.com']

    membersCsvLocation = input(' Drop the newly converted file in the right format :')
    membersCsvLocation = membersCsvLocation.replace('.csv ', '.csv')
    if not 'members-' in membersCsvLocation:
        print("This is not a valid file. Please choose a csv file exported from memberpress on the wordpress admin dashboard!")
        sys.exit()
    data = read_csv_as_array_of_arrays(membersCsvLocation)
    headers = ['Email', 'First Name', 'Last Name', 'Full Name', 'Last Transaction Date', 'Days Since Last TXN', 'Member Tier', 'Video Role', 'Total Spent $']
    formattedData = []
    freeTier = [];
    bronzeTier = []
    silverTier = []
    goldTier = []
    platinumTier = []
    for row in data:
        if row[15].lower() == 'latest_txn_date':
            continue

        daysSince = days_since(row[15])
        memberTypeId = convertMemberIdToInt(row[18])

        memberTier = 'None'
        videoRole = ''
        
        if row[17].lower() != 'active':
            memberTier = 'None'
        elif memberTypeId == 5762:
            memberTier = 'Bronze'
        elif memberTypeId == 5778:
            memberTier = 'Free'
        elif memberTypeId == 5780:
            memberTier = 'Gold'
            if row[2] in producerExceptionList:
                videoRole = ''
            else:
                videoRole = 'Producer'
                
        elif memberTypeId == 5781:
            memberTier = 'Platinum'
            if row[2] in producerExceptionList:
                videoRole = ''
            else:
                videoRole = 'Executive Producer'
            
        elif memberTypeId == 5779:
            memberTier = 'Silver'
        else:
            print("didn't find any category! = " + row[17])

        newLine = [row[2].lower(), row[4].capitalize(), row[5].capitalize(), row[4].capitalize() + ' ' + row[5].capitalize() , row[15], str(daysSince), memberTier, videoRole, row[22]];

        if memberTier == 'Bronze':
            bronzeTier.append(newLine)
        elif memberTier == 'Silver':
            silverTier.append(newLine)
        elif memberTier == 'Gold':
            goldTier.append(newLine)
        elif memberTier == 'Platinum':
            platinumTier.append(newLine);
        else:
            freeTier.append(newLine)
    


    freeTier = sorted(freeTier, key=lambda x: x[7], reverse= True)
    bronzeTier = sorted(bronzeTier, key=lambda x: x[7], reverse= True)
    silverTier = sorted(silverTier, key=lambda x: x[7], reverse= True)
    goldTier = sorted(goldTier, key=lambda x: x[7], reverse= True)
    platinumTier = sorted(platinumTier, key=lambda x: x[7], reverse= True)
    
    for row in platinumTier:
        formattedData.append(row)

    for row in goldTier:
        formattedData.append(row)

    for row in silverTier:
        formattedData.append(row)

    for row in bronzeTier:
        formattedData.append(row)

    for row in freeTier:
        formattedData.append(row)
    
    formattedData.insert(0, headers);

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d")
    home_dir = os.path.expanduser("~")
    
    # Define the path to the Downloads folder
    downloads_folder = os.path.join(home_dir, "Downloads")
    finalPath = os.path.join(downloads_folder, 'Memberships ' + formatted_time + '.csv')
    write_array_of_arrays_to_csv(formattedData, finalPath)

def get_current_time():
    # Get the current date and time
    current_time = datetime.now()
    
    # Format it to the desired format 'YYYY-MM-DD HH:MM:SS'
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    return formatted_time


print('test = "' + str(days_since('2024-08-24 16:17:28')) + '"')

selection = input('''

What would you like to do?

1. Convert rafflepress csv to flodesk
2. Merge New Rafflepress entries into flodesk master    
3. Convert Memberpress csv to format for google sheets
    :''')


if selection == '1':
    convertRafflepress()
elif selection == '2':
    mergeRafflepressToFlodesk()
elif selection == '3':
    convertMemberpress()