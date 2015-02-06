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

url = "https://www.kickstarter.com/projects/137857383/older-than-recorded-history-pens-made-from-ancient/"

scraper = KickScraper(url)

with open("stats.json", "w") as outfile:
	json.dump(scraper.stats.all_data, outfile, sort_keys=True, indent=4)

with open("updates.json", "w") as outfile:
	json.dump(scraper.updates.all_data, outfile, sort_keys=True, indent=4)

with open("comments.json", "w") as outfile:
	json.dump(scraper.comments.all_data, outfile, sort_keys=True, indent=4)