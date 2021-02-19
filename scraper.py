#!/usr/bin/env python3

import logging
import requests
import csv
# import traceback
import sys
from bs4 import BeautifulSoup


def joinUrls(*args):
	url_parts = [arg.split('/') for arg in args]
	url_parts = [part for part_list in url_parts for part in part_list if part]
	url = []
	for part in url_parts:
		if part == ".." and url:
			url.pop()
		else:
			url.append(part)
	if url[0] == "http:":
		url[0] += '/'
	return "/".join(url)

def scrapeBookData(soup, url):
	"""
	returns a dictionary containing basic data about the book :
	product_page_url
	universal_ product_code (upc)
	title
	price_including_tax
	price_excluding_tax
	number_available
	product_description
	category
	review_rating
	image_url
	"""
	
	# first reduce the scope a bit, so we're not looking through the whole html page
	# product_page contains all the info about the book (except, somehow, the title
	# and the category), so we can start there.
	# Then there's also an interesting table with organized data

	log.info("scraping book data: " + url)
	product_page = soup.find("article", class_="product_page")
	table = product_page.find('table')
	
	table_data_keys = [
		'UPC',
		'type',
		'price_excluding_tax',
		'price_including_tax',
		'tax',
		'availability',
		'number_of_reviews'
	]
	table_data = dict(
		zip(
			table_data_keys,
			[td.string for td in table.findAll("td")]
		)
	)
	
	desc = product_page.find(id="product_description").find_next_sibling('p').string
	
	rating_lookup = {
		'One': 1,
		'Two': 2,
		'Three': 3,
		'Four': 4,
		'Five': 5
	}

	return {
		'product_page_url': url,
		'universal_product_code': table_data['UPC'],
		'title': soup.h1.string,
		'price_including_tax': table_data['price_including_tax'][1:],
		'price_excluding_tax': table_data['price_excluding_tax'][1:],
		'number_available': int(''.join(filter(str.isdigit, table_data['availability']))),
		'product_description': desc,
		'category': "/".join([a.string for a in soup.find(class_="breadcrumb").findAll("a")[2:]]),
		'review_rating': rating_lookup[product_page.find(class_="star-rating")['class'][1]],
		'image_url': joinUrls(url, product_page.img['src'])
	}

def scrapeBookLinks(soup, url):
	articles = soup.findAll("article")
	links = [joinUrls(url[:url.rfind("/")], article.find("a")['href']) for article in articles]
	pager = soup.find(class_="pager")
	if pager != None and pager.find(class_="next"):
		next_page = pager.find(class_="next").a['href']
		links += scrapePage(joinUrls(url[:url.rfind("/")], next_page), scrapeBookLinks)
	# [print(link) for link in links]
	return links

def scrapeCategories(soup, url):
	nav_list = soup.find(class_="nav nav-list").ul
	categories = [joinUrls(url[:url.rfind("/")], a['href']) for a in nav_list.findAll("a")]
	return categories

"""
wrapper around the scrapeFunction to avoid repeating the basic stuff
"""
def scrapePage(url, scrapeFunction):
	try:
		r = requests.get(url)
		if r.ok:
			soup = BeautifulSoup(r.text, 'lxml')
			return scrapeFunction(soup, url)
		else:
			print(r.status_code)
	except Exception as e:
		log.EXCEPTION(repr(e) + ": " + url)

def saveToCsv(data, header, file_path):
	with open(file_path, 'w', newline='') as f:
		w = csv.writer(f)
		for i in range(len(data)):
			if data[i] is None:
				print(i)
		w.writerows([d.values() for d in data if d])

def main(url, file):
	categories = scrapePage(url, scrapeCategories)
	books_links = [scrapePage(cat, scrapeBookLinks) for cat in categories[3:4]]
	books_links = [book for cat in books_links for book in cat]		# flatten the list of lists
	books_data = [scrapePage(book, scrapeBookData) for book in books_links]
	# [print(book['title']) for book in books]
	# saveToCsv(books_data, header, file)

if __name__ == "__main__":
	log = logging.getLogger(__name__)
	# if "-d" in sys.argv:
	# 	print("debug")
	# 	log.setLevel(logging.DEBUG)
	# elif "-s" in sys.argv:
	# 	print("warning")
	# 	log.setLevel(logging.WARNING)
	# else:
	# 	print("info")
	# 	log.setLevel(logging.INFO)
	log.setLevel(logging.INFO)
	log.info("hello")
	# home_url = "http://books.toscrape.com/index.html"
	# csv_file = "./books.csv"
	# main(home_url, csv_file)
else:
	print("HELLO THERE")
