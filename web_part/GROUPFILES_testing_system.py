# здесь тестируем все модули по группам и букмекеркам
from manage import BET_PROJECT_ROOT
from moduls.bet_manage import YandexAPI_detection, LastGroupPost

from moduls.group_moduls import ExpertMnenie_group
import nltk, json, time

TEST_FILE = BET_PROJECT_ROOT + r'\web_part\user_data\test.json'

def testing_group(group_module) :
    YandexAPI_detection.create_new_token()
    post = LastGroupPost(group_module.WALL_URL)
    # сколько постов всего нужно получить
    N = 10
    count = 10
    # получаем 10 постов
    for i in range(N // count) :
        post.get(offset=i * count, count=count)
    lt = []
    for url in post.photo_list :
        a = YandexAPI_detection(url)
        text = a.text_detection()
        st = None
        for (tmp, parse) in group_module.BET_TEMPLATES :
            if (tmp(text.upper())) :
                st = parse(url, nltk.word_tokenize(text))
        if st != None :
            lt.append({
                'link' : url,
                'bet' : st.__json_repr__(),
            })
        else :
            lt.append({
                'link' : url,
                 'bet' : 'not'
            })
    return lt

if __name__ == "__main__":
    with open(TEST_FILE, 'w') as js :
        json.dump(testing_group(ExpertMnenie_group), js, indent=4)

