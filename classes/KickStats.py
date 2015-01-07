#!/usr/bin/python

import re

import requests
from bs4 import BeautifulSoup

class KickStats:

	def __init__(self, path):
		r = requests.get(path)
		tree = BeautifulSoup(r.text)
		self.all_data = self.get_stats(tree, path)

	def get_num_updates(self, tree):
		return int(tree.find("a", attrs={"id":"updates_nav"})["data-updates-count"])

	def get_num_comments(self, tree):
		return int(tree.find("span", attrs={"id":"comments_count"})["data-comments-count"])

	def get_backers_count(self, tree):
		return int(tree.find("div", attrs={"id":"backers_count"}).get_text().replace(",",""))

	def get_project_title(self, tree):
		return tree.find("title").string

	def get_creator_name(self, tree):
		return tree.find("a", attrs={"data-modal-class":"modal_project_by"}).get_text()

	def get_pledge_amount(self, tree):
		pledgeObject = tree.find("div", attrs={"id":"pledged"})

		return {
			"current_type": pledgeObject.data["data-currency"],
			"pledge_amount": int(re.sub(r'(\.|,)', "", pledgeObject.get_text().strip()[1:]))
		}

	def get_pledge_goal(self, tree):
		contents = tree.find("span", attrs={"class":"no-code"})

		pledge_goal = int(re.sub(r'(\.|,)', "", contents.get_text()[1:]))

		classNames = re.search(re.compile(r'(money\s(\w{3})\sno-code)'), 
			str(contents)).group()

		if classNames is not None:
			currency_type = classNames.split(" ")[1]

		return {
			"currency_type": currency_type,
			"pledge_goal": pledge_goal
		}


	def get_status(self, tree):
		fundingHTML = tree.find("div", 
			attrs={"class":"NS_projects__deadline_copy"}).div["data-render"]

		pattern = re.compile(r'(\w{3})\s(\d{2}|\d{1})\s(\d{4})\s(\d{1}|\d{2}):(\d{2})\s(\w{2})\s(\w{3})')
		soup = BeautifulSoup(re.sub(r'\\n|\\', "", fundingHTML[1:-1]))

		return re.search(pattern, soup.get_text()).group()

	def get_stats(self, tree, path):

		return {
			"project_title": self.get_project_title(tree),
			"creator_name": self.get_creator_name(tree),
			"backers_count": self.get_backers_count(tree),
			"pledge_amount": self.get_pledge_amount(tree),
			"pledge_goal": self.get_pledge_goal(tree),
			"num_updates": self.get_num_updates(tree),
			"num_comments": self.get_num_comments(tree),
			"status_string": self.get_status(tree)
		}