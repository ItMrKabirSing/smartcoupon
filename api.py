# Copyright @ISmartCoder
# Updates Channel: https://t.me/TheSmartDev

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

def scrape_coupon_codes(url, integer):
    if not url.startswith('http'):
        corrected_url = f"https://dealspotr.com/promo-codes/{url}"
    else:
        corrected_url = url
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

@app.route('/')
def home():
    return Response(json.dumps({
        'message': 'Welcome to the SmartDev Coupon API!',
        'tutorial': {
            'endpoint': '/cpn',
            'method': 'GET',
            'description': 'Retrieve coupons from smartdev for a given store.',
            'example_usage': '/cpn?site=amazon',
            'note': 'Replace "amazon" with the desired store slug (from amazon.com URL).'
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
        corrected_url = f"https://dealspotr.com/promo-codes/{site_url}"
        store_name = site_url.split('/')[0].split('.')[0]
    else:
        corrected_url = site_url
        domain = site_url.split('//')[-1]
        parts = domain.split('/')
        store_name = parts[-1] if parts[-1] else parts[-2]

    integer = extract_integer_from_html(corrected_url)
    if not integer:
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
