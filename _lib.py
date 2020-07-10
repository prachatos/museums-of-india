#!/usr/bin/env python
# coding: utf-8
import urllib.request
import requests
from lxml import html
import pandas as pd
import re, os, shutil

BASE_URI = "http://museumsofindia.gov.in"


def gen_coll_list(museum):
    i = 1
    count = 0
    REPOS_URI = "http://museumsofindia.gov.in/repository/collection/fetchCategories?collectionType=ObjectType&pageNo="
    CONT_URI = "http://museumsofindia.gov.in/repository/collection/fetchRecords?collectionType=ObjectType&collectionCategory="
    coll_list = []
    url_list = []
    while True:
        composed_uri = REPOS_URI + str(i) + "&museum=" + museum + "&category="
        page = requests.get(composed_uri)
        text_json = json.loads(str(page.content.decode("utf-8")))
        entries = len(list(text_json.keys()))
        count += entries
        if entries == 0:
            break
        for k, v in text_json.items():
            coll_list.append(k)
            url_list.append([CONT_URI + k + "&pageNo=1&museum=im_kol", int(v)])
        i += 1
    
    df = pd.DataFrame(url_list, index=coll_list, columns=["url", "count"])
    df.index.name = "name"
    os.makedirs("files", exist_ok=True)
    df.to_csv(os.path.join("files", museum + ".csv"))
    print("Writing to", os.path.join("files", museum + ".csv"))
    return count

def coll_meta_list(coll_name, coll_url, min_page=1, max_page=9999):
    cur_page_no = int(coll_url.split("pageNo")[1].split("&")[0].replace("=", ""))
    coll_url = coll_url.replace("pageNo="+str(cur_page_no), "pageNo="+str(min_page))
    cur_page_no = min_page
    data = []
    while True:
        page = requests.get(coll_url)
        text_json = json.loads(str(page.content.decode("utf-8",errors='replace')))
        entries = len(text_json["listOfResult"])
        data += (text_json["listOfResult"])
        cur_page_no += 1
        coll_url = coll_url.replace("pageNo="+str(cur_page_no-1), "pageNo="+str(cur_page_no))
        if entries < 16 or cur_page_no > max_page: break
    return data, min_page, cur_page_no - 1
    
def pic_for_record(record_no, img_url):
    r = requests.get(img_url, stream = True)
    with open(record_no+".jpg",'wb') as f:
        shutil.copyfileobj(r.raw, f)

def data_for_record(record_no):
    record_url = "http://museumsofindia.gov.in/repository/record/" + record_no
    page = requests.get(record_url)
    tree = html.fromstring(page.content)
    key = tree.cssselect('th')
    value = tree.cssselect('td')
    key_l = [k.text_content() for k in key]
    value_l = [v.text_content().replace("\r", "").replace("\n", "") for v in value]
    return dict(zip(key_l, value_l))

def data_for_coll(coll_name, clist, min_page=1, max_page=9999):
    data_list = []
    for c in clist:
        print("Downloading data for", c["recordIdentifier"])
        data_list.append(data_for_record(c["recordIdentifier"]))
    pd_df = pd.DataFrame(data_list)
    pd_df.to_csv(re.sub(r"\s+", '-', coll_name) + "-" + str(min_page) + "-" + str(max_page) + ".csv", index=False)

def image_for_coll(clist):
    data_list = []
    for c in clist:
        print("Downloading image for", c["recordIdentifier"])
        pic_for_record(c["recordIdentifier"], c["displayImage"])

def download_coll(coll_name, coll_url, min_page=1, max_page=9999, data=True, image=False):
    # first download meta info
    print("Downloading meta information about collection")
    clist, min_page, max_page = coll_meta_list(coll_name, coll_url, min_page, max_page)
    if data:
        data_for_coll(coll_name, clist, min_page, max_page)
    if image:
        image_for_coll(clist)
	
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
            tot += (gen_coll_list(row["id"]))
    return tot

	
def gen_data_from_csvlist(csvlist, indices=[], nodesc=False):
    df = pd.read_csv(os.path.join("files", csvlist))
    for index, row in df.iterrows():
        if index in indices:
            gen_coll_list(csvlist.split(".")[0] + "-" + row[1], row[2], row[3], nodesc)
