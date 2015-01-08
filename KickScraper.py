#!/usr/bin/python

from __future__ import division
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


class KickUpdates:

	def __init__(self, path):
		r = requests.get(path + "posts")
		tree = BeautifulSoup(r.text)
		self.all_data = self.get_updates(tree, path)

	def get_post_id(self, tree):
		text = tree.find("p", attrs={"class":"update-number"}).get_text().strip()
		return (re.search(r"#\d{1,4}", text).group())[1:]

	def get_post_time(self, tree):
		return tree.find("time")["datetime"]

	def get_post_title(self, tree):
		title = tree.find("h2", attrs={"class":"normal title"})
		return title.a.string

	def get_post_comments_total(self, tree):
		statLine = tree.find("div", attrs={"class":"statline"})

		commentText = str(statLine.find("span", attrs={"class":"comments"}))

		try:
			return re.search(r'(\d{1,4})', commentText).group()
		except:
			return 0

	def get_post_likes(self, tree): # ''' simplify '''
		return tree.find("span", attrs={"class":"count"}).get_text()

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
		return tree.find("data")["data-value"]

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
				time.sleep(1)
		except NoSuchElementException:
			pass

		allCommentObjects = driver.find_elements_by_class_name("NS_comments__comment")
		allCommentsStructure = [self.get_comment_attributes(comment) for comment in allCommentObjects]
		allComments = []

		for x in allCommentsStructure:
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