#!/usr/bin/env python3

#import logging
import requests
from bs4 import BeautifulSoup

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

def joinUrls(*args):
	url_parts = [arg.split('/') for arg in args]
	url_parts = [part for part_list in url_parts for part in part_list if part]
	url = []
	for part in url_parts:
		if part == ".." and url:
			url.pop()
		else:
			url.append(part)
	return "/".join(url)

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
def scrapeBook(soup, url):
	"""
	first reduce the scope a bit, so we're not looking through the whole html page
	product_page contains all the info about the book (except, somehow, the title
	and the category), so we can start there.
	Then there's also an interesting table with organized data
	"""
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

	return {
		'product_page_url': url,
		'universal_product_code': table_data['UPC'],
		'title': soup.h1.string,
		'price_including_tax': table_data['price_including_tax'][1:],
		'price_excluding_tax': table_data['price_excluding_tax'][1:],
		'number_available': int(''.join(filter(str.isdigit, table_data['availability']))),
		'product_description': desc[:desc.index(".", 120)] + "...",
		'category': "/".join([a.string for a in soup.find(class_="breadcrumb").findAll("a")[2:]]),
		'review_rating': "",
		'image_url': joinUrls(url, product_page.img['src'])
	}

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
		print(repr(e))

def main():
	url = "http://books.toscrape.com/catalogue/foundation-foundation-publication-order-1_375/index.html"
	book_data = scrapePage(url, scrapeBook)
	{print("# " + k + ":\n" + repr(v)) for (k, v) in book_data.items()}

if __name__ == "__main__":
	main()
else:
	print("HELLO THERE")
