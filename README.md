# Museums of India
This tool can be used to download data from the Museums of India website in CSV format.

# Scripts
This repository has 3 scripts - one for generating list of all museums (not neccessary to use), one for generating collections for a set of museums and the third for actually downloading collections given a CSV file.

# Installation
- Python 3.6
- Clone repo
- pip install -r requirements.txt 

# Generating list of museums

- *python gen_museums.py <optional filename>*
- The file always saves to the files/ folder. This only needs to be run if the website adds more museums, as a default list is available at *files/all-museums.csv*

# Generating collections for specific museums

- This relies on the **config/museums.ini** file. The first parameter is the museum CSV generated in the first step and the second is a list of indices of museums to fetch data from.
- *python gen_coll_list.py*
- This generates a set of files using the ID field of the museum, all saved to *files/xyz.csv*. These files are required to actually generate CSV containing data.

# Generating CSV with data of items

- This relies on the **config/collections.ini** file. The first parameter is the collection CSV generated in the first step and the second is a list of indices of museums to fetch data from. Any CSV that contains *<index,collection_name,collection_url,max_to_fetch>* should work.
- *python gen_coll_data.py*
- This generates a set of CSVs that contain data for each collection of items.
