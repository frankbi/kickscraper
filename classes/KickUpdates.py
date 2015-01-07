#!/usr/bin/python

import requests
from bs4 import BeautifulSoup

import re

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