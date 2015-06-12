__author__ = 'Sizhe'
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bfs
from requests import request
import urllib2
from mongoengine import *
from datetime import datetime

"""start point matrix
    for each value in the map, first one is the current year index page and the 
    second one is Historical arhive for index Pages 
"""
startpoints = {"weeklyreport": ["http://www.cdc.gov/mmwr/index2015.html","http://www.cdc.gov/mmwr/mmwr_wk/wk_pvol.html"], 
				"recommendations": ["http://www.cdc.gov/mmwr/indrr_2015.html","http://www.cdc.gov/mmwr/mmwr_rr/rr_pvol.html"],
				"Surveillance": ["http://www.cdc.gov/mmwr/indss_2015.html",
				                "http://www.cdc.gov/mmwr/mmwr_ss/ss_pvol.html"],
				"supplements": [None, "http://www.cdc.gov/mmwr/mmwr_su/index.html"],
				"Notifiable Diseases": [None, "http://www.cdc.gov/mmwr/mmwr_nd/index.html"]}

def connectMongoDB():
	try:
		connect("test")
	except Exception as e:
		print str(e)

def getLinks(historicalIndexLink):
	try:
		response = urllib2.urlopen(historicalIndexLink)
		content = response.read()
		soup = bfs(content)
		mainContent = soup.find("div", class_="main-inner")
		links = mainContent.find_all("a") #traverse the tree find all <a>
		hrefs = [link.get("href") for link in links if link.get("href") is not None]
		hrefs = map(lambda x: "http://www.cdc.gov" + x, hrefs)
		return hrefs
	except urllib2.HTTPError as e1:
		print "please check your url for %s"%(historicalIndexLink,), e1.reason
		return [] 
	except urllib2.URLError as e2:
		print "please check your link for %s"%(historicalIndexLink), e2.reason
		return []


class Cdc_mmwr(Document):
	title = StringField(required=True)
	link = StringField(unique=True, required=True)
	reportType = StringField()
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

#crawl the document with in plain <p> tag
def crawl_document(link):
	response = urllib2.urlopen(link)
	out = response.read()
	soup = bfs(out)
	buff = []
	paragraphs = soup.find_all("p", class_=False)
	for paragraph in paragraphs:
		content = str(paragraph).strip("<p>").strip("</p>")
		buff.append(content)
	text = "".join(buff)
	print text

	
	#print len(links) - len(dates)
def get_index_links(year):
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
	#crawl_document("http://www.cdc.gov/mmwr/preview/mmwrhtml/00000182.htm")
	print getLinks(startpoints.get("supplements")[1])
	


