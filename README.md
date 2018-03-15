# shopify-scraper

Simple scraper to extract all products from shopify sites

## Requirements

Python 3

## Usage

### Saving result as csv

```bash
python3 shopify.py [site's url] > products.csv
```

### Saving result as json 

```bash
python3 shopify.py --output-format json [site's url] > products.json
```

### Listing collections:

```bash
python3 shopify.py --list-collections [site's url] > products.csv
```

### Scraping products only in given collections

```bash
python3 shopify.py -c col1,col2,col3 [site's url] > products.csv
python3 shopify.py -c vip,babs-and-bab-lows https://www.greats.com > products.csv
```
