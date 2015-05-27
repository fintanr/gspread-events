#!/usr/bin/python
#
# an events calender cheat app, use a simple google spreadsheet
# to keep track of events, and generate a markdown file of past
# and future events for use later in Jekyll
#
# we also pull a news feed for the same doc
#

import gspread
import os
import argparse
from oauth2client.client import SignedJwtAssertionCredentials
from datetime import date, datetime, timedelta
from time import strptime, mktime

def oauthLogin():
    try:
        os.environ['GOOGLE_KEY']
        os.environ['GOOGLE_EMAIL']
        os.environ['EVENTS_SHEET']
    except KeyError:
        print "Please ensure you have GOOGLE_KEY, GOOGLE_EMAIL and EVENTS_SHEET set"
        exit(1)

    pemFile = os.environ['GOOGLE_KEY']
    f = file(pemFile, 'rb')
    key = f.read()
    f.close()

    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(os.environ['GOOGLE_EMAIL'], key, scope)

    try:
        gc = gspread.authorize(credentials)
    except AuthenticationError:
        print "Authentication Error"
        exit(1)

    return (gc)

def extractEvents(gc, outDir):
    sh = gc.open(os.environ['EVENTS_SHEET'])
    ws = sh.worksheet("Events")

    if ( not os.path.isdir(outDir) ):
        print "Outdir %s not found" % outDir
        exit(1)

    today = str(date.today().strftime('%-m/%-d/%Y'))
    allVals = ws.get_all_records()

    upcomingFile = outDir + "/UpcomingEvents.md"
    pastFile = outDir + "/PastEvents.md"

    upcoming = open(upcomingFile, "w")
    past = open(pastFile, "w")

    for row in allVals:
        thisDate = row['Date']

        if ( row['Publish'] == 'Yes' ):
            thisEvent = "* (" + row['Link'] + ")[" + row['Title'] + "]"
            thisEvent += ", " + row['Location'] + "," + row['Long Date String'] + "\n"

            if ( thisDate >= today ):
                upcoming.write(thisEvent)
            else:
                past.write(thisEvent)

def extractNews(gc, outDir):
    sh = gc.open(os.environ['EVENTS_SHEET'])
    ws = sh.worksheet("News")

    if ( not os.path.isdir(outDir) ):
        print "Outdir %s not found" % outDir
        exit(1)

    allVals = ws.get_all_records()

    allNewsFile = outDir + "/AllNews.md"
    latestNewsFile = outDir + "/LatestNews.md"

    allNews = open(allNewsFile, "w")
    latestNews = open(latestNewsFile, "w")

    ourNews = dict()
    minCounter = 0

    for row in allVals:
        thisDate = row['Date']
        longDate = datetime.fromtimestamp(mktime(strptime(thisDate, '%m/%d/%Y')))
        thisNews = ""

        if ( row['Publish'] == 'Yes' ):
            if (row['Alternative_Text'] == ''):
                thisNews = "* (" + row['Link'] + ")[" + row['Title'] + "]\n"
            else:
                thisNews = "* " + row['Alternative_Text'] + "\n"

        if longDate in ourNews:
            minCounter += 1
            longDate = longDate + timedelta(minutes=minCounter)

        ourNews[longDate] = thisNews

    latestCounter = 0

    for key in sorted(ourNews.keys(), reverse=True):
        if ( latestCounter < 5 ):
            latestNews.write(ourNews[key])
            latestCounter += 1

        allNews.write(ourNews[key])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='Ouput Directory', default='/tmp')
    args = parser.parse_args()
    gc = oauthLogin()
    #extractEvents(gc, args.d)
    extractNews(gc, args.d)
