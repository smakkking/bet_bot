from manage import BOOKMAKER_OFFSET, ALL_POSTS_JSON_PATH
import json

def main(betting_array) :
    # в кач входных данных - результат работы scan_database.main()
    with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
        data = json.load(last_posts_json)
    for peruser_data in betting_array :
        for group in peruser_data['groups'] :
            data[]
    