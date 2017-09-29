# -*- coding: utf-8 -*-
from flask import (abort, Flask, render_template, request, Markup)
import json
import requests
import pywikibot
from pywikibot import page

app = Flask(__name__)

COMMONS = pywikibot.Site('commons', 'commons')
FILE_NAMESPACE = 6

IMAGE_WIDTH = 300
IMAGE_HEIGHT = 200

COMMONS_QI_CATEGORY = 'Category:Quality images'
COMMONS_FP_CATEGORY = 'Category:Featured pictures on Wikimedia Commons'
COMMONS_VI_CATEGORY = 'Category:Valued images sorted by promotion date'
SUPPORTED_CATEGORIES = [
    u'Category:Supported by Wikimedia AU‎',
    u'Category:Supported by Wikimedia CH‎',
    u'Category:Supported by Wikimedia Deutschland‎',
    u'Category:Supported by Wikimedia France',
    u'Category:Supported by Wikimedia Italia‎',
    u'Category:Supported by Wikimedia UK',
    u'Category:Supported by Wikimedia Österreich‎ ',
    u'Category:Media supported by Wikimedia France',
    u'Images uploaded by Fæ'
]

GLOBALUSAGE_URL = "https://commons.wikimedia.org/w/api.php?action=query&prop=globalusage&format=json&titles="

IMAGES = json.loads(open("images.json").read())


def number_of_usages(image):
    dict = requests.get(GLOBALUSAGE_URL + image.title()).json()["query"]["pages"]
    page_id = requests.get(GLOBALUSAGE_URL + image.title()).json()["query"]["pages"].keys()[0]
    return len(dict[page_id]["globalusage"])


def compute_criteria(image, with_usage):
    # Init
    img = image.title()
    if img not in IMAGES:
        IMAGES[img] = {}
    # Google
    if "Google" not in IMAGES[img]:
        IMAGES[img]["Google"] = "Google" in img
    # Usage
    if with_usage and "Usage" not in IMAGES[img]:
        IMAGES[img]["Usage"] = number_of_usages(image)
    # QI/VI/FP and partnership
    if "Featured" not in IMAGES[img]:
        IMAGES[img]["Featured"] = False
        IMAGES[img]["Valued"] = False
        IMAGES[img]["Quality"] = False
        IMAGES[img]["Partnership"] = False
        for category in image.categories():
            IMAGES[img]["Featured"] = IMAGES[img]["Featured"] or category.title() == COMMONS_FP_CATEGORY
            IMAGES[img]["Valued"] = IMAGES[img]["Valued"] or category.title() == COMMONS_VI_CATEGORY
            IMAGES[img]["Quality"] = IMAGES[img]["Quality"] or category.title() == COMMONS_QI_CATEGORY
            IMAGES[img]["Partnership"] = IMAGES[img]["Partnership"] or category.title() in SUPPORTED_CATEGORIES
    return IMAGES[img]


def images_of(category):
    return [img for img in page.Category(COMMONS, category).members(namespaces=FILE_NAMESPACE)]


def xor(b1, b2):
    return (b1 and not b2) or (b2 and not b1)


def with_label(c):
    return c["Featured"] or c["Valued"] or c["Quality"]


def compare_criteria(c1, c2, with_usage):
    if xor(c1["Google"], c2["Google"]):
        return c2["Google"]
    if xor(with_label(c1), with_label(c2)):
        return with_label(c2)
    if xor(c1["Partnership"], c2["Partnership"]):
        return c2["Partnership"]
    if with_usage:
        return c1["Usage"] < c2["Usage"]
    return False


def best_image(category, with_usage):
    images = images_of(category)
    if len(images) == 0:
        return None
    # Initiatization
    best_image = images[0]
    best_criteria = compute_criteria(images[0], with_usage)
    # Finding the best
    for image in images:
        current_criteria = compute_criteria(image, with_usage)
        if compare_criteria(best_criteria, current_criteria, with_usage):
            best_criteria = current_criteria
            best_image = image
    return best_image


def generated_code(category_name, with_usage, width=True):
    image = best_image(category_name, with_usage)
    with open("images.json", "w") as file:
        data = json.dumps(IMAGES, indent=2)
        file.write(data)
    if image is None:
        return None
    elif width:
        return {
            "Title": image.title(),
            "Image": image.get_file_url(url_width=IMAGE_WIDTH),
            "URL": image.full_url(),
            "debug": IMAGES
        }
    else:
        return {
            "Title":  image.title(),
            "Image": image.get_file_url(url_height=IMAGE_HEIGHT),
            "URL": image.full_url()
        }


def subcategories(category_name, flattening=False):
    if flattening:
        result = []
        for category in page.Category(COMMONS, category_name).subcategories():
            subs = [cat for cat in category.subcategories()]
            if len(subs) == 0:
                result.append(category)
            else:
                for subcategory in subs:
                    result.append(subcategory)
        return result
    else:
        return [category for category in page.Category(COMMONS, category_name).subcategories()]


def generate_gallery(category_name, with_usage, flattening=False):
    HTML_gallery = ""
    WIKI_gallery = "<gallery mode=\"packed\">"
    categories = subcategories(category_name, flattening)
    if len(categories) == 0:
        # Feedback when there are no sub categories
        HTML_gallery = '<p>No subcategory in {}</p>'.format(category_name)
    for category in categories:
        code = generated_code(category.title(), with_usage, False)
        if code:  # generated_code may return None value
            HTML_gallery = HTML_gallery + "<img src=\"" + code["Image"] + "\" height=\"" + str(IMAGE_HEIGHT) + "\">"
            WIKI_gallery = WIKI_gallery + "\n" + code["Title"] + "|[[:" + category.title() + "|" + category.title()[9:] + "]]"
    WIKI_gallery = WIKI_gallery + "\n</gallery>"
    return [Markup(HTML_gallery), WIKI_gallery]


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('view_index.html')


@app.route('/gallery/', methods=['GET', 'POST'])
def gallery():
    gallery = {'category_name': '', 'code_generated': '', 'with_usage': False}
    if request.method == 'POST':
        gallery['category_name'] = request.form['category']

        gallery['with_usage'] = "with_usage" in request.form
        gallery['flattening'] = "flattening" in request.form
        generated = generate_gallery(gallery['category_name'], gallery['with_usage'],
                                     gallery['flattening'])
        gallery['HTML'] = generated[0]
        gallery['WIKI'] = generated[1]
    else:
        # GET
        pass
    return render_template('view_gallery.html', **gallery)


@app.route('/image', methods=['GET', 'POST'])
def image():
    gallery = {'category_name': '', 'code_generated': '', 'with_usage': False}
    if request.method == 'POST':
        # POST method
        gallery['category_name'] = request.form['category']
        gallery['with_usage'] = "with_usage" in request.form
        generated = generated_code(gallery['category_name'], gallery['with_usage'])
        gallery['image_name'] = generated['Title']
        gallery['image_url'] = generated['Image']
        gallery['file_url'] = generated['URL']
        gallery['debug'] = generated['debug']
    else:
        # GET
        pass
    return render_template('view_image.html', **gallery)


@app.route('/json', methods=['GET'])
def json_endpoint():
    """Serve the JSON file.

    If request is used with ?fmt=html, the response is returned to be pretty print in HTML
    Otherwise just sends the content of the JSON file.
    """
    response = ''
    if request.method == 'GET':
        with open('images.json', mode='r') as f:
            images = json.loads(f.read())
            json_content = json.dumps(images, indent=4)
            if request.args.get('fmt', '') == 'html':
                response = '<pre>{}</pre>'.format(json_content)
            else:
                response = json_content
    else:
        # Method not allowed
        abort(405)
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4242)
