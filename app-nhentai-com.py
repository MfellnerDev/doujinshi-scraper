from selenium import webdriver
from flask import Flask
import requests
from selenium.webdriver.chrome.options import Options
from waitress import serve
import os
import json
from bs4 import BeautifulSoup
from helpers import create_dir_in_current_folder

app = Flask(__name__)

website_url = "https://nhentai.com"
img_server_url = "https://nhentai.com/api/comics"  # the complete url ALWAYS ends with /images !!!


@app.route('/download/<doujin_number>')
def scrape_doujin(doujin_number):
    if doujin_number.isdigit() and len(doujin_number) == 6:
        web_driver = _get_web_driver()
        try:
            # translate the 6 digit number to the slug
            doujin_slug = _get_doujin_slug(doujin_number, web_driver)
            _download_images(doujin_slug, web_driver)
        finally:
            web_driver.quit()
        return "Download complete"
    return "You must specify a valid doujin number!"


def _get_web_driver():
    """
    Initialize and return the selenium web driver.
    Why am I using it for this case? Because nhentai.com doesn't accept plain requests from the "requests" library,
    JavaScript and Cookies must be enabled.
    :return: web driver
    """
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-javascript")
    return webdriver.Chrome(options=options)


def _get_doujin_slug(doujin_number: str, web_driver):
    """
    Make a request to nhentai.com and translate the doujin number to the slug
    Explanation: When you access nhentai.com/g/[number], you get redirectet to nhentai.com/en/comic/[slug]
    We want to extract the slug out of the url.
    :param doujin_number: 6 digit number of the doujin
    :param web_driver: web driver
    :return: string containing the slug of the doujin
    """
    web_driver.get(f"{website_url}/g/{doujin_number}")
    url_with_slug = web_driver.current_url
    print(url_with_slug)
    return url_with_slug.split("/")[5]


def _parse_api_response_and_get_image_urls(response_content):
    """
    Extract the "source_url" elements from the API request.
    :param response_content: plain HTML content of API request.
    :return: list of the source images
    """
    soup = BeautifulSoup(response_content)
    response_data = soup.find("body").text
    response_json = json.loads(response_data)

    image_urls = []
    for image in response_json["images"]:
        image_urls.append(image["source_url"])

    return image_urls


def _download_images(doujin_slug: str, web_driver):
    """
    Download all images from the img_urls list using the requests library (see explanation below)
    :param doujin_slug:
    :param web_driver:
    :return:
    """
    # try to get the image source urls from the doujin
    web_driver.get(f"{img_server_url}/{doujin_slug}/images")
    img_urls = _parse_api_response_and_get_image_urls(web_driver.page_source)

    create_dir_in_current_folder(doujin_slug)

    for image_url in img_urls:
        """
        for the image downloading, we will use the requests library, because it is lightweight and the nhentai.com cdn
        (cdn.nhentai.com) is accepting requests from this library.
        """
        response_image = requests.get(image_url)
        if response_image.status_code == 200:
            current_img_filename = image_url.split('/')[7]
            with open(f"{doujin_slug}/{current_img_filename}", 'wb') as img:
                img.write(response_image.content)
                print(
                    f"Img download of {doujin_slug}: Saved img {image_url.split('/')[7]} into /{doujin_slug}/{current_img_filename}")
        else:
            raise ConnectionError(f"Expected server response status code {response_image.status_code}, got "
                                  f"{response_image.status_code}. Aborting.")
    print(f"Finished downloading all images for {doujin_slug}.")


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
