from datetime import datetime, timedelta, timezone
import discord

import requests

class CtfTimeEvents:
    def __init__(self, start=None, finish=None):
        self.a = 1

        self.baseUrl = 'https://ctftime.org/api/v1/events/'
        self.payload = {
            'limit': 999,
            'start': int(datetime.now(timezone.utc).timestamp()),
            'finish': int((datetime.now(timezone.utc)+timedelta(weeks=2)).timestamp())
        }
        self.headers = {
            'User-Agent': 'HackPack Bot/1.0.0'
        }

        self.attempts = 0
        self.currentList = []
        self.currentIndex = 0
        self.set_up_ctf_embed_list()

    def current(self):
        return self.currentList[self.currentIndex]

    def next(self):
        self.currentIndex += 1
        if (len(self.currentList) == self.currentIndex):
            self.payload['start'] = self.payload['finish']
            self.payload['finish'] = self.get_timestamp_plus_weeks(self.payload['finish'], 2)
            if not self.set_up_ctf_embed_list():
                return self.next()
        return self.currentList[self.currentIndex]

    def prev(self):
        self.currentIndex -= 1
        if (self.currentIndex < 0):
            self.payload['finish'] = self.payload['start']
            self.payload['start'] = self.get_timestamp_plus_weeks(self.payload['finish'], -2)
            if not self.set_up_ctf_embed_list():
                return self.prev()
        return self.currentList[self.currentIndex]

    def set_up_ctf_embed_list(self):
        response_json = requests.get(self.baseUrl, headers=self.headers, params=self.payload).json()
        self.currentIndex = 0
        self.currentList = self.parse_json(response_json)
        if len(self.currentList) == 0:
            if self.attempts == 5:
                raise Exception("No CTF's found in the past 5 attempted retrievals")
            self.attempts += 1
            return False
        
        self.attempts = 0
        return True

    def parse_json(self, json):
        ctf_embeds = []
        for ctf in json:
            organizer_name = ctf['organizers'][0]['name']
            ctf_url = ctf['ctftime_url']
            ctf_format = ctf['format']
            logo_url = ctf['logo']
            ctf_title = ctf['title']
            ctf_desc = ctf['description']
            ctf_start = ctf['start']

            embed_var = discord.Embed(title=ctf_title, description=ctf_desc, url=ctf_url)

            embed_var \
                .set_author(name=organizer_name, icon_url=logo_url) \
                .add_field(name="Format", value=ctf_format, inline=True) \
                .add_field(name="Starts: ", value=datetime.fromisoformat(ctf_start).strftime("%m/%d/%Y, %H:%M"))

            ctf_embeds.append(embed_var)

        return ctf_embeds

    def get_timestamp_plus_weeks(self, timestamp, num_weeks):
        return int((datetime.fromtimestamp(timestamp)+timedelta(weeks=num_weeks)).timestamp())