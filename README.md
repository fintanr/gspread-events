# GSpread Events

Read Events from a Google Spreadsheet and generate a markdown file.

You need to have a google apps account setup which has access to the
spreadsheet you are writing too, and the spreadsheet itself needs 
an Events and News worksheet, with columns as detailed below 

**Worksheet**|**Columns**
Events|Date, Participation, Publish, Long Date String, Title, Location, Link
News|Date, Publish, Title, Link, Alternative_Text

Publish is always Yes or No.

Set the environment variables as

```
GOOGLE_KEY=<path/to/key>
GOOGLE_EMAIL=<some-prefix>@developer.gserviceaccount.com
EVENTS_SHEET=Name_of_Spreadsheet
```

and then just call the script. Default output is to /tmp, use -d <outdir>
for an alternative directory.

There will be four markdown files generated

* AllNews.md
* LatestNews.md
* PastEvents.md
* UpcomingEvents.md

## Dependencies

* [gspread](https://github.com/burnash/gspread)
* [oauth2client](https://github.com/google/oauth2client)
