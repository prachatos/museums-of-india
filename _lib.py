#!/usr/bin/env python
# coding: utf-8
import urllib.request
import requests
from lxml import html
import pandas as pd
import re

BASE_URI = "http://museumsofindia.gov.in"

def gen_museum_list(museum):
    REPOS_URI = BASE_URI + "/repository/search/" + museum + "/collection/object_type"
    init = 1
    stride = 50
    runs = 0
    url_list = []
    coll_list = []
    while runs < 50:
        composed_uri = REPOS_URI + '/' + str(init) + '/' + str(stride)
        tree_m = html.fromstring(requests.get(composed_uri).content)
        all_titles = tree_m.find_class('title_bg')
        if not all_titles:
            break
        for t in all_titles:
            coll_list.append(str(t.text_content()).split("(")[0].strip())
            lim = int(str(t.text_content()).split("(")[1].strip().replace(")", "").split(":")[1])
            url_list.append([BASE_URI + str(t.cssselect('a')[0].get('href')).rsplit("/", 1)[0] + "/" + str(lim + 10), lim])
        init += stride
        stride = 1
        runs += 1
    df = pd.DataFrame(url_list, index=coll_list, columns=["url", "entries"])
    df.index.name = "name"
    df.to_csv(open(museum + ".csv", "w+"))
    return


def csv_for_coll(coll_name, coll_url, to=0):
    # Reason why a "from" parameter isn't supported:
    # The parameters for the website have the pattern x/y/z
    # This indicates open the y_th page where each page
    # contains z entries, which makes having a to complicated
    # without accessing multiple pages. I still don't know what 
    # x does so maybe that's needed to implement this
    if not to:
        to = int(coll_url.rsplit("/", 1)[1])
    else:
        coll_url = coll_url.rsplit("/", 1)[0] + "/" + str(to)
    page = requests.get(coll_url)
    tree = html.fromstring(page.content)
    link_p = tree.find_class('user')
    link_new = [link_p[i] for i in range(len(link_p)) if i % 2 == 0] #remove dupes
    k = 0
    data = []
    for l in link_new:
        cur_entry = dict()
        uri = BASE_URI + "/" + l.cssselect('a')[0].get('href')
        page = requests.get(uri)
        tree = html.fromstring(page.content)
        txts = tree.find_class('maroon_txt')
        for e in txts:
            key = e.cssselect('td')[0].text_content()
            val = e.getnext().cssselect('td')[0].text_content()
            cur_entry[str(key)] = str(val)
        data.append(cur_entry)
        k += 1
    pd_df = pd.DataFrame(data)
    pd_df.to_csv(re.sub(r"\s+", '-', coll_name) + "-" + str(to) + ".csv", index=False)
