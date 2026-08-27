import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://steamcommunity.com/app/1665460/homecontent/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_FILE = "dataset/tester/steam_EFootball_reviews.csv"

unique_reviews = set()

cursor = None
page = 1
offset = 0

with open(
    OUTPUT_FILE,
    mode="w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Author",
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

        response = requests.get(
            BASE_URL,
            params=params,
            headers=HEADERS
        )

        if response.status_code != 200:
            print("Request gagal.")
            break

        soup = BeautifulSoup(
            response.text,
            "html.parser"
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

        for review in reviews:

            author_name = "-"
            author_url = "-"

            author_block = review.find(
                "div",
                class_="apphub_CardContentAuthorName"
            )

            if author_block:

                author_link = author_block.find("a")

                if author_link:
                    author_name = author_link.text.strip()
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
                    posted_date = date.text.strip()
                    date.extract()
                    

                review_text = content.get_text(
                    separator=" ",
                    strip=True
                )

            unique_key = (
                author_name,
                review_text
            )

            if unique_key in unique_reviews:
                continue

            unique_reviews.add(unique_key)

            writer.writerow([
                author_name,
                author_url,
                posted_date,
                review_text
            ])

            print("Saved :", author_name)

        # =====================================
        # AMBIL CURSOR BERIKUTNYA
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

        # Jika cursor tidak ada berarti review habis
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
