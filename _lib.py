#!/usr/bin/env python
# coding: utf-8
import urllib.request
import requests
from lxml import html
import pandas as pd
import re, os

BASE_URI = "http://museumsofindia.gov.in"

def gen_museum_list_new(museum):
    i = 1
    REPOS_URI = BASE_URI + "/repository/collection/fetchCategories?collectionType=ObjectType&pageNo="
    CONT_URI = BASE_URI + "/collection/fetchRecords?collectionType=ObjectType&collectionCategory="
    coll_list = []
    url_list = []
    while True:
        composed_uri = REPOS_URI + str(i) + "&museum=" + museum + "&category="
        page = requests.get(composed_uri)
        text_json = json.loads(str(page.content.decode("utf-8")))
        entries = len(list(text_json.keys()))
        print(entries)
        if entries == 0:
            break
        for t in text_json.keys():
            coll_list.append(t)
            url_list.append(CONT_URI + t + "&pageNo=1&museum=im_kol")
        i += 1
    
    df = pd.DataFrame(url_list, index=coll_list, columns=["url"])
    df.index.name = "name"
    df.to_csv(open(museum + ".csv", "w+"))
    return

def gen_museum_list(museum):
    REPOS_URI = BASE_URI + "/repository/search/" + museum + "/collection/object_type"
    init = 1
    stride = 50
    runs = 0
    url_list = []
    coll_list = []
    count = 0
    while runs < 50:
        composed_uri = REPOS_URI + '/' + str(init) + '/' + str(stride)
        tree_m = html.fromstring(requests.get(composed_uri).content)
        all_titles = tree_m.find_class('title_bg')
        if not all_titles:
            break
        for t in all_titles:
            count += 1
            coll_name = str(t.text_content()).split("(")[0].strip()
            lim = int(str(t.text_content()).split("(")[1].strip().replace(")", "").split(":")[1])
            url_t = BASE_URI + str(t.cssselect('a')[0].get('href')).rsplit("/", 1)[0] + "/" + str(lim + 10)
            url_list.append([coll_name, url_t, lim])
        init += stride
        stride = 1
        runs += 1
    df = pd.DataFrame(url_list, columns=["name", "url", "entries"])
    df.index.name = "index"
    os.makedirs("files", exist_ok=True)
    df.to_csv(os.path.join("files", museum + ".csv"))
    print("Writing to", os.path.join("files", museum + ".csv"))
    return count


def csv_for_coll(coll_name, coll_url, to=0, nodesc=False):
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
            if not (nodesc and "Description" in str(key)):
                cur_entry[str(key)] = str(val)
        cur_entry["url"] = uri
        data.append(cur_entry)
        k += 1
    pd_df = pd.DataFrame(data)
    os.makedirs("files", exist_ok=True)
    pd_df.columns = pd_df.columns.str.strip()
    pd_df.to_csv(os.path.join("files", re.sub(r"\s+", '-', coll_name) + "-" + str(to) + ".tsv"), index=False, sep="\t")
    print("Writing to", os.path.join("files", re.sub(r"\s+", '-', coll_name) + "-" + str(to) + ".tsv"))
    return len(data)
	
	
def gen_all_museums(fname="all-museums.csv"):
    tree_m = html.fromstring(requests.get(BASE_URI).content)
    title_root = tree_m.get_element_by_id('keywordMuseumId')
    if not len(title_root):
        return
    all_mus = title_root.cssselect('option')
    if not all_mus:
        return
    d = []
    count = 0
    for a in all_mus:
        if a.get("value").strip() != "all": # if there's an use case for this lmk
            d.append([str(a.text_content().strip()).replace('"', ''), a.get("value").strip()])
            count += 1
    pd_df = pd.DataFrame(d, columns=["name", "id"])
    pd_df.index.name = "index"
    os.makedirs("files", exist_ok=True)
    pd_df.to_csv(os.path.join("files", fname))
    print("Writing to", os.path.join("files", fname))
    return count

	
def gen_coll_from_csvlist(csvlist="all-museums.csv", indices=[]):
    df = pd.read_csv(os.path.join("files", csvlist))
    tot = 0
    for index, row in df.iterrows():
        if len(indices) == 0 or index in indices:
            tot += (gen_museum_list(row["id"]))
    return tot

	
def gen_data_from_csvlist(csvlist, indices=[], nodesc=False):
    df = pd.read_csv(os.path.join("files", csvlist))
    for index, row in df.iterrows():
        if index in indices:
            csv_for_coll(csvlist.split(".")[0] + "-" + row[1], row[2], row[3], nodesc)
