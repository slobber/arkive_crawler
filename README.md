# arkive_crawler
Download all photo and video from arkive.org

The arkive.org will close at Feb. 15, 2019. 
This crawler will download all spices content (factsheets, photos, videos) for storage them in local.

The total count of spices is 16053. I pull data following [this index file](https://search.arkive.org/solr/live/discover?rows=20000&facet.limit=-1&json.nl=map&q=doctype%3Aspecies&facet=true&wt=json) (This file is downloaded as arkive.json, it's 25mb+).

# Usage
1. run `python split.py` to split the data to smaller sets in `data` folder.
2. Install dependencies through `pip install -r requirement.txt`
3. Run `python main.py [start_file_index] [end_file_index]`, the file_index are the seq no of files in `data` folder, if you don't assign the indices, it will from first file to last file.
4. You will got contents in `output` folder.

# PS
1. The video files maybe large than 100mb+ and total data is 357GB, so the download progress may be very slowly.
2. You can rerun the script, it will only download the rest parts without the resources that are downloaded.

