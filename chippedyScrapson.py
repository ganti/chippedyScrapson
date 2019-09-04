#!/usr/bin/env python3


import os
import sys
from pprint import pprint
import csv
import json, codecs
import time
import random

import requests
from lxml import html
from scrapy import Selector
from bs4 import BeautifulSoup

allURLs = []

def main():
	url = "https://www.tagesanzeiger.ch"
	depth = 3

	makeListTxtFromURL(url, depth=depth)

	call = "python3 ./webscreenshot/webscreenshot.py -i list.txt -v --workers 7"
	#
	#	webscreenshot has many params: screensize, browser etc.
	#   all arguments of webscreenshot.py are in ./webscreenshot/00_help_webscreenshot.txt
	#
	os.system(call)





def makeListTxtFromURL(url, depth=5):
	global allURLs
	domain = url.split("://")[0]+"://" + url.split("://")[1].split("/")[0] 
	with open('list.txt', 'w') as file:
		file.write("")
	with open('url_error.txt', 'w') as file:
		file.write("")

	allURLs = getExtractAllLinksFromPage(url, domain, depth)
	#pprint(allURLs)
	allURLs = [url] + allURLs
	allURLs = list(set(allURLs))
	with open('list.txt', 'w') as file:
		for row in allURLs:
		    file.write(row +"\n")
    
def getExtractAllLinksFromPage(url, domain, depth):
	global allURLs
	result = []
	if depth >= 1 and domain in url:
		content = getPageContentOfURL(url)		
		if content != None:
			contentLinks = getLinksFromPageContent(content, domain)
			result = result + contentLinks
			depth = depth -1
			for link in contentLinks:
				#print(str(depth)+" "+link)
				sublinks = getExtractAllLinksFromPage(link, domain, depth)
				for sublink in sublinks:
					if not sublink in allURLs:
						result.append(sublink)
			result = list(set(result))
			allURLs = allURLs + result
	return result
		
def getLinksFromPageContent(content, domain):
	global allURLs
	links = []
	bs = BeautifulSoup(content, features="lxml")
	for link in bs.findAll('a'):
		links.append(link.get('href'))
	result = []
	for link in links:
		addToList = True
		if not link is None:
			ignoreStartWith = ['javascript:', 'mailto:']
			ignoreEndsWith = ['.pdf', '.zip', '.png', '.jpg', '.gif']
			for ignorePraefix in ignoreStartWith:
				if link.startswith(ignorePraefix):
					addToList = False
			for ignoreSuffix in ignoreEndsWith:
				if link.endswith(ignoreSuffix):
					addToList = False
			if addToList == True:
				if link.startswith('//'):
					link = domain.split("://")[0]+link
				if link.startswith('/'):
					link = domain+link
				if domain in link and not link in allURLs:
					result.append(link)
				addToList = False
	result = list(set(result))
	allURLs = allURLs + result
	return result

def getPageContentOfURL(url, run=3):
	content = None
	try:
		page = requests.get(url)
		if page.status_code != 200:
			print(str(page.status_code) +" 💩 " + url)
		else:
			print(str(page.status_code) +" ✅ " + url)
			content = page.content
	except requests.exceptions.RequestException:
		content = getPageContentOfURL(url, run=(run-1))
		if content == None and run == 0:
			with open('url_error.txt', 'a') as file:
				file.write(url+"\n")
			content = None
	return content

if __name__ == "__main__" :
    main()