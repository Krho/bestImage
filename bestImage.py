#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mwclient

COMMONS_SITE_URL = 'commons.wikimedia.org'
SITE =  mwclient.Site(COMMONS_SITE_URL)

FILE_NAMESPACE = 6

COMMONS_QI_CATEGORY = 'Category:Quality images'
COMMONS_FP_CATEGORY = 'Category:Featured pictures on Wikimedia Commons'
COMMONS_VI_CATEGORY = 'Category:Valued images sorted by promotion date'

def isGoogle(image):
    return "Google" in image["name"]

def isPartner(image):
    # api.php?action=query&titles=Image:Commons-logo.svg&prop=templates
    return False #TODO

def isQuality(image):
    return False or image["quality"] or image["featured"] or image["valued"]

def density_of(image):
    return 1
    # return image.size / (image.height * image.width)

def compute_criteria(image):
    return [isGoogle(image), isQuality(image), density_of(image)]

def compare_criteria(criteria1, criteria2):
    if xor(criteria2[0],criteria2[0]): # Only one of them is Google
        return criteria2[0]
    elif xor(criteria2[1],criteria1[1]): # Only one of them is quality
        return criteria2[1]
    else: # Smallest density wins
        return criteria2[2] > criteria1[2]

def xor(bool1, bool2):
    return (bool1 and not bool2) or (bool2 and not bool1)

def collect_info(img):
    image = {}
    image["name"] = img.page_title
    cats = [cat for cat in img.categories()]
    image["featured"] = False
    image["valued"] = False
    image["quality"] = False
    for cat in cats:
        image["featured"] = image["featured"] or cat.name == COMMONS_FP_CATEGORY
        image["valued"] = image["valued"] or cat.name == COMMONS_VI_CATEGORY
        image["quality"] = image["quality"] or cat.name == COMMONS_QI_CATEGORY
    return image

def best_image(category):
    # Initiatization
    images = [collect_info(img) for img in SITE.Categories[category.decode("utf8")] if img.namespace==FILE_NAMESPACE]
    best_criteria = compute_criteria(images[0])
    best_image = images[0]
    # Finding the best
    for image in images:
        current_criteria = compute_criteria(image)
        if compare_criteria(best_criteria, current_criteria):
            best_criteria = current_criteria
            best_image = image
    return best_image["name"]

print "best image"
print best_image("Musée Saint-Raymond, Ra 73e").encode("utf8")
