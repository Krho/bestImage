# -*- coding: utf-8 -*-
from flask import (
    Flask,
    render_template,
    request)
import json
import pywikibot
from pywikibot import page

app = Flask(__name__)

COMMONS = pywikibot.Site('commons', 'commons')
FILE_NAMESPACE = 6
IMAGE_WIDTH = 300
COMMONS_QI_CATEGORY = 'Category:Quality images'
COMMONS_FP_CATEGORY = 'Category:Featured pictures on Wikimedia Commons'
COMMONS_VI_CATEGORY = 'Category:Valued images sorted by promotion date'
SUPPORTED_CATEGORIES = [u'Category:Supported by Wikimedia AU‎', u'Category:Supported by Wikimedia CH‎',
u'Category:Supported by Wikimedia Deutschland‎', u'Category:Supported by Wikimedia France',
u'Category:Supported by Wikimedia Italia‎', u'Category:Supported by Wikimedia UK',
u'Category:Supported by Wikimedia Österreich‎ ', u'Category:Media supported by Wikimedia France']
# IMAGES = json.loads(open("images.json").read())
IMAGES = {}

def compute_criteria(image):
    # Init
    img = image.title()
    if img not in IMAGES:
        IMAGES[img] = {}
    # Google
    if "Google" not in IMAGES[img]:
        IMAGES[img]["Google"] = "Google" in img
    # QI/VI/FP and chapter
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
        with open("images.json", "w") as file:
            data = json.dumps(IMAGES, indent=2)
            file.write(data)

    return IMAGES[img]

def images_of(category):
    return [img for img in page.Category(COMMONS, category).members(namespaces=FILE_NAMESPACE)]

def xor(b1, b2):
    return (b1 and not b2) or (b2 and not b1)

def with_label(c):
    return c["Featured"] or c["Valued"] or c["Quality"]

def compare_criteria(c1, c2):
    if xor(c1["Google"], c2["Google"]):
        return c2["Google"]
    if xor(with_label(c1), with_label(c2)):
        return with_label(c2)
    return c2["Partnership"]

def best_image(category):
    images = images_of(category)
    if len(images) == 0:
        return None
    # Initiatization
    best_image = images[0]
    best_criteria = compute_criteria(images[0])
    # Finding the best
    for image in images:
        current_criteria = compute_criteria(image)
        if compare_criteria(best_criteria, current_criteria):
            best_criteria = current_criteria
            best_image = image
    return best_image

def generated_code(category_name):
    image = best_image(category_name)
    return [image.title(), image.get_file_url(url_width=IMAGE_WIDTH), image.full_url(), IMAGES]

@app.route('/', methods=['GET', 'POST'])
def index():
    gallery = {
        'category_name': '',
        'code_generated': ''
    }
    if request.method == 'POST':
        # POST method
        gallery['category_name'] = request.form['category']
        generated =  generated_code(gallery['category_name'])
        gallery['image_name'] = generated[0]
        gallery['image_url'] = generated[1]
        gallery['file_url'] = generated[2]
        gallery['debug'] = generated[3]
    else:
        # GET
        pass
    return render_template('view_image.html', **gallery)


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=4242)
