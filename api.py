#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev
from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from collections import OrderedDict

app = Flask(__name__)

def extract_integer_from_html(url):
    if not url.startswith('http'):
        corrected_url = f"https://dealspotr.com/promo-codes/{url}"
    else:
        corrected_url = url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://dealspotr.com/',
    }
    try:
        response = requests.get(corrected_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        promo_div = soup.find('div', class_='copy-code')
        if promo_div and 'id' in promo_div.attrs:
            match = re.search(r'(\d+)', promo_div['id'])
            return match.group(1) if match else None
        return None
    except requests.RequestException as e:
        print(f"Failed to retrieve page to extract integer from {corrected_url}: {e}")
        return None

def scrape_coupon_codes(url, integer=None):
    if not url.startswith('http'):
        corrected_url = f"https://dealspotr.com/promo-codes/{url}"
    else:
        corrected_url = url
    if re.search(r'hostinger(?:\.com(?:-website-builder)?)?$', corrected_url):
        full_url = 'https://dealspotr.com/promo-codes/hostinger.com-website-builder'
    else:
        if not integer:
            return []
        full_url = f"{corrected_url.rstrip('/')}/{integer}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://dealspotr.com/',
    }
    try:
        response = requests.get(full_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        coupons = []
        coupon_divs = soup.find_all('div', class_='copy-code')
        for div in coupon_divs:
            title_elem = div.find('div', class_='promoblock--title')
            code_input = div.find('input', {'class': 'dnone', 'type': 'text'})
            title = title_elem.get_text(strip=True) if title_elem else "No title available"
            code = code_input.get('value') if code_input and code_input.get('value') else "No code available"
            coupons.append({
                'code': code,
                'title': title
            })
        return coupons
    except requests.RequestException as e:
        print(f"Failed to retrieve page {full_url}: {e}")
        return []

def search_store_url(keyword):
    search_url = f"https://dealspotr.com/stores?qT={keyword}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://dealspotr.com/',
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        store_blocks = soup.find_all('div', class_='storeblock--main')
        for block in store_blocks:
            link = block.find('a', class_='gr3')
            if link and 'href' in link.attrs:
                store_url = link['href']
                store_name_elem = block.find('span', class_='href gr9')
                store_name = store_name_elem.get_text(strip=True).split('/')[0] if store_name_elem else store_url.split('/')[-1]
                if re.match(r'hostinger(?:\.com)?$', store_name):
                    return 'https://dealspotr.com/promo-codes/hostinger.com-website-builder', 'hostinger'
                return store_url, store_name
        return None, None
    except requests.RequestException as e:
        print(f"Failed to search for store with keyword {keyword}: {e}")
        return None, None

@app.route('/')
def home():
    return Response(json.dumps({
        'message': 'Welcome to the SmartDev Coupon API!',
        'tutorial': {
            'endpoint': '/cpn',
            'method': 'GET',
            'description': 'Retrieve coupons from Dealspotr for a given store.',
            'example_usage': '/cpn?site=hostinger.com-website-builder',
            'note': 'Replace "hostinger.com-website-builder" with the desired store slug (from Dealspotr URL).'
        },
        'search_tutorial': {
            'endpoint': '/search',
            'method': 'GET',
            'description': 'Search for coupons by store keyword.',
            'example_usage': '/search?keyword=hostinger',
            'note': 'Replace "hostinger" with the desired store name.'
        },
        'developer': '@ISmartCoder',
        'updates_channel': 't.me/TheSmartDev'
    }, indent=2), mimetype='application/json')

@app.route('/cpn')
def get_coupons():
    start_time = time.time()
    site_url = request.args.get('site')
    if not site_url:
        return Response(json.dumps({'error': 'Please Provide A Valid URL For Coupons ❌'}, indent=2), status=400, mimetype='application/json')
    if not site_url.startswith('http'):
        if re.match(r'hostinger(?:\.com)?$', site_url):
            corrected_url = 'https://dealspotr.com/promo-codes/hostinger.com-website-builder'
            store_name = 'hostinger'
        else:
            # Append .com if site_url has no domain extension or specific suffix
            if not re.search(r'\.\w+$|-website-builder$', site_url):
                site_url = f"{site_url}.com"
            corrected_url = f"https://dealspotr.com/promo-codes/{site_url}"
            store_name = site_url.split('/')[0].split('.')[0]
    else:
        corrected_url = site_url
        domain = site_url.split('//')[-1]
        parts = domain.split('/')
        store_name = parts[-1] if parts[-1] else parts[-2]
        if re.match(r'hostinger(?:\.com)?$', store_name):
            corrected_url = 'https://dealspotr.com/promo-codes/hostinger.com-website-builder'
            store_name = 'hostinger'
    integer = extract_integer_from_html(corrected_url) if not re.search(r'hostinger(?:\.com(?:-website-builder)?)?$', corrected_url) else None
    if not integer and not re.search(r'hostinger(?:\.com(?:-website-builder)?)?$', corrected_url):
        return Response(json.dumps({'error': 'Sorry Bro Invalid Site URL Provided ❌'}, indent=2), status=404, mimetype='application/json')
    coupons = scrape_coupon_codes(corrected_url, integer)
    if not coupons:
        return Response(json.dumps({'message': 'Sorry No Coupons Available For This Site ❌'}, indent=2), status=404, mimetype='application/json')
    total = len(coupons)
    time_taken = f"{time.time() - start_time:.2f} seconds"
    response = OrderedDict()
    response["store"] = store_name
    response["time_taken"] = time_taken
    response["total"] = total
    response["updates_channel"] = "t.me/TheSmartDev"
    response["api"] = "SmartDev Coupon Scraper"
    response["developer"] = "@ISmartCoder"
    response["results"] = coupons
    return Response(json.dumps(response, indent=2), mimetype='application/json')

@app.route('/search')
def search_coupons():
    start_time = time.time()
    keyword = request.args.get('keyword')
    if not keyword:
        return Response(json.dumps({'error': 'Please Provide A Valid Keyword For Search ❌'}, indent=2), status=400, mimetype='application/json')
    store_url, store_name = search_store_url(keyword)
    if not store_url or not store_name:
        return Response(json.dumps({'error': f'No Store Found For Keyword "{keyword}" ❌'}, indent=2), status=404, mimetype='application/json')
    integer = extract_integer_from_html(store_url) if not re.search(r'hostinger(?:\.com(?:-website-builder)?)?$', store_url) else None
    if not integer and not re.search(r'hostinger(?:\.com(?:-website-builder)?)?$', store_url):
        return Response(json.dumps({'error': f'Sorry Bro Invalid Store URL Found For Keyword "{keyword}" ❌'}, indent=2), status=404, mimetype='application/json')
    coupons = scrape_coupon_codes(store_url, integer)
    if not coupons:
        return Response(json.dumps({'message': f'Sorry No Coupons Available For Store "{store_name}" ❌'}, indent=2), status=404, mimetype='application/json')
    total = len(coupons)
    time_taken = f"{time.time() - start_time:.2f} seconds"
    response = OrderedDict()
    response["store"] = store_name
    response["time_taken"] = time_taken
    response["total"] = total
    response["updates_channel"] = "t.me/TheSmartDev"
    response["api"] = "SmartDev Coupon Scraper"
    response["developer"] = "@ISmartCoder"
    response["results"] = coupons
    return Response(json.dumps(response, indent=2), mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
