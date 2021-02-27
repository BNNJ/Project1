#!/usr/bin/env python3

import os
import requests
import csv
import argparse
import sys
from bs4 import BeautifulSoup
from loguru import logger as log

def joinUrls(*args):
	"""
	Returns a single url made of several parts, after cleaning them up.

	Because we might (and do) get relative paths, we need to handle going back
	to the parent (".."), which is why we need more than a simple concatenation
	"""
	url_parts = [arg.split('/') for arg in args]
	url_parts = [part for part_list in url_parts for part in part_list if part]
	url = []
	for part in url_parts:
		if part == ".." and url:
			url.pop()
		else:
			url.append(part)

	# Because we got rid of all the '/', we need to fix things by adding one
	# after "http:" to have proper url formatting.
	if url[0] == "http:":
		url[0] += '/'
	return "/".join(url)

def scrapeBookData(soup, url):
	"""
	Returns a dictionary containing basic data about the book

	The particular data we're looking for are:
		product_page_url
		universal_product_code (upc)
		title
		price_including_tax
		price_excluding_tax
		number_available
		product_description
		category
		review_rating
		image_url
	"""
	
	# First reduce the scope a bit, so we're not looking through the whole html page
	# product_page contains all the info about the book (except, somehow, the title
	# and the category), so we can start there.
	product_page = soup.find("article", class_="product_page")

	# Then there's also an interesting table with organized data
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
		'image_url': f"{url[:25]}/{product_page.img['src'][6:]}"
	}

def scrapeBookLinks(soup, url):
	articles = soup.findAll("article")
	links = [joinUrls(url[:url.rfind("/")], article.find("a")['href']) for article in articles]
	pager = soup.find(class_="pager")
	if pager != None and pager.find(class_="next"):
		next_page = pager.find(class_="next").a['href']
		links += scrapePage(joinUrls(url[:url.rfind("/")], next_page), scrapeBookLinks)
	return links

def scrapeCategories(soup, url):
	nav_list = soup.find(class_="nav nav-list").ul
	categories = [joinUrls(url[:url.rfind("/")], a['href']) for a in nav_list.findAll("a")]
	return categories

# @log.catch
def scrapePage(url, scrapeFunction):
	""" Wrapper around the scrapeFunction to avoid repeating the basic stuff """
	try:
		r = requests.get(url)
		if r.ok:
			log.info(f"{scrapeFunction.__name__: <17} {url}")
			soup = BeautifulSoup(r.text, 'lxml')
			return scrapeFunction(soup, url)
		else:
			log.warning("request returned code " + r.status_code + " for " + url)
	except Exception as e:
		log.exception(repr(e) + ": " + url)

def saveToCsv(data, header, file_path):
	with open(file_path, 'w', newline='') as f:
		w = csv.writer(f)
		w.writerow(header)
		w.writerows([d.values() for d in data if d])

def saveImages(books):
	categories = set([b['category'].replace(' ', '_') for b in books if b])
	[os.makedirs(f"images/{cat}", exist_ok=True) for cat in categories]
	for b in books:
		if b:
			log.info(f"saving {b['title']}...")
			path = f"images/{b['category'].replace(' ', '_')}/{b['title'].replace(' ', '_').replace('/', '-')}.jpg"
			img = requests.get(b['image_url']).content
			with open(path, 'wb') as f:
				f.write(img)

def format(record):
	""" Formatting function for the logger """
	if record['level'].name == "INFO":
		fmt = "{message}\n"
	else:
		fmt = "<level>{level: <8}</level> {message}\n"
	return fmt

def parseArgs():
	argp = argparse.ArgumentParser(description="Webscraper for books")
	
	verb = argp.add_mutually_exclusive_group()
	verb.add_argument(
		"-d", "--debug",
		action='store_true',
		help="Enables debug logs"
	)
	verb.add_argument(
		"-q", "--quiet",
		action='store_true',
		help="Silences the info logs"
	)

	argp.add_argument(
		"--nosave",
		action='store_false',
		help="Don't save to csv"
	)

	argp.add_argument(
		"-i", "--images",
		action='store_true',
		help="Save images"
	)

	argp.add_argument(
		"file",
		action='store',
		help="The csv file to write to (default 'books.csv')",
		nargs='?',
		default="books.csv"
	)
	return argp.parse_args()

def main(url, file, save=True, images=False):
	categories = scrapePage(url, scrapeCategories)
	books_links = [scrapePage(cat, scrapeBookLinks) for cat in categories]
	books_links = [book for cat in books_links for book in cat]
	books_data = [scrapePage(book, scrapeBookData) for book in books_links if book]
	log.info(f"scraped {len(books_data)} books from {len(categories)} categories")
	if save:
		header = [
			'product_page_url',
			'universal_product_code',
			'title',
			'price_including_tax',
			'price_excluding_tax',
			'number_available',
			'product_description',
			'category',
			'review_rating',
			'image_url'
		]
		saveToCsv(books_data, header, file)
	if images:
		saveImages(books_data)

if __name__ == "__main__":
	args = parseArgs()

	lvl = "DEBUG" if args.debug			\
		else "WARNING" if args.quiet	\
		else "INFO"
	log.remove()
	log.add(sys.stderr, level=lvl, format=format)

	home_url = "http://books.toscrape.com/index.html"
	main(home_url, args.file, args.nosave, args.images)
else:
	print("So I heard you like books...")
