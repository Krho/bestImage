# -*- coding: utf-8 -*-
import re
import json
import pywikibot
from pywikibot import page

WIKTIONNAIRE = pywikibot.Site('fr', 'wiktionary')
WIKIPEDIA = pywikibot.Site('fr','wikipedia')
WIKIDATA = pywikibot.Site('wikidata', 'wikidata')
source = re.compile("{{source\|[\w|\{\{| |\}|é|.|&]+")
wAuthor = re.compile("{{w\|[\w| ]+}}")
gender = "P21"
cache = {
    "words":{},
    "authors":{}
    }

def sources(word):
    result={
        'Authors'=[]
    }
    text = page.Page(WIKTIONNAIRE, word).text
    templates = source.findall(text)
    for template in templates:
        #Authors are linked to wikipedia
        wikiAuthors = wAuthor.findall()
        for wikiAuthor in wikiAuthors:
            if wikiAuthor not in result["authors"]:
                result["authors"].add(wikiAuthor)
                genders = gender(wikiAuthor)
                if wikiAuthor not in cache["authors"]:
                    cache["authors"][wikiAuthor]=genders
                else:
                    cache["authors"][wikiAuthor].addAll(genders)
    return {word:result}

def gender(author):
    result = []
    wikiArticle = page.Page(WIKIPEDIA, author)
    if wikiArticle.exists():
        item = wikiArticle.data_item()
        if gender in item.claims:
            for claim in item.claims[gender]:
                if claim.getTarget() is not None:
                    result.add(claim.getTarget().id)
    return {author:{genders:result}}


