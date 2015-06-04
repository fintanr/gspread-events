#!/usr/bin/python
#
# an events calender cheat app, use a simple google spreadsheet
# to keep track of events, and generate a yaml file of past
# and future events for use later in Jekyll
#
# we also pull a news feed from the same doc
#

import gspread
import os
import argparse
import markdown
import re
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

    _checkDirs(outDir)

    today = str(date.today().strftime('%-m/%-d/%Y'))
    allVals = ws.get_all_records()

    upcomingEventsYAML = outDir + "/_data/eventsdata.yml"
    pastEventsYAML = outDir + "/_data/pasteventsdata.yml"

    upcoming = open(upcomingEventsYAML, "w")
    past = open(pastEventsYAML, "w")

    for row in allVals:
        thisDate = row['Date']

        if ( row['Publish'] == 'Yes' ):
            thisEvent = "- title:" + row['Title'] + "\n"
            thisEvent += "  dateandloc: " + row['Location'] + "," + row['Long Date String'] + "\n"
            thisEvent += "  url: " +  row['Link'] + "\n\n"

            if ( thisDate >= today ):
                upcoming.write(thisEvent)
            else:
                past.write(thisEvent)

def extractNews(gc, outDir):
    sh = gc.open(os.environ['EVENTS_SHEET'])
    ws = sh.worksheet("News")

    _checkDirs(outDir)

    allVals = ws.get_all_records()

    allNewsYAML = outDir + "/_data/allnewsdata.yml"
    latestNewsYAML = outDir + "/_data/newsdata.yml"

    allNews = open(allNewsYAML, "w")
    latestNews = open(latestNewsYAML, "w")

    ourNews = dict()
    minCounter = 0

    for row in allVals:
        thisDate = row['Date']
        longDate = datetime.fromtimestamp(mktime(strptime(thisDate, '%m/%d/%Y')))
        thisNews = ""

        if ( row['Publish'] == 'Yes' ):
            if (row['Alternative_Text'] == ''):
                thisNews = "- title: " + row['Title'] + "\n"
                thisNews += "  url: " + row['Link'] + "\n"
                thisNews += "  alternative: \n\n"
            else:
                # we need to parse out the markdown..
                altText = markdown.markdown(row['Alternative_Text'])
                # and markdown adds <p> ... </p> per spec, we need to remove
                # theses
                altTextClean = re.search('<p>(.*)</p>', altText, re.IGNORECASE)
                thisNews = "- title:\n"
                thisNews += "  url:\n"
                thisNews += "  alternative: " + altTextClean.group(1) + "\n\n"

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

def _checkDirs(outDir):
    dataDir = outDir + "/_data"

    if ( not os.path.isdir(outDir) ):
        print "Outdir %s not found" % outDir
        exit(1)

    if ( not os.path.isdir(dataDir) and ( outDir == '/tmp') ):
        os.mkdir(dataDir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='Output Directory, defaults to /tmp', default='/tmp')
    args = parser.parse_args()
    gc = oauthLogin()
    extractEvents(gc, args.d)
    extractNews(gc, args.d)
