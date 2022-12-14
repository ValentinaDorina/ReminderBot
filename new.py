from __future__ import print_function

import os.path
from telegram import ParseMode
from google.auth.transport.requests import Request

import datetime
import time
from googleapiclient.errors import HttpError
import telegram as telegram
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import config
import telebot
import schedule
from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient import discovery


SCOPES = 'https://www.googleapis.com/auth/calendar'
TOKEN = '5720580673:AAE0B84CqzcHewcIVrInhrpbA4g8VLd8Yvo'

bot = telebot.TeleBot(token=TOKEN)


def main():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        now_1day = round(time.time()) + 86400  # плюс сутки
        now_1day = datetime.datetime.fromtimestamp(now_1day).isoformat() + 'Z'

        print('Берем 100 событий')
        eventsResult = service.events().list(
            calendarId='cc5bacdad3c72cf5f609e9f928594cc40ab560ce3e9905127dcb87a57c8eb7a4@group.calendar.google.com',
            timeMin=now, timeMax=now_1day, maxResults=100, singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            print('нет событий на ближайшие сутки')
            main.bot.sendMessage('920750557', 'нет событий на ближайшие сутки')
        else:
            msg = '<b>События на ближайшие сутки:</b>\n'
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, ' ', event['summary'])
                if not event['description']:
                    print('нет описания')
                    ev_desc = 'нет описания'
                else:
                    print(event['description'])
                    ev_desc = event['description']

                    ev_title = event['summary']
                    cal_link = '<a href="/%s">Подробнее...</a>' % event['htmlLink']
                    ev_start = event['start'].get('dateTime')
                print(cal_link)
                msg = msg + '%s\n%s\n%s\n%s\n\n' % (ev_title, ev_start, ev_desc, cal_link)
                print('===================================================================')
            bot.send_message('920750557', msg, parse_mode='html')

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()

