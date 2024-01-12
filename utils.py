import csv
import json
import openreview

from constants import *

def csv_to_dict(filename, delimiter=','):
    with open(filename, 'r', newline='') as csvfile:
        lines = list(csv.reader(csvfile))

        # Exclude header
        header = set(lines[0])
        lines = lines[1:]

        raw = False
        if 'TurkerId' in header:
            raw = True

        dataset = {}
        for entry in lines:
            if raw:
                review, sentence, turker, *args = entry
            else:
                review, sentence, *args = entry

csv_to_dict('raw_annotated_data.csv')

class Review:
    def __init__(self) -> None:
        self.client = openreview.Client(
            baseurl='https://api.openreview.net', 
            username=USERNAME, 
            password=PASSWORD
        )
        self.all_reviews = self.scrape_all_reviews()
    
    def get_venues(self, filter=''):
        venues = []
        for venue in self.client.get_group(id='venues').members:
            if filter in venue:
                venues.append(venue)
        return venues
    
    def scrape_all_reviews(self):
        reviews = {}
        titles = {}

        venues = self.get_venues(filter='Conference')

        for venue in venues:
            sub_reviews, sub_titles = self.scrape_reviews(venue)

            reviews.update(sub_reviews)
            titles.update(sub_titles)

        return reviews, titles
    def scrape_reviews(self, venue='ICLR.cc/2019/Conference'):
        reviews = {}
        titles = {}

        invitation = venue+'/-/Blind_Submission'
        notes = openreview.tools.iterget_notes(self.client, invitation=invitation, details='directReplies')

        for note in notes:
            content = note.content
            title = content['title']
            reviews[title] = []

            replies = note.details['directReplies']
            for reply in replies:
                reviews[title].append(reply['content'])
                titles[title] = content

        return reviews, titles
    
    def get_reviews(self):
        return self.all_reviews

reviewer = Review()
reviews, titles = reviewer.scrape_reviews()

with open("ICLR_titles.json", "w") as outfile: 
    json.dump(titles, outfile)

with open("ICLR_reviews.json", "w") as outfile: 
    json.dump(reviews, outfile)

all_reviews, all_titles = reviewer.scrape_all_reviews()

with open("all_titles.json", "w") as outfile: 
    json.dump(all_titles, outfile)

with open("all_reviews.json", "w") as outfile: 
    json.dump(all_reviews, outfile)