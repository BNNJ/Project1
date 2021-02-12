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
	if url[0] == "http:":
		url[0] += '/'
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
def scrapeBookData(soup, url):
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
		'product_description': desc[:desc.index(".", 120)] + "...",
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
		print(repr(e))

def main():
	url_foundation = "http://books.toscrape.com/catalogue/foundation-foundation-publication-order-1_375/index.html"
	url_sciencefiction = "http://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html"
	url_fiction = "http://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
	url_home = "http://books.toscrape.com/index.html"

	categories = scrapePage(url_home, scrapeCategories)
	# [print(cat) for cat in categories]
	books_links = [scrapePage(cat, scrapeBookLinks) for cat in categories]
	books_links = [book for cat in books_links for book in cat]
	# [print(link) for link in books_links]
	books_data = [scrapePage(book, scrapeBookData) for book in books_links]
	[print(book['title']) for book in books]

if __name__ == "__main__":
	main()
else:
	print("HELLO THERE")
