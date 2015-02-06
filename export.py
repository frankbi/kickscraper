#!/usr/bin/python

from KickScraper import KickScraper
import csv
import json


url = "https://www.kickstarter.com/projects/713023302/socrates-the-most-clever-socks-ever/"

scraper = KickScraper(url)


with open("stats.json", "w") as outfile:
	json.dump(scraper.stats.all_data, outfile, sort_keys=True, indent=4)

with open("updates.json", "w") as outfile:
	json.dump(scraper.updates.all_data, outfile, sort_keys=True, indent=4)

with open("comments.json", "w") as outfile:
	json.dump(scraper.comments.all_data, outfile, sort_keys=True, indent=4)