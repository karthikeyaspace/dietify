import requests
from bs4 import BeautifulSoup
from config import env

links = [
    "https://www.bbcgoodfood.com/health/healthy-food-guides/best-recipes-health",
    "https://www.delish.com/cooking/recipe-ideas/g3733/healthy-dinner-recipes",
    "https://www.mayoclinic.org/healthy-lifestyle/recipes/heart-healthy-recipes/rcs-20077163",
    "https://www.taste.com.au/healthy/galleries/top-100-healthy-dinner-recipes/9v410ya9",
    "https://www.thepioneerwoman.com/food-cooking/meals-menus/g35180879/healthy-dinner-ideas",
    "https://time.com/3724505/healthy-recipes-healthiest-foods",
    "https://www.healthline.com/nutrition/simple-dinner-ideas",
    "https://www.everydayhealth.com/healthy-recipes/the-most-popular-everyday-health-recipes-of-2022",
    "https://vaya.in/10-balanced-diet-recipes-to-satisfy-your-taste-buds/",
    "https://www.goodhousekeeping.com/food-recipes/healthy/g154/healthy-dinner-recipes",
    "https://timesofindia.indiatimes.com/life-style/health-fitness/diet/10-healthy-dinner-ideas/articleshow/46173052.cms",
]


OUTFILE = env['SCRAPPER_OUTFILE']


def scrape_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        return text

    except Exception as e:
        print(f"Error scraping url {url}: {e}")
        return None


def save_to_disk(data: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        for url, content in data.items():
            if content:
                f.write(f"URL: {url}\n")
                f.write(content)
                f.write("\n\n")


def main():
    data = {}

    for url in links:
        print(f"Scraping {url}")
        data[url] = scrape_url(url)

    save_to_disk(data, OUTFILE)
    print("Scraping done")


if __name__ == "__main__":
    main()
