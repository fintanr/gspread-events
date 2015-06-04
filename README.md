# GSpread Events

Read Events from a Google Spreadsheet and generate a yaml file.

You need to have a google apps account setup which has access to the
spreadsheet you are writing too, and the spreadsheet itself needs 
an Events and News worksheet, with columns as detailed below 

| **Worksheet** |**Columns** |
| ------------- | ---------- |
| Events	| Date, Participation, Publish, Long Date String, Title, Location, Link |
| News		| Date, Publish, Title, Link, Alternative_Text |

Publish is always Yes or No.

Set the environment variables as

```
GOOGLE_KEY=<path/to/key>
GOOGLE_EMAIL=<some-prefix>@developer.gserviceaccount.com
EVENTS_SHEET=Name_of_Spreadsheet
```

and then just call the script. Default output is to /tmp, use -d <outdir>
for an alternative directory.

There will be four yaml files generated

* allnewsdata.yml		
* newsdata.yml		
* eventsdata.yml		
* pasteventsdata.yml

## Using in Jekyll

The yaml files can be used by jekyll. Assuming these files end up in your
_data directory, you can use them with [liquid](http://jekyllrb.com/docs/templates/).

i.e. for events listing we use 

``` html
{% for event in site.data.eventsdata %}
	<li><a href="{{ event.url }}" {% if event.url contains 'http' %}target="_blank"{% endif %}>{{ event.title }}</a>, {{ event.dateandloc }}</li>
  {% endfor %}
```

## Dependencies

* [gspread](https://github.com/burnash/gspread)
* [oauth2client](https://github.com/google/oauth2client)
* [markdown](https://pypi.python.org/pypi/Markdown)

