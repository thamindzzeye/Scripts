import csv, pandas
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
from pathlib import Path

productNameRow = 0
productPriceRow = 1
productSerialNumber = 2
productOferingIdStart = 3
id_amazon = '637c765d-77c5-4531-992c-0d1811cf197f'

def createAmazonDict(items):
    result= {'id': id_amazon, 'taskGroupName': 'Amazon', 'taskGroupSite': 'Amazon', 'totalCarts': 0, 'totalCheckouts': 0, 'runningTasks': 0}
    result['test'] = 'ok'
    return result

def getStartedLookingForCSVFiles():
    workingDir = os.getcwd()
    files = os.listdir(workingDir)
    csvFiles = []
    for file in files:
        split_up = os.path.splitext(file)
        extension = split_up[1]
        if extension == '.csv':
            csvFiles.append(os.path.join(workingDir, file))


    # Now we have a list of valid CSV files
    products = []

    for csvFile in csvFiles:
        result = pandas.read_csv(csvFile)
        rows, cols = result.shape
        for col in range(0,cols):
            data = result.iloc[:,col:col + 1]
            name = data.iloc[productNameRow,0]
            price = data.iloc[productPriceRow,0]
            sn = data.iloc[productSerialNumber,0]
            if pandas.isna(name):
                continue
            offeringId = data.iloc[productOferingIdStart, 0]
            offeringIdIndex = productOferingIdStart + 1
            while pandas.isna(data.iloc[offeringIdIndex,0]) == False:
                offeringId = data.iloc[offeringIdIndex,0]
                offeringIdIndex += 1
            newItem = {'name': name,'price':price,'sn':sn,'offeringId':offeringId}
            products.append(newItem)

    return products

products = getStartedLookingForCSVFiles()
testing = createAmazonDict(products)
print(testing)
