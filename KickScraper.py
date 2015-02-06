#!/usr/bin/python

from __future__ import division
from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup

import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class KickScraper:

	def __init__(self, path):
		self.stats = KickStats(path)
		self.comments = KickComments(path)
		self.updates = KickUpdates(path)


class KickHelper:
	
	def convert_time(self, date, zone):
		dateFormat = "%Y-%m-%dT%H:%M:%S"
		time = datetime.strptime(date, dateFormat)
		return {
			"date": time.strftime("%m/%d/%Y"),
			"time": time.strftime("%H:%M:%S"),
			"zone": zone.replace(":","")
		}


class KickUpdates:

	def __init__(self, path):
		r = requests.get(path + "posts")
		tree = BeautifulSoup(r.text)
		self.all_data = self.get_updates(tree, path)

	def get_post_id(self, tree):
		text = tree.find("p", attrs={"class":"update-number"}).get_text().strip()
		return (re.search(r"#\d{1,4}", text).group())[1:]

	def get_post_time(self, tree):
		dateString = tree.find("time")["datetime"]
		return KickHelper().convert_time(dateString[:-6], dateString[-6:])

	def get_post_title(self, tree):
		title = tree.find("h2", attrs={"class":"normal title"})
		return (title.a.string).replace(u"\u2019","'").replace(u"\u2014","-")

	def get_post_comments_total(self, tree):
		statLine = tree.find("div", attrs={"class":"statline"})
		commentText = statLine.find("a", attrs={"class":"comments"})
		try:
			postComments = str(commentText.get_text())
			if postComments.find(" ") is not -1:
				return int(postComments[:postComments.find(" ")])
			else:
				return 0
		except:
			'''
			idk
			/1507621537/tlc-is-back-to-make-our-final-album-with-you/
			'''
			print commentText

	def get_post_likes(self, tree):
		text = tree.find("span", attrs={"class":"count"}).get_text()
		if text.find(" ") is not -1:
			return int(text[:text.find(" ")])
		else:
			return 0

	def get_post_url(self, tree):
		title = tree.find("h2", attrs={"class":"normal title"})
		return title.a["href"]

	def get_update_content(self, pageNum, path):
		payload = {"page":pageNum}
		r = requests.get(path + "posts", params=payload)
		tree = BeautifulSoup(r.text)
		postsOnThisPage = []
		for post in tree.findAll("div", attrs={"class":"project_post_summary"}):
			postsOnThisPage.append({
				"post_id": self.get_post_id(post),
				"post_time": self.get_post_time(post),
				"post_title": self.get_post_title(post),
				"post_comments": self.get_post_comments_total(post),
				"post_likes": self.get_post_likes(post),
				"post_url": self.get_post_url(post)
			})
		return postsOnThisPage

	def get_updates(self, tree, path):
		paginationLinks = tree.find("div", attrs={"class":"pagination"})
		if paginationLinks is None:
			return self.get_update_content(1, path)
		else:
			allPaginationLinks = []
			[allPaginationLinks.append(link["href"]) for link in paginationLinks.findAll("a")]
			sortedListOfPages = [int(page[page.find("=")+1:]) for page in allPaginationLinks]
			allUpdates = []
			for x in range(1, max(sortedListOfPages) + 1):
				for i in self.get_update_content(x, path):
					allUpdates.append(i)
			return allUpdates


class KickComments:

	def __init__(self, path):
		r = requests.get(path)
		tree = BeautifulSoup(r.text)
		self.all_data = []

		numberOfComments = int(tree.find("span", 
			attrs={"id":"comments_count"})["data-comments-count"])

		if numberOfComments > 0:
			self.all_data = self.get_comments(tree, path, numberOfComments)

	def get_comment_text(self, tree):
		return "\n".join([p.get_text() for p in tree.findAll("p")])

	def get_comment_date(self, tree):
		dateString = tree.find("data")["data-value"]
		return KickHelper().convert_time(dateString[:-6], dateString[-6:])

	def get_comment_author(self, tree):
		return tree.find("a", attrs={"class":"author"}).get_text()

	def get_comment_author_url(self, tree):
		return tree.find("a", attrs={"class":"author"})["href"]

	def get_creator_comment(self, array):
		creatorComment = False;
		if array[1].find("creator") > 0:
			creatorComment = True
		return creatorComment

	def get_comment_attributes(self, comment):
		return [comment.get_attribute("innerHTML"), comment.get_attribute("class")]

	def get_comment_content(self, commentsArray):
		tree = BeautifulSoup(commentsArray[0].strip())
		return {
			"comment_text": self.get_comment_text(tree),
			"comment_date": self.get_comment_date(tree),
			"comment_author": self.get_comment_author(tree),
			"comment_author_url": self.get_comment_author_url(tree),
			"creator_comment": self.get_creator_comment(commentsArray)
		}

	def get_comments(self, tree, path, numComments):
		numberOfClicksNeeded = (numComments / 50)
		if numberOfClicksNeeded > int(numberOfClicksNeeded):
			numberOfClicksNeeded + 1
		driver = webdriver.PhantomJS()
		driver.get(path + "comments")
		try:
			showMoreComments = driver.find_element_by_class_name("older_comments")
			for x in range(int(numberOfClicksNeeded)):
				showMoreComments.click()
				print "clicked #" + str(x)
				time.sleep(1)
		except NoSuchElementException:
			pass
		allCommentObjects = driver.find_elements_by_class_name("NS_comments__comment")
		allCommentsStructure = [self.get_comment_attributes(comment) for comment in allCommentObjects]
		allComments = []
		for idx, x in enumerate(allCommentsStructure):
			print "processing #" + str(idx)
			allComments.append(self.get_comment_content(x))
		driver.close()
		return allComments


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

	# can be improved
	def get_project_title(self, tree):
		return (tree.find("title").string).replace(u"\u2019","'").replace(u"\u2014","-")

	# can be improved
	def get_short_description(self, tree):
		return tree.find("p", attrs={"class":"h3 mb3"}).get_text().replace(u"\n","")

	def get_creator_name(self, tree):
		return tree.find("a", attrs={"data-modal-class":"modal_project_by"}).get_text()

	def get_pledge_amount(self, tree):
		pledgeObject = tree.find("div", attrs={"id":"pledged"})
		return {
			"current_type": pledgeObject.data["data-currency"].lower(),
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
			"currency_type": currency_type.lower(),
			"pledge_goal": pledge_goal
		}

	def get_duration(self, tree):
		return int(float(tree.find("span", attrs={"id":"project_duration_data"})["data-duration"]))

	# can be improved
	def get_location(self, tree):
		return (tree.find("a", attrs={"class":"grey-dark mr3 nowrap"})).get_text().strip()

	# can be improved
	def get_category(self, tree):
		allOfIt = tree.findAll("a", attrs={"class":"grey-dark mr3 nowrap"})
		return allOfIt[1].get_text().strip()

	def get_scrape_date(self):
		return {
			"date": time.strftime("%m/%d/%Y"),
			"time": time.strftime("%H:%M:%S"),
			"zone": time.strftime("%z")
		}

	# get_status helper
	def get_status_funding_deadline(self, tree):
		fundingHTML = tree.find("div", 
			attrs={"class":"NS_projects__deadline_copy"}).div["data-render"]
		pattern = re.compile(r'(\w{3})\s(\d{2}|\d{1})\s(\d{4})\s(\d{1}|\d{2}):(\d{2})\s(\w{2})\s(\w{3})')
		soup = BeautifulSoup(re.sub(r'\\n|\\', "", fundingHTML[1:-1]))

		return re.search(pattern, soup.get_text()).group()

	# get_status helper
	def get_status_funding_status(self, tree):
		if (len(tree.findAll("a", attrs={"id":"button-back-this-proj"}))) > 0:
			return "funding_open"
		else:
			status = tree.find("div", attrs={"class":"border-left-thick"}).h3.get_text()
			if "funded" in status.lower():
				return "funding_complete"
			if "unsuccessful" in status.lower():
				return "funding_failed"

	# get_status helper
	def get_status_funding_percent(self, tree):
		raised = self.get_pledge_amount(tree)
		goal = self.get_pledge_goal(tree)
		return raised["pledge_amount"] / goal["pledge_goal"]

	# get_full_description_characters helper
	def count_characters(self, text):
		return len(text) - text.count(' ')

	def get_full_description_characters(self, tree):
		description_body = tree.find("div", attrs={"class":"NS_projects__description_section"})
		column = description_body.find("div", attrs={"class":"col col-8"})
		sections = column.findAll("div", attrs={"class":"mb6"})
		total_character_count = 0
		for sec in sections:
			num_characters = self.count_characters(sec.get_text().strip())
			total_character_count = total_character_count + num_characters
		return total_character_count

	def get_status(self, tree):
		return {
			"funding_status": self.get_status_funding_status(tree),
			"funding_deadline": self.get_status_funding_deadline(tree),
			"funding_percent": self.get_status_funding_percent(tree)
		}

	def get_stats(self, tree, path):
		return {
			"project_title": self.get_project_title(tree),
			"project_short_description": self.get_short_description(tree),
			"project_category": self.get_category(tree),
			"pledge_duration": self.get_duration(tree),
			"pledge_location": self.get_location(tree),
			"pledge_amount": self.get_pledge_amount(tree),
			"pledge_goal": self.get_pledge_goal(tree),
			"creator_name": self.get_creator_name(tree),
			"num_updates": self.get_num_updates(tree),
			"num_comments": self.get_num_comments(tree),
			"backers_count": self.get_backers_count(tree),
			"scrape_date": self.get_scrape_date(),
			"status": self.get_status(tree),
			"product_description_character_count": self.get_full_description_characters(tree)
		}