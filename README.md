# scumlogs for webservice (for python v3.7)
forked from gamebotland and edited for send logs to web service by Behçet Atalay.

is incremental, adds new lines to last updated files and create new ones from last execution

created to keep a backup of the server logs in local

run once to generate a new ini file, edit ini file and complete gportal data

edit the webserviceurl in the configuration file yourself.
when sending logs using the log name, 
for example:

	webserviceurl = https://example.com/webapi/
	Sends login logs to https://example.com/webapi/login
	Sends kill logs to https://example.com/webapi/kill
	Sends admin logs to https://example.com/webapi/admin
	Sends chat logs to https://example.com/webapi/chat
	Sends violations logs to https://example.com/webapi/violations
	also post as logLine, example php to get the post: $_POST['logLine']


when you access your gportal server you can see serverid value in url: https://www.g-portal.com/en/scum/status/XXXXXX

- for gportal international set: gportal_loc = com
- for gportal us set: gportal_loc = us

include in crontab or in windows task manager to run periodicaly

Instructions

	Install python 3.7.4 on your system
	Download all files and decompress in a folder
		
	pip install -r requirements.txt
	
	Run scumlogs:
		python scumlogs.py
	
