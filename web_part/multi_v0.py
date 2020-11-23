import multiprocessing, time
import requests, json
import eventlet

from moduls.bet_manage import YandexAPI_detection


urls = [
    'https://sun9-76.userapi.com/impf/VtWlfBr60Rj5exk8flLGzjJPYJiD6FT8KOPbaQ/5FpDU_P4-Ak.jpg?size=762x353&quality=96&proxy=1&sign=c491b13044813e30e81c42e38bfc3b3b',
]

def func(url) :
    a = YandexAPI_detection(url)
    print(YandexAPI_detection.iam_token)
    b = a.text_detection(debug=True)
    print(f'text={b}!')
    #b = requests.get(url).status_code
    
    return (url, b)

if __name__ == "__main__":
    YandexAPI_detection.create_new_token()
    print(YandexAPI_detection.iam_token)
    dic = {}
    # sequence call
    #now1 = time.time()
    #r = []
    #for u in urls :
    #    a = YandexAPI_detection(u)
    #    r.append((u, a.text_detection()))

    #dic['sequence'] = {'value' : dict(r), 'sec' : time.time() - now1}

    # parallel call
    now1 = time.time()
    with multiprocessing.Pool(processes=len(urls)) as p :
        dic['parallel'] = {'value' : dict(p.map(func, urls)), 'sec' : time.time() - now1}

    with open(r'C:\GitRep\bet_bot\web_part\user_data\test.json', 'w') as f :
        json.dump(dic, f, indent=4)