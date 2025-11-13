import datetime
import subprocess
from dateutil import parser
from decimal import Decimal
import os
import pandas as pd
import numpy as np
import re
import csv

## FinancialTexts.txt is located at this drive path (which is linked in the README)
##  - MuckRock: US Military Base Slot Machine Revenue Explorer\Team B\TeamB_Exported_Data\FinancialStatements

## INSTRUCTIONS FOR USAGE
##  1. Set path to the folder where you want to store the output of this parser
##  2. Download the FinancialTexts.txt file and put it said folder (this parser uses a Linux based text extraction
##      tool which requires a custom install, so I've provided the post-extraction text to be read in directly instead of the pdf)
##  3. Run the file, the CSVs will be created in the same folder.

path = r"C:\Users\Cameron\Documents\muckrock" 
pdf = r"\Financial Statements.pdf"
csvs = [r'\FinancialStatement.csv', r'\ActualVsBudget.csv', r'\BranchBudget.csv', r'\GamingRevenue.csv']
badDates = [datetime.datetime(2021, 1, 31), datetime.datetime(2020, 5, 31)]
with open(path + r'\categoryMap.csv', 'r') as f:
    reader = csv.reader(f)
    categoryMap = dict(reader)

#Getting page type from title
def determinePageType(page: str) -> str:
    if "Statement of Financial Condition" in page:
        return "FinancialStatement"
    elif "Operating Results" in page:
        if "Actual vs Budget" in page:
            return "OperatingBudget"
        elif "Branch of Service" in page:
            return "OperatingBranchBudget"
        else:
            return "None"
    elif "Statement of Gaming Revenue" in page:
        return "RevenueStatement"
    else:
        return "None"
    
#Parse date string into a datetime object
def parseDate(line: list[str]) -> datetime:
    line[-3] = re.sub(r'[il]', "1", line[-3])
    line[-2] = line[-2]
    line[-1] = re.sub(r'[il]', "1", line[-1])

    return parser.parse(" ".join(line[-3:]).strip())

#Clean number strings that have been improperly parsed
def numCleanup(numStr: str) -> str:
    #print(numStr)
    trailingMinus = ''

    removeSpace = re.sub(r'[\s+]', '', numStr.strip()) #remove spaces
    badChars = re.sub(r'[:;,._·\"\']', '', removeSpace) #remove characters that we don't want (add back in decimal later)
    if badChars[-1] == '-': #we need to remove erroneous characters so we can check if minus is in expected place
        trailingMinus = '-' #save trailing minus before we erase all instances of character

    removeMinus = re.sub(r'[-]', '', badChars) #now we can remove all minus instances
    letterTransposition = re.sub(r'[LlJ]', '1', removeMinus) #fixes num->letter transposition error 
    zeroTransposition = re.sub(r'[QODo]', '0', letterTransposition) #fixes letter->number transposition error for 0 and 5
    fiveTransposition = re.sub(r'[Ss]', "5", zeroTransposition)
    
    return trailingMinus + fiveTransposition[:-2] + '.' + fiveTransposition[-2:] #add back in decimal point and put minus in front for excel (if needed)
    
#convert to DataFrame for easy csv export
def exportCSV(data: list[list[str]], file: str, headers: list[str]):
    df = pd.DataFrame(data)
    df.columns = headers
    df.to_csv(path + file, index=False)

#Build row for the FinancialStatements.csv file
def buildFinancialRow(date: datetime, category: str, cols: list[str]) -> list[str]:
    assetType = re.sub(r'[.]', '', ' '.join(cols[0:-1]))
    cols[-1] = numCleanup(cols[-1])
    return [date, assetType, cols[-1], category]

#Build row for the ActualVsBudget.csv and BranchBudget file
def buildBudgetRow(date: datetime, location: str, assetType: str, cols: list[str], idx: int) -> list[str]:
    budgetRow = [date, location, assetType]

    if len(cols) > idx: #Sometimes category will get split up into multiple columns, so we concat them together.
        cols = [" ".join(cols[:-(idx-1)])] + cols[(len(cols) - (idx-1)):]

    if len(cols) < idx: #Sometimes we get too few columns because entries only have one space between them and don't get split
        for j in range(1, len(cols)):
            if cols[j].count('.') == 2: #if we have two numbers in one column
                cols = cols[:j] + cols[j].split() + cols[(j+1):]

    for i in range(len(cols)):
        if i == 0:
            if cols[i] in categoryMap.keys():
                budgetRow.append(categoryMap[cols[i]])
            else:
                budgetRow.append(cols[i]) #append row category
        else:
            #print(str(date) + " | " + location + " | " + assetType + " | " + cols[i])
            cols[i] = numCleanup(cols[i])
            if cols[i] == '-242631.91': #bad solution but it works and others haven't for some indiscernable reason
                cols[i] = '-24263.91'
                
            budgetRow.append(cols[i]) #TODO: Get regex parser to ensure number, otherwise append np.nan!

    return budgetRow

#Build row for the GamingRevenue.csv file
def buildRevenueRow(date: datetime, cols: list[str]) -> list[str]:
    revenueRow = [date]


    if len(cols) > 7: #Sometimes category will get split up into multiple columns
        cols = [" ".join(cols[:-(7-1)])] + cols[(len(cols) - (7-1)):]

    if len(cols) < 7: #Sometimes we get too few columns because entries only have one space between them and don't get split
        for j in range(1, len(cols)):
            if cols[j].count('.') == 2: #if we have two numbers in one column
                cols = cols[:j] + cols[j].split() + cols[(j+1):]

    for i in range(len(cols)):
        if i == 0:
            if cols[i] in categoryMap.keys(): #fix broken category names
                revenueRow.append(categoryMap[cols[i]])
            else:
                revenueRow.append(re.sub("S ", "S", cols[i])) #append row category
        else:
            cols[i] = numCleanup(cols[i])
            revenueRow.append(cols[i]) #TODO: Get regex parser to ensure number, otherwise append np.nan!

    return revenueRow

#Parse all Statement of Financial Condition pages
def parseFinancials(pages: list[str]) -> None:
    header = ['Date', 'AssetType', 'Balance', 'Category']
    data = []

    for page in pages:
        page = os.linesep.join([s for s in page.splitlines() if s]) #remove blank lines
        lines = page.splitlines() #split page into lines
        date = parseDate(lines[3].strip().split())
        category = ""

        start = [idx for idx, val in enumerate(lines) if "Balance" in val][0] + 1 #find starting index for asset data

        if date.year == 2020 and date.month == 5:
            lines[11] = lines[11].strip()[:-1] + '-'

        for line in lines[start:-1]:
            line = line.strip()
            cols = re.split(r'[\s]{2,}', line) #split by multiple whitespace delimiter

            if len(cols) == 1 and '--' not in cols[0] and '==' not in cols[0]:
                category = cols[0]
            elif "EQUITY" in cols[0]:
                category = "EQUITY"
                if re.match(r'[\w]', ' '.join(cols[0:-1])) :
                    data.append(buildFinancialRow(date, category, cols))
            else:
                if re.match(r'[\w]', ' '.join(cols[0:-1])) :
                    data.append(buildFinancialRow(date, category, cols))

    exportCSV(data, csvs[0], header) #export to csv file

#Parse all Actual Vs Budget pages
def parseTotalBudget(pages: list[str]) -> None:
    header = ['Date', 'Location', "AssetType", 'Category', 'Month_Actual', 'Month_Budget', 
              'Month_Variance', 'YTD_Actual', 'YTD_Budget', 'YTD_Variance']
    data = []
    assets = {"Revenue": "Revenue", 
              "Operating Expenses": "Expenses", 
              "Interest Revenue": "Net"}
    
    tbBadDates = badDates
    tbBadDates.append(datetime.datetime(2020, 1, 31))

    for page in pages:
        page = os.linesep.join([s for s in page.splitlines() if s]) #remove blank lines
        lines = page.splitlines() #split page into lines
        date = parseDate(lines[3].strip().split()) #parse date from header
        location = lines[1].split()[0] #get location (Korea, Europe, Japan or Consolidated)
        assetType = ""

        if date.year == 2019 and location == "Korea":
            lines[34] = lines[34][:70] + lines[32].strip() + lines[34][70:]
            lines = lines[:32] + lines[34:]

        if date not in badDates:
            for line in lines[4:-1]: #for lines with data
                line = line.strip()
                cols = re.split(r'[\s]{2,}', line) #split into columns by multiple whitespace delimiter

                if not re.match(r'[-=_]{3,}', cols[0]): #if the current line isn't a section delimiter (denoted by --- or ===)
                    if cols[0] in assets: #if beginning maps to assettype we will update the assetType column
                        assetType = assets[cols[0]]

                    if len(cols) > 1 and assetType != "": #if we have an assettype and a line with budget data build row
                        data.append(buildBudgetRow(date, location, assetType, cols, 7))

    exportCSV(data, csvs[1], header) #csv export

#Parse all Branch Operating Results pages
def parseBranchBudget(pages: list[str]) -> None:
    header = ['Date', 'Location', "AssetType", 'Category', 'ARMP', 'Army', 'Navy', 'USMC', 'MonthCount']
    data = []
    assets = {"Revenue": "Revenue", 
              "Operating Expenses": "Expenses", 
              "Interest Revenue": "Net"}
    word2num = {"Two": "2", "Three": "3", "Four": "4", "Five": "5", "Six": "6", "Seven": "7", 
                "Eight": "8", "Nine": "9", "Ten": "10", "Eleven": "11", "Twelve": "12"} #found a library for this that doesn't work.

    for page in pages:
        page = os.linesep.join([s for s in page.splitlines() if s]) #remove blank lines
        lines = page.splitlines() #split page into lines
        months = "1"
        if 'Months' in lines[3].strip(): #If we're dealing with a multiple month consolidated report
            months = word2num[lines[3].strip().split()[2]]
        
        date = parseDate(lines[3].strip().split())
        location = lines[1].split()[0] #get location (Korea, Europe, Japan or Consolidated)
        assetType = ""

        if date.month == 1 and date.year == 2020 and location == 'Europe':
            lines[12] = "Operating Expenses"

        if date.year == 2019 and months == "3":
            if location == "Consolidated":
                lines[16] = lines[16][:35] + '4' + lines[16][36:]
            elif location == "Japan":
                lines[24] = lines[24][:79] + lines[24][80:]

        if date not in badDates:
            for line in lines[4:-1]: #for lines with data
                line = line.strip()
                cols = re.split(r'[\s]{2,}', line)

                if not re.match(r'[-=_]{3,}', cols[0]): #if the current line isn't a section delimiter (denoted by --- or ===)
                    if cols[0] in assets: #if beginning maps to assettype we will update the assetType column
                        assetType = assets[cols[0]]

                    if len(cols) > 1 and assetType != "": #if we have an assettype and a line with budget data build row
                        data.append(buildBudgetRow(date, location, assetType, cols, 5))
                        data[-1].append(months)

    exportCSV(data, csvs[2], header) #csv export

#Parse all Statement of Gaming Revenue pages
def parseRevenue(pages: list[str]) -> None:
    header = ['Date', 'Base_Location', 'Europe', 'Korea', 'Japan', 'YTD Europe', 'YTD Korea', 'YTD Japan']
    data = []

    for page in pages:
        page = os.linesep.join([s for s in page.splitlines() if s]) #remove blank lines
        lines = page.splitlines() #split page into lines
        date = parseDate(lines[2].strip().split())

        if date.year == 2020 and date.month == 1:
            lines[40] = lines[40] + lines[42]
            lines = lines[:42]

        if date.year == 2019 and date.month == 12:
            lines[7] = lines[5] + lines[7]
            lines = lines[0:5] + lines[6:]

        if date not in badDates:
            for line in lines[5:-1]: #for lines with data
                line = line.strip()
                cols = re.split(r'[\s]{2,}', line)

                if not re.match(r'[-=_]{3,}', cols[0]) and len(cols) > 1: #if the current line isn't a section delimiter (denoted by --- or ===)
                    data.append(buildRevenueRow(date, cols))

    exportCSV(data, csvs[3], header) #csv export

#Run the parser
def runProcess(pdf: str) -> None:
    pageType = {"FinancialStatement" : [],
                "OperatingBudget" : [],
                "OperatingBranchBudget" : [],
                "RevenueStatement" : [],
                "None" : []} #dict storing pages by type

    #read in PDF
    #text = subprocess.check_output(['pdftotext', '-layout', path + pdf, '-']).decode('utf-8')
    with open(path + r'\FinancialTexts.txt') as f:
        text = f.read()

    pages = text.split('\f') #split into pages

    for i in range(len(pages)):
        if len(pages[i]) != 0: 
            pageType[determinePageType(pages[i])].append(pages[i]) #otherwise append page to its list in dict

    print(len(pageType["None"]))

    #call to parse each type of page
    parseFinancials(pageType["FinancialStatement"])
    parseTotalBudget(pageType["OperatingBudget"])
    parseBranchBudget(pageType["OperatingBranchBudget"])
    parseRevenue(pageType["RevenueStatement"])

runProcess(pdf)