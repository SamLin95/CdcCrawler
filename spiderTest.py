__author__ = 'Sizhe'
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bfs
from requests import request
import urllib2
from mongoengine import *
from datetime import datetime

def connectMongoDB():
	try:
		connect("test")
	except Exception as e:
		print str(e)

class Cdc_mmwr(Document):
	title = StringField(required=True)
	link = StringField(unique=True, required=True)
	issueTime = DateTimeField()
	crawlTime = DateTimeField(default=datetime.now())
	html = StringField()
	description = StringField()

def crawl_index(filename="sampleB.html"):
	soup = bfs(open(filename))
	mainContent = soup.find("div", class_="main-inner")
	dates = mainContent.find_all("p")
	links = mainContent.find_all("ul")
	for idx, date in enumerate(dates):
		#bfs4 will also extract "\n from text"
		string = date.find("strong").string.split(" / ")[0]
		day, year = string.split(", ")
		print "start crawling for date %s year %s...."%(day, year)
		currentLinks = links[idx]
		a = currentLinks.find_all('a')
		for link in a:
			link = "http://www.cdc.gov/mmwr/preview/" + link.get("href")
			print "link %s for the %s year %s"%(link, day, year)

def crawl_document(link):
	response = urllib2.urlopen(link)
	out = response.read()
	soup = bfs(out)
	buff = []
	paragraphs = soup.find_all("p", class_=False)
	print len(paragraphs)
	for paragraph in paragraphs:
		content = str(paragraph).strip("<p>").strip("</p>")
		buff.append(content)
	text = "".join(buff)
	print text	
	
	#print len(links) - len(dates)
def get_index_link(year):
	dic = {}
	dic[str(year)] = []
	year = str(year)[2: 4] if year < 2000 else str(year)
	link = "http://www.cdc.gov/mmwr/index%s.htm"%(year,)
	return link

def get_years_links(currentYear=2015):
	years = [x for x in xrange(1982, currentYear + 1)]
	years = map(lambda x: get_index_link(x), years)
	return years

def get_page_links(volumePage):
	soup = bfs(volumePage)
	mainContent = soup.find("div", class_="mSyndicate")
	links = mainContent.find("a")

if __name__ == "__main__":
	crawl_document("http://www.cdc.gov/mmwr/preview/mmwrhtml/00000182.htm")
	


