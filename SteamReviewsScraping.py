import requests
from bs4 import BeautifulSoup
import csv
import time

# CONFIG

BASE_URL = "https://steamcommunity.com/app/866020/homecontent/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

OUTPUT_FILE = "dataset/steam_GT_reviews.csv"

unique_reviews = set()

# Gunakan Session agar request lebih stabil
session = requests.Session()
session.headers.update(HEADERS)

# =========================================
# PARAMETER AWAL
# =========================================

cursor = None
page = 1
offset = 0

# =========================================
# CSV
# =========================================

with open(
    OUTPUT_FILE,
    mode="w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Author",
        "Game Title",
        "Profile URL",
        "Tanggal",
        "Review"
    ])

    while True:

        print(f"\n========== PAGE {page} ==========")

        params = {

            "userreviewsoffset": offset,
            "p": page,

            "workshopitemspage": page,
            "readytouseitemspage": page,
            "mtxitemspage": page,
            "itemspage": page,
            "screenshotspage": page,
            "videospage": page,
            "artpage": page,
            "allguidepage": page,
            "webguidepage": page,
            "integratedguidepage": page,
            "discussionspage": page,

            "numperpage": 10,

            "browsefilter": "toprated",

            "l": "indonesian",

            "appHubSubSection": 10,

            "filterLanguage": "indonesian",

            "searchText": "",

            "maxInappropriateScore": 100
        }

        # Halaman pertama tidak memakai cursor
        if cursor is not None:
            params["userreviewscursor"] = cursor

        # =========================================
        # REQUEST
        # =========================================

        response = session.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            print("Request gagal :", response.status_code)
            break

        print("=" * 60)
        print("Encoding  :", response.encoding)
        print("Apparent  :", response.apparent_encoding)
        print("Content-Type :", response.headers.get("Content-Type"))
        print("=" * 60)

        # Pakai encoding yang dideteksi
        response.encoding = response.apparent_encoding

        # Parse dari byte asli
        soup = BeautifulSoup(
            response.content,
            "html.parser",
            from_encoding=response.encoding
        )

        reviews = soup.find_all(
            "div",
            class_="apphub_Card"
        )

        print("Jumlah review :", len(reviews))

        if len(reviews) == 0:
            print("Tidak ada review lagi.")
            break

        # =====================================
        # LOOP REVIEW
        # =====================================

        for index, review in enumerate(reviews):

            author_game = "Growtopia"
            author_name = "-"
            author_url = "-"

            author_block = review.find(
                "div",
                class_="apphub_CardContentAuthorName"
            )

            if author_block:

                author_link = author_block.find("a")

                if author_link:
                    author_name = author_link.get_text(strip=True)
                    author_url = author_link.get("href", "-")

            posted_date = "-"
            review_text = "-"

            content = review.find(
                "div",
                class_="apphub_CardTextContent"
            )

            if content:

                date = content.find(
                    "div",
                    class_="date_posted"
                )

                if date:
                    posted_date = date.get_text(strip=True)
                    date.extract()

                # Debug HTML hanya sekali
                if page == 1 and index == 0:
                    print("\n========== RAW HTML ==========")
                    print(content.prettify())
                    print("==============================\n")

                review_text = content.get_text(
                    separator=" ",
                    strip=True
                )

                # Debug hasil akhir hanya sekali
                if page == 1 and index == 0:
                    print("========== REVIEW ==========")
                    print(repr(review_text))
                    print("============================\n")

            unique_key = (
                author_name,
                review_text
            )

            if unique_key in unique_reviews:
                continue

            unique_reviews.add(unique_key)

            writer.writerow([
                author_name,
                author_game,
                author_url,
                posted_date,
                review_text
            ])

            print("Saved :", author_name)

        # =====================================
        # CURSOR BERIKUTNYA
        # =====================================

        cursor_input = soup.find(
            "input",
            {"name": "userreviewscursor"}
        )

        offset_input = soup.find(
            "input",
            {"name": "userreviewsoffset"}
        )

        page_input = soup.find(
            "input",
            {"name": "p"}
        )

        if cursor_input is None:
            print("\nReview terakhir telah dicapai.")
            break

        cursor = cursor_input["value"]
        offset = int(offset_input["value"])
        page = int(page_input["value"])

        print(f"Next Cursor : {cursor}")
        print(f"Next Offset : {offset}")
        print(f"Next Page   : {page}")

        time.sleep(2)

print("\n================================")
print("SCRAPING SELESAI")
print(f"File tersimpan : {OUTPUT_FILE}")
print("================================")
