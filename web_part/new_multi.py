from moduls.bet_manage import create_webdriver
from manage import ALL_POSTS_JSON_PATH

urls = ['aaa', 'bbb']

from joblib import Parallel, delayed

import json
with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
    data = json.load(last_posts_json)

def do_stuff(url):
    return data[url]

#Parallel(n_jobs=-1)(delayed(do_stuff)(url) for url in urls) #execute parallel for all urls

from multiprocessing import Pool

if __name__ == "__main__":
    pool = Pool(processes=2)
    print(list(pool.map(do_stuff, urls)))

