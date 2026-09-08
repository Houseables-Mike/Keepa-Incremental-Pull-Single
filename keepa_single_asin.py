"""
Standalone test: confirms a single Keepa API call works and that we can
correctly parse star rating and review count out of the response. No
Google Sheets logic involved — this only proves the Keepa piece works.

Before running:
1. Set your Keepa API key as an environment variable named KEEPA
   (or temporarily paste it into API_KEY below for a quick test).
2. Fill in TEST_ASIN with any real Amazon ASIN.
3. pip install requests
"""

import os
import requests
from dotenv import load_dotenv

# ---- Fill this in ----
load_dotenv()
API_KEY = os.getenv('KEEPA', 'PASTE_YOUR_KEY_HERE_IF_NOT_USING_ENV_VAR')
TEST_ASIN = 'B0CGHZZFNM'  # Example ASIN: Skeleton Disarticulated Skeleton, SDH-WH-62IN-FBA


def parse_product(p):
    """Same parsing logic as the full script — isolated here for testing."""
    csv = p.get('csv') or []

    # Rating: csv[16] values are 0-50 (e.g. 45 = 4.5 stars)
    rating_arr = csv[16] if len(csv) > 16 and csv[16] else []
    star_rating = ''
    if rating_arr:
        raw = rating_arr[-1]
        star_rating = round(raw / 10, 1) if raw > 0 else ''

    # Review count: csv[17]
    review_arr = csv[17] if len(csv) > 17 and csv[17] else []
    review_count = ''
    if review_arr:
        raw = review_arr[-1]
        review_count = raw if raw > 0 else ''

    return star_rating, review_count


def main():
    print(f'Step 1: Calling Keepa for ASIN {TEST_ASIN}...')
    url = f'https://api.keepa.com/product?key={API_KEY}&domain=1&asin={TEST_ASIN}&rating=1'
    print(url)
    response = requests.get(url, timeout=30)
    print(f'  HTTP status: {response.status_code}')

    data = response.json()

    print('Step 2: Checking the response for product data...')
    products = data.get('products')
    if not products:
        print('  No product data returned. Full response below for debugging:')
        print(data)
        return

    print(f'  Found product data. Tokens left on your account: {data.get("tokensLeft")}')

    print('Step 3: Parsing rating and review count...')
    title = products[0].get('title', '(no title returned)')
    star_rating, review_count = parse_product(products[0])

    print('\n--- RESULT ---')
    print(f'ASIN:          {TEST_ASIN}')
    print(f'Title:         {title[:70]}')
    print(f'Star Rating:   {star_rating}')
    print(f'Review Count:  {review_count}')

    if star_rating != '' and review_count != '':
        print('\nSUCCESS — got both a rating and a review count back.')
    else:
        print('\nNOTE: one or both values came back blank. This can be normal for a '
              'brand-new listing with no reviews yet, or it may mean the "rating=1" '
              'parameter/history data is unavailable for this ASIN. Try a different '
              'well-established ASIN to confirm the parsing logic itself is correct.')


if __name__ == '__main__':
    main()