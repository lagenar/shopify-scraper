import sys
import csv
import json
import time
import urllib.request
from urllib.error import HTTPError
import argparse


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'


def get_page(url, page, collection_handle=None):
    full_url = url
    if collection_handle:
        full_url += '/collections/{}'.format(collection_handle)
    full_url += '/products.json'
    req = urllib.request.Request(
        full_url + '?page={}'.format(page),
        data=None,
        headers={
            'User-Agent': USER_AGENT
        }
    )
    while True:
        try:
            data = urllib.request.urlopen(req).read()
            break
        except HTTPError:
            sys.stderr.write('Blocked! Sleeping...')
            time.sleep(180)
            sys.stderr.write('Retrying')

    products = json.loads(data.decode())['products']
    return products


def get_page_collections(url):
    full_url = url + '/collections.json'
    page = 1
    while True:
        req = urllib.request.Request(
            full_url + '?page={}'.format(page),
            data=None,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        while True:
            try:
                data = urllib.request.urlopen(req).read()
                break
            except HTTPError:
                sys.stderr.write('Blocked! Sleeping...')
                time.sleep(180)
                sys.stderr.write('Retrying')

        cols = json.loads(data.decode())['collections']
        if not cols:
            break
        for col in cols:
            yield col
        page += 1


def check_shopify(url):
    try:
        get_page(url, 1)
        return True
    except Exception:
        return False


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
       not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url

    return fixed_url.rstrip('/')


def extract_products_collection(url, col):
    page = 1
    products = get_page(url, page, col)
    while products:
        for product in products:
            title = product['title']
            product_type = product['product_type']
            product_url = url + '/products/' + product['handle']
            product_handle = product['handle']

            def get_image(variant_id):
                images = product['images']
                for i in images:
                    k = [str(v) for v in i['variant_ids']]
                    if str(variant_id) in k:
                        return i['src']

                return ''

            for i, variant in enumerate(product['variants']):
                price = variant['price']
                option1_value = variant['option1'] or ''
                option2_value = variant['option2'] or ''
                option3_value = variant['option3'] or ''
                option_value = ' '.join([option1_value, option2_value,
                                         option3_value]).strip()
                sku = variant['sku']
                main_image_src = ''
                if product['images']:
                    main_image_src = product['images'][0]['src']

                image_src = get_image(variant['id']) or main_image_src
                stock = True
                if not variant['available']:
                    stock = False

                row = {'sku': sku, 'product_type': product_type,
                       'title': title, 'option_value': option_value,
                       'price': price, 'stock': stock, 'body': str(product['body_html']),
                       'variant_id': product_handle + str(variant['id']),
                       'product_url': product_url, 'image_src': image_src}
                yield row

        page += 1
        products = get_page(url, page, col)


def extract_products(url, collections=None):
    seen_variants = set()
    for col in get_page_collections(url):
        if collections and col['handle'] not in collections:
            continue
        handle = col['handle']
        title = col['title']
        for product in extract_products_collection(url, handle):
            variant_id = product['variant_id']
            if variant_id in seen_variants:
                continue

            seen_variants.add(variant_id)
            yield {
                'code': product['sku'],
                'collection': str(title),
                'category': product['product_type'],
                'name': product['title'],
                'variant_name': product['option_value'],
                'price': product['price'],
                'in_stock': product['stock'],
                'url': product['product_url'],
                'image_url': product['image_src'],
                'image_thumbnail_url': product['image_src'].replace('.jpg', '_large.jpg').replace('.png', '_large.png'),
                'body': product['body']
            }


def print_as_csv(url, collections):
    writer = csv.writer(sys.stdout)
    writer.writerow(['Code', 'Collection', 'Category',
                     'Name', 'Variant Name',
                     'Price', 'In Stock', 'URL', 'Image URL', 'Body'])
    for product in extract_products(url, collections):
        writer.writerow([product['code'], product['collection'],
                         product['category'], product['name'],
                         product['variant_name'], product['price'],
                         'Yes' if product['in_stock'] else 'No', product['url'],
                         product['image_url'], product['body']])


def print_as_json(url, collections):
    products = []
    for product in extract_products(url, collections):
        products.append(product)
    json.dump(products, sys.stdout, indent=4)


def main():
    parser = argparse.ArgumentParser(
        description='Simple scraper to extract all products from shopify sites')
    parser.add_argument('--list-collections', '-l', dest='list_collections', action='store_true',
                        help='List collections in the site')
    parser.add_argument('--collections', '-c', dest='collections', default='',
                        help='Get products only from the given collections (comma separated)')
    parser.add_argument('--output-format', '-of', dest='output_format', default='csv', choices=['csv', 'json'],
                        help='Get output in either csv(default) or json')
    parser.add_argument('url', metavar='URL', help='URL of the shopify site')
    args = parser.parse_args()
    url = fix_url(args.url)
    if args.list_collections:
        for col in get_page_collections(url):
            print(col['handle'])
    else:
        collections = []
        if args.collections:
            collections = args.collections.split(',')
        if args.output_format == 'csv':
            print_as_csv(url, collections)
        elif args.output_format == 'json':
            print_as_json(url, collections)


if __name__ == '__main__':
    main()
