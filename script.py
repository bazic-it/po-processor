import os
import csv
import pandas as pd
from datetime import datetime
import openpyxl
from functools import cmp_to_key
from config import *

class Order:
    def __init__(self, PO, vendor, shipToLocation, ASIN, externalId, externalIdType, modelNumber, title, availability, windowType, windowStart, windowEnd, expectedDate, quantityRequested, expectedQuantity, unitCost, currencyCode):
        self.PO = PO
        self.vendor = vendor
        self.shipToLocation = shipToLocation
        self.ASIN = ASIN
        self.externalId = externalId
        self.externalIdType = externalIdType
        self.modelNumber = modelNumber
        self.itemNumber = self.modelNumber.split('-')[0]
        self.title = title
        self.availability = availability
        self.windowType = windowType
        self.windowStart = windowStart
        self.windowEnd = windowEnd
        self.expectedDate = expectedDate
        self.quantityRequested = int(quantityRequested)
        self.expectedQuantity = int(expectedQuantity)
        self.unitCost = float(unitCost)
        self.currencyCode = currencyCode
        self.uomCode = None
        self.totalPrice = self.unitCost * self.quantityRequested

    def __str__(self):
        return 'PO: {}, Item Number: {}, UOM Code: {}, Qty: {}, Total: {}'.format(self.PO, self.modelNumber, self.uomCode, self.quantityRequested, self.totalPrice)

def getTimestamp():
    now = datetime.now()
    return datetime.strftime(now, "%m%d%Y%H%M%S")

def getCurrentime():
    return datetime.now()

def getFileModifiedDate(filepath):
    return datetime.fromtimestamp(os.path.getmtime(filepath))

def getDaysDifferent(currentTime, timestamp):
    return (currentTime - timestamp).days

def getUOMMasterData(inputFilepath):
    mapped = {}

    try:
        with open (inputFilepath, mode='r') as file:
            content = csv.reader(file)
            for line in content:
                if (len(line) == 3):
                    mapped['{}-{}'.format(line[1], line[2])] = line[0]
    except:
        print('*** Error: Failed to read input file for UOM Master. Please make sure filename is valid. ***')
        return {}

    return mapped

def getInventoryAndPriceMasterData(inputFilepath):
    pass

def getOrdersFromInputfile(filepath):
    orders = []
    
    try:
        with open (filepath, mode='r') as file:
            count = 1
            content = csv.reader(file)
            for line in content:
                if count == 1:
                    count += 1
                    continue
        
                if (len(line) == 17):
                    if not line[6]: # if Model Number not exists
                        continue
                    order = Order(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11], line[12], line[13], line[14], line[15], line[16])
                    orders.append(order)
                count += 1
    except Exception as err:
        message = 'Please check your input batch file: {}'.format(filepath)
        print('*** Error: Failed to read batch input file. Please make sure filename is valid. err: {} ***'.format(err))
        return []

    return orders

def processAmazonVendorCentralOrders(orders, uomMaster):
    acceptedOrders = []
    rejectedOrders = []
    for order in orders:
        uomCode = ''
        if '-' in order.modelNumber:
            if order.modelNumber in uomMaster:
                modelNumber = uomMaster[order.modelNumber]
                uomCode = modelNumber.split('-')[-1]
            else:
                uomCode = 'EA'
            order.uomCode = uomCode
            acceptedOrders.append([order.PO, order.modelNumber, order.quantityRequested, order.unitCost, order.uomCode, order.totalPrice])
        else:
            rejectedOrders.append([order.PO, order.modelNumber, order.quantityRequested, order.unitCost, order.uomCode, order.totalPrice])
        

    return acceptedOrders, rejectedOrders

def validateInputFilename(filename):
    cleaned = filename
    if '/' in filename:
        cleaned = filename.split('/')[-1]

    if '.csv' not in cleaned:
        cleaned = cleaned + '.csv'

    return USER_DOWNLOADS + cleaned

def getUOMMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, UOM_MASTER_FILENAME)

# def writeLog(timestamp, status):
#     path = os.path.join(ASSETS_BASE_DIR, LOGS_FILENAME)
#     user = os.getenv('COMPUTERNAME')
#     try:
#         with open(path, 'a') as file:
#             file.write('USR;{} | IN;{} | SUCCESS;{} | ERR;{} | WARNING;{} | WARN;{} | OOS;{} | OUT;{} | TS;{}\n'.format(user, status["inputFilename"], status["success"], status["errorMessage"], status["warning"], status["warningMessage"], status["outOfStockSKUs"], status["outputFilename"], timestamp))
#     except:
#         print('*** Error: Failed to write to logs. ***')

def sortOrders(a, b):
    if a[4] == 'CASE' and (b[4] == 'BOX' or b[4] == 'EA'):
        return -1
    elif a[4] == 'BOX' and b[4] == 'EA':
        return -1
    else:
        return 1

def processResult(inputFilepath):
    input = validateInputFilename(inputFilepath)
    timestamp = getTimestamp()

    response = {
        "success": True,
        "errorMessage": "",
        "inputFilename": "",
        "outputFilename": ""
    }

    uomMasterFilepath = getUOMMasterFilepath()

    uomMaster = getUOMMasterData(uomMasterFilepath)
    orders = getOrdersFromInputfile(input)

    acceptedOrders, rejectedOrders = processAmazonVendorCentralOrders(orders, uomMaster)

    if not acceptedOrders:
        response["success"] = False
        response["errorMessage"] = "Please try again or contact admin."
        return response

    acceptedOrders.sort(key=cmp_to_key(sortOrders))

    outputFilename = 'batch_output_{}.xlsx'.format(timestamp)
    outputFilepath = OUTPUT_DIR + outputFilename

    acceptedDF = pd.DataFrame(acceptedOrders, columns=['PO', 'Item Number', 'Qty', 'Unit Cost', 'UOM', 'Total Price'])
    acceptedDF.index = acceptedDF.index + 1

    rejectedDF = pd.DataFrame(rejectedOrders, columns=['PO', 'Item Number', 'Qty', 'Unit Cost', 'UOM', 'Total Price'])
    rejectedDF.index = rejectedDF.index + 1

    with pd.ExcelWriter(outputFilepath, engine='xlsxwriter') as writer:
        acceptedDF.to_excel(writer, sheet_name='Accepted', startrow=0, startcol=0)
        rejectedDF.to_excel(writer, sheet_name='Rejected', startrow=0, startcol=0)

    response["outputFilename"] = outputFilepath

    return response