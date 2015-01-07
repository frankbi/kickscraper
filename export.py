#!/usr/bin/python

from KickScraper import KickScraper
import csv
import json

'''
with open("test_pages.csv", "rU") as f:
	f_reader = csv.reader(f)
	for idx, x in enumerate(f_reader):
		scraper = KickScraper(x[0])
'''

scraper = KickScraper("https://www.kickstarter.com/projects/692895003/succumb-gender-neutral-self-care-and-sensual-body/")

with open("stats.json", "w") as outfile:
	json.dump(scraper.stats.all_data, outfile, sort_keys=True, indent=4)

with open("updates.json", "w") as outfile:
	json.dump(scraper.updates.all_data, outfile, sort_keys=True, indent=4)

with open("comments.json", "w") as outfile:
	json.dump(scraper.comments.all_data, outfile, sort_keys=True, indent=4)