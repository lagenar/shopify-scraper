# shopify-scraper
Simple scraper to extract all products from shopify sites


Requirements:
Python 3

Usage:
python3 shopify.py [site's url]

Listing collections:
python3 shopify.py --list-collections [site's url]

Scraping products only in given collections:
python3 shopify.py -c col1,col2,col3 [site's url]

Example:
python3 shopify.py -c vip,babs-and-bab-lows https://www.greats.com

The products get saved into a file named products.csv in the current directory.
