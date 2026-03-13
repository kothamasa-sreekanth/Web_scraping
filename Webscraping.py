# """
# Hotel Scraper - BeautifulSoup Only
# Handles MakeMyTrip bot blocking using ScraperAPI (free tier)
# """

# import requests
# from bs4 import BeautifulSoup
# import csv
# import time


# # ══════════════════════════════════════════════════════
# #  ScraperAPI Setup (FREE - 1000 requests/month)
# #  Sign up at: https://www.scraperapi.com/
# #  Then paste your API key below
# # ══════════════════════════════════════════════════════

# SCRAPER_API_KEY = "0e9bffe008cf923662e4d04857251e46"

# def fetch_with_scraperapi(web_url):
#     """Uses ScraperAPI to bypass bot detection - renders JS too"""
#     api_url = "http://api.scraperapi.com/"
#     params = {
#         "api_key": SCRAPER_API_KEY,
#         "url": web_url,
#         "render": "true",       # renders JavaScript ✅
#         "country_code": "in",   # Indian IP address ✅
#     }
#     print("🔁 Fetching via ScraperAPI...")
#     response = requests.get(api_url, params=params, timeout=120)
#     return response


# def web_scrapper(web_url, f_name):

#     print("✅ URL and filename received!")
#     print("⏳ Connecting...\n")

#     # ── Step 1: Fetch page via ScraperAPI ────────────
#     try:
#         response = fetch_with_scraperapi(web_url)
#     except requests.exceptions.ReadTimeout:
#         print("❌ Request timed out.")
#         print("👉 Check your API key or internet connection.")
#         return
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return

#     # ── Step 2: Check response ───────────────────────
#     if response.status_code != 200:
#         print(f"❌ Failed! Status code: {response.status_code}")
#         print(f"   Response: {response.text[:300]}")
#         return

#     print(f"✅ Connected! Status: {response.status_code}")

#     # ── Step 3: Parse HTML ───────────────────────────
#     soup = BeautifulSoup(response.text, 'lxml')

#     # ── DEBUG: Save raw HTML to find correct class names ──
#     # Uncomment below if no hotels found, open debug.html in browser
#     with open("debug.html", "w", encoding="utf-8") as f:
#         f.write(soup.prettify())
#     print("🔍 Raw HTML saved to debug.html (helps find correct class names)")

#     # ── Step 4: Find hotel cards ─────────────────────
#     # MMT class names change often — check debug.html if this returns 0
#     mobile_divs = soup.find_all('div', class_= sg-col-inner)
             


#     if not mobile_divs:
#         print("\n⚠️  No hotels found with current class names!")
#         print("📂 Open 'debug.html' in your browser")
#         print("   Right-click a hotel card → Inspect → find the correct class name")
#         print("   Then update 'mobile_divs = soup.find_all(...)' line above\n")
#         return

#     print(f"🏨 Found {len(mobile_divs)} hotels — saving to '{f_name}.csv'...\n")

#     # ── Step 5: Extract & Save ───────────────────────
#     with open(f'{f_name}.csv', 'w', encoding='utf-8', newline='') as file_csv:
#         writer = csv.writer(file_csv)
#         writer.writerow(['mobile_name','price', 'rating', 'features', 'review'])

#         for mobile in mobile_divs:

#             tag = mobile.find('span', class_="a-size-mini s-line-clamp-1")
#             mobile_name = tag.text.strip() if tag else "NA"

#             tag = mobile.find('span', class_="a-price-whole")
#             price = tag.text.strip() if tag else "NA"

#             tag = mobile.find('span', class_="a-size-small a-color-base")
#             rating = tag.text.strip() if tag else "NA"

#             tag = mobile.find('span', class_="a-size-mini puis-normal-weight-text s-underline-text")
#             review = tag.text.strip() if tag else "NA"

#             tag= mobile.find('span', class_="a-size-medium a-spacing-none a-color-base a-text-normal")
#             features= tag.text.strip() if tag else "NA"

#             # tag = mobile.find('a', href=True)
#             # link = tag['href'] if tag else "NA"

#             writer.writerow([mobile_name, price, rating, features, review])
#             print(f"  ✔ {mobile_name} | {rating} | ₹{price}")

#     print(f"\n✅ Done! Saved to '{f_name}.csv'")


# # ══════════════════════════════════════════════════════
# if __name__ == '__main__':
#     url = input("Enter URL: ").strip()
#     fn  = input("Enter file name (without .csv): ").strip()
#     web_scrapper(url, fn)


# """
# Amazon Oppo Mobile Scraper - BeautifulSoup + ScraperAPI
# Correctly targets individual product cards (not page wrapper)
# """

import requests
from bs4 import BeautifulSoup
import csv
import time

SCRAPER_API_KEY = "0e9bffe008cf923662e4d04857251e46"


def fetch_with_scraperapi(web_url):
    api_url = "http://api.scraperapi.com/"
    params = {
        "api_key"     : SCRAPER_API_KEY,
        "url"         : web_url,
        "render"      : "true",
        "country_code": "in",
        "wait"        : 4000,
    }
    print("🔁 Fetching via ScraperAPI (wait ~30 sec)...")
    response = requests.get(api_url, params=params, timeout=120)
    return response


def web_scrapper(web_url, f_name):

    print("✅ Starting scraper!")
    all_data = []
    page = 1

    while True:
        # ── Build paged URL ───────────────────────────
        paged_url = web_url + f"&page={page}" if "page=" not in web_url else web_url
        print(f"\n📄 Scraping page {page}...")

        try:
            response = fetch_with_scraperapi(paged_url)
        except Exception as e:
            print(f"❌ Error: {e}")
            break

        if response.status_code != 200:
            print(f"❌ Failed! Status: {response.status_code}")
            break

        # ── Save debug HTML (page 1 only) ─────────────
        if page == 1:
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("📂 Saved debug.html — open in browser if you see NA values")

        soup = BeautifulSoup(response.text, 'lxml')

        # ══════════════════════════════════════════════
        # KEY FIX: Target EACH product card individually
        # NOT the whole page wrapper (id="search")
        # Each product card has: data-component-type="s-search-result"
        # ══════════════════════════════════════════════
        cards = soup.find_all('div', attrs={'data-component-type': 's-search-result'})

        if not cards:
            print("⚠️  No product cards found!")
            print("   → Open debug.html and search for 'data-component-type'")
            print("   → If missing, Amazon may have blocked — retry in few minutes")
            break

        print(f"   ✅ Found {len(cards)} products on page {page}")

        found_on_page = 0
        for card in cards:

            # ── Name ──────────────────────────────────
            tag = (
                card.find('span', class_='a-size-medium a-color-base a-text-normal') or
                card.find('span', class_='a-size-base-plus a-color-base a-text-normal') or
                card.find('h2')
            )
            name = tag.text.strip() if tag else "NA"
            if name == "NA":
                continue   # skip empty/ad cards

            # ── Price ─────────────────────────────────
            tag = card.find('span', class_='a-price-whole')
            price = "₹" + tag.text.replace(',','').strip() if tag else "NA"

            # ── Star Rating ───────────────────────────
            tag = card.find('span', class_='a-icon-alt')
            rating = tag.text.strip() if tag else "NA"   # e.g. "4.2 out of 5 stars"

            # ── Review Count ──────────────────────────
            tag = card.find('span', class_='a-size-base s-underline-text')
            reviews = tag.text.strip() if tag else "NA"

            # ── RAM / Features ────────────────────────
            tag = card.find('span', class_='a-size-base po-break-word')
            features = tag.text.strip() if tag else "NA"

            # ── Product Link ──────────────────────────
            tag = card.find('a', class_='a-link-normal s-no-outline', href=True)
            if not tag:
                tag = card.find('a', href=True)
            link = ("https://www.amazon.in" + tag['href']) if tag and tag['href'].startswith('/') else "NA"

            all_data.append([name, price, rating, reviews, features, link])
            found_on_page += 1
            print(f"  ✔ {name[:55]:<55} | {price} | ⭐ {rating}")

        # ── Check next page ───────────────────────────
        next_btn = soup.find('a', class_='s-pagination-next')
        if not next_btn or found_on_page == 0:
            print(f"\n🏁 All pages done! Total pages: {page}")
            break

        page += 1
        time.sleep(2)

    # ── Save CSV ──────────────────────────────────────
    if all_data:
        with open(f'{f_name}.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['mobile_name', 'price', 'rating', 'reviews', 'features', 'link'])
            writer.writerows(all_data)
        print(f"\n🎉 {len(all_data)} products saved to '{f_name}.csv'")
    else:
        print("\n❌ No data saved. Open debug.html to investigate.")


# ══════════════════════════════════════════════════════
if __name__ == '__main__':

    print("=" * 50)
    print("   🛒 Oppo Mobiles Scraper — Amazon India")
    print("=" * 50)
    url = input("\nPress Enter to use default OR paste your URL: ").strip()
    fn = input("File name (without .csv): ").strip()
    web_scrapper(url, fn)


