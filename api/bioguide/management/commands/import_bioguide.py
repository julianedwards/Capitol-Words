import csv
import sys
import urllib2

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from bioguide.models import Legislator

import name_tools
from BeautifulSoup import BeautifulSoup


class Command(BaseCommand):
    def handle(self, *args, **options):
        fields = ['bioguide_id', 'name', 'birth_death', 'position', 'party', 'state', 'congress', ]

        if args:
            congress = args[0]
        else:
            congress = 111

        data = 'lastname=&firstname=&position=&state=&party=&congress=%s' % str(congress)
        url = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req).read()

        soup = BeautifulSoup(response)

        for row in soup.findAll('tr')[2:]:
            cells = row.findAll('td')
            if len(cells) != 6:
                continue

            try:
                name = cells[0].find('a').renderContents()
                bioguide_id = cells[0].find('a')['href'].split('=')[-1]

                birth_death, position, party, state, congress = [x.renderContents() for x in cells[1:]]
                congress = congress.split('<br />')[0]

                data = {'bioguide_id': bioguide_id,
                        'birth_death': birth_death,
                        'position': position,
                        'party': party,
                        'state': state,
                        'congress': congress, }

                data['prefix'], data['first'], data['last'], data['suffix'] = name_tools.split(name)
                print data
            except Exception, e:
                print Exception, e

            try:
                legislator = Legislator.objects.create(**data)
            except IntegrityError:
                continue