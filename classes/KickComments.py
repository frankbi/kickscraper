#!/usr/bin/python

from __future__ import division
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import requests
from bs4 import BeautifulSoup

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