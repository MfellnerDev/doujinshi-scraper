from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import json
import os
from waitress import serve

app = Flask(__name__)

website_detail_url = 'https://www.nhentai.name/g'


@app.route('/download/<doujin_number>')
def download_doujin(doujin_number):
    if doujin_number.isdigit() and len(doujin_number) == 6:
        metadata = fetch_metadata(doujin_number)
        if metadata:
            return jsonify(metadata), 200
        else:
            return "Metadata not found", 404


def create_dir_in_current_folder(doujin_number):
    if not os.path.exists(doujin_number):
        os.makedirs(doujin_number)


def fetch_metadata(doujin_number):
    create_dir_in_current_folder(doujin_number)

    response = requests.get(f"{website_detail_url}/{doujin_number}/")

    if response.status_code == 200:
        parsed_response = parse_detail_page_response(response.text)
        if parsed_response:
            with open(f"{doujin_number}/meta.json", 'w') as meta_data:
                json.dump(parsed_response, meta_data)
            return parsed_response
    else:
        return None


def parse_detail_page_response(html_response):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_response, 'html.parser')

    # TODO: Find a way to parae www.nhentai.name/g/{doujin-number}, get metdata and store it in
    # TODO: /{doujin-number}/meta.json
    return ""

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
