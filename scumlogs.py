# -*- coding: utf-8 -*-
# Sending scum server logs in G-portal to web service
# by TechnoBeceT

import json
import re
import asyncio

import aiohttp

from bs4 import BeautifulSoup
import cfscrape
from configparser import RawConfigParser
from datetime import datetime


def log(text):
    print('[%s] %s' % (datetime.strftime(datetime.now(), '%H:%M:%S'), text))


def help():
    print('\nPlease edit scumlogs.ini and include your g-portal credentials, use:')
    print('  user = gportal email or username')
    print('  password = gportal password')
    print('  serverid = gportal server id')
    print('  loc = com (for gportal international) or us (for gportal us)')
    print('  folder = blank for local or path folder to store your log files')
    print('  leave the rest of the parameters as is\n')


def loadConfigini():
    config = RawConfigParser()
    with open('scumlogs.ini', 'r', encoding="utf-8") as f:
        config.read_file(f)
    global configini
    configini = dict(config['GPORTAL'])


def saveConfigini():
    parser = RawConfigParser()
    parser.add_section('GPORTAL')
    for key in configini.keys():
        parser.set('GPORTAL', key, configini[key])
    with open('scumlogs.ini', 'w', encoding="utf-8") as f:
        parser.write(f)


async def sendToServer(line, wsFunction):
    values = (
    'user', 'password', 'serverid','webserviceurl', 'loc', 'folder', 'admin_file', 'admin_line', 'chat_file', 'chat_line', 'kill_file',
    'kill_line', 'login_file', 'login_line', 'violations_file', 'violations_line')
    try:
        loadConfigini()
    except:
        global configini
        configini = {}
    data = {
        "logLine": line
    }
    headers = {
        'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/45.0.2454.101 Safari/537.36'),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(configini['webserviceurl'] + wsFunction, headers=headers, data=data) as resp:
            log(await resp.json())


async def read_logins(syncTarget):
    values = (
    'user', 'password', 'serverid','webserviceurl', 'loc', 'folder', 'admin_file', 'admin_line', 'chat_file', 'chat_line', 'kill_file',
    'kill_line', 'login_file', 'login_line', 'violations_file', 'violations_line')
    print('scumlogs v1.0, scum server logs downloader from gportal\nby htttps://GAMEBotLand.com')
    try:
        loadConfigini()
    except:
        global configini
        configini = {}
    for value in values:
        if value not in configini:
            configini[value] = ''
    if configini['folder'] != '':
        if configini['folder'][-1:] != '/' and configini['folder'][-1:] != '\\':
            configini['folder'] = configini['folder'] + '/'
    saveConfigini()

    if configini['loc'] == 'com':
        loc = 'com'
    else:
        loc = 'us'
    URL_LOGIN = 'https://id2.g-portal.com/login?redirect=https://www.g-portal.{0}/auth/login?redirectAfterLogin=https://www.g-portal.{0}/es/'.format(configini['loc'])
    URL_LOGS = 'https://www.g-portal.{0}/server/scum/{1}/logs'.format(configini['loc'], configini['serverid'])
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}

    with cfscrape.create_scraper() as session:
        try:
            log('connecting g-portal...')
            payload = {'_method': 'POST', 'login': configini['user'], 'password': configini['password'],
                       'rememberme': 1}
            raw_response = session.post(URL_LOGIN, headers=headers, data=payload)
            raw_response = session.get(URL_LOGS, headers=headers)
            response = raw_response.text
            html = BeautifulSoup(response, 'html.parser')
            select = html.find('div', {'class': 'wrapper logs'})
            logList = select['data-logs']
            logs = json.loads(logList)

            for i in range(len(logs)):
                getid = logs["file_" + str(i + 1)]
                id = (getid[int(getid.find('Logs')) + 5:])
                type = id.split('_')[0]

                if type == syncTarget:
                    if configini[type + '_file'] != '':
                        if id < configini[type + '_file']:
                            continue
                    payload = {'_method': 'POST', 'load': 'true', 'ExtConfig[config]': getid}
                    raw_response = session.post(URL_LOGS, headers=headers, data=payload)
                    response = raw_response.text
                    content = json.loads(response)
                    lines = content["ExtConfig"]["content"].splitlines()
                    filename = configini['folder'] + id
                    file = open(filename, "a+", encoding='utf-8')
                    found = False
                    writing = False
                    for line in lines:
                        if id == configini[type + '_file'] and not found:
                            if line == configini[type + '_line']:
                                found = True
                                continue
                        else:
                            file.write(line + '\n')
                            table = id.split('_')
                            table_1 = table[0]
                            if table_1 == 'admin':
                                await sendToServer(line, 'admin')
                            if table_1 == 'chat':
                                await sendToServer(line, 'chat')
                            if table_1 == 'kill':
                                await sendToServer(line, 'kill')
                            if table_1 == 'login':
                                await sendToServer(line, 'login')
                            if table_1 == 'violations':
                                await sendToServer(line, 'violations')
                            writing = True
                    if writing:
                        if found:
                            log('updating {}'.format(id))
                        else:
                            log('creating {}'.format(id))
                    file.close()
                    configini[type + '_file'] = id
                    configini[type + '_line'] = lines[-1]
                else:
                    continue

            saveConfigini()
        except Exception as e:
            print(e)
            log('error connecting, check connectivity and scumlogs.ini')
            help()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_logins('login'))
    loop.run_until_complete(read_logins('kill'))
    loop.run_until_complete(read_logins('admin'))
    loop.run_until_complete(read_logins('chat'))
    loop.run_until_complete(read_logins('violations'))
    loop.close()
