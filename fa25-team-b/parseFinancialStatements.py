import subprocess
from dateutil import parser
from decimal import Decimal
import os
import pandas as pd
import numpy as np
import re
import csv

path = r"C:\Users\Cameron\Documents\muckrock"
pdf = r"\Financial Statements.pdf"


def getOCRText(pdf: str, idx: int) -> str:
    #TODO
    return pdf

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

def buildFinancialRow(date: str, category: str, cols: list[str]) -> list[str]:
    assetType = ' '.join(cols[0:-1])
    balance = re.findall(r'-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?', cols[-1])

    if len(balance) == 1:
        return [date.strftime("%Y-%m-%d"), assetType, balance[0], category]
    else:
        return [date.strftime("%Y-%m-%d"), assetType, np.nan, category]

def parseFinancials(pages: list[str]) -> None:
    header = ['Date', 'AssetType', 'Balance', 'Category']
    data = []

    for page in pages:
        page = os.linesep.join([s for s in page.splitlines() if s])
        lines = page.splitlines()
        date = parser.parse(lines[3].strip()[6:])
        category = ""

        start = [idx for idx, val in enumerate(lines) if "Balance" in val][0] + 1

        for line in lines[start:-1]:
            line = line.strip()
            cols = re.split(r'[\s]{2,}', line)

            if len(cols) == 1 and not re.search('[=-]', cols[0]):
                category = cols[0]
            elif "EQUITY" in cols[0]:
                category = "EQUITY"
                data.append(buildFinancialRow(date, category, cols))
            else:
                data.append(buildFinancialRow(date, category, cols))

    df = pd.DataFrame(data)
    df.columns = header
    df = df.dropna()
    df.to_csv(path + r'\FinancialStatement.csv', index=False)

def parseTotalBudget(pages: list[str]) -> None:
    print("hi")

def parseBranchBudget(pages: list[str]) -> None:
    print("hi")

def parseRevenue(pages: list[str]) -> None:
    print("hi")

def runProcess(pdf: str) -> None:
    pageType = {"FinancialStatement" : [],
                "OperatingBudget" : [],
                "OperatingBranchBudget" : [],
                "RevenueStatement" : [],
                "None" : []}

    #text = subprocess.check_output(['pdftotext', '-layout', path + pdf, '-']).decode('utf-8')
    with open(path + r'\FinancialTexts.txt') as f:
        text = f.read()

    pages = text.split('\f')

    for i in range(len(pages)):
        if len(pages[i]) == 0:
            pages[i] = getOCRText(pdf, i)

        pageType[determinePageType(pages[i])].append(pages[i])

    parseFinancials(pageType["FinancialStatement"])
    parseTotalBudget(pageType["OperatingBudget"])
    parseBranchBudget(pageType["OperatingBranchBudget"])
    parseRevenue(pageType["RevenueStatement"])

runProcess(pdf)