from flask import (
    Flask,
    render_template,
    request)
import pywikibot
from pywikibot import page

app = Flask(__name__)

COMMONS = pywikibot.Site('commons', 'commons')
FILE_NAMESPACE = 6

def is_google_art(image):
    return "Google" in image.title()

def compute_criteria(image):
    return [is_google_art(image)]

def images_of(category):
    return [img for img in page.Category(COMMONS, category).members(namespaces=FILE_NAMESPACE)]

def compare_criteria(c1, c2):
    return c2[0] and not c1[0]

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
    return [image.title(), image.get_file_url(url_width=300), image.full_url()]
#    return image.getImagePageHtml()
#    return 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/'+image+'/640px-'+image
#    return '<gallery name="{0}">42</gallery>'.format(category_name)


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
    else:
        # GET
        pass
    return render_template('view_image.html', **gallery)


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=4242)
