import multiprocessing, time
import requests, json
import eventlet, functools

from moduls.bet_manage import YandexAPI_detection


urls = [
    'https://sun9-76.userapi.com/impf/VtWlfBr60Rj5exk8flLGzjJPYJiD6FT8KOPbaQ/5FpDU_P4-Ak.jpg?size=762x353&quality=96&proxy=1&sign=c491b13044813e30e81c42e38bfc3b3b',
    'https://sun9-21.userapi.com/impg/Oz6stMy2Fq_oQ1BHH5X4xdubkmVCWcnc_aFwxQ/oWzauTFNDhc.jpg?size=489x437&quality=96&proxy=1&sign=e2f28c88d76e90792c502208b4c24391',
    'https://sun9-12.userapi.com/impg/y3uYT5hzrWWnMOd4mMnXSwV2YH4EQIeQvFBSQQ/J7r2zvGtXJI.jpg?size=1080x607&quality=96&proxy=1&sign=0ccc803741a426d385e25b7c45c29f97',
    'https://sun9-39.userapi.com/impg/SIRFGd4ehgAedW8lLc-K_8yYYO6VlFAZNwoVFQ/S2Z18ZY2-F4.jpg?size=559x481&quality=96&proxy=1&sign=7591e83ac5dc897ffbd63c5705ab544a',
    'https://sun9-72.userapi.com/impg/TO3itswmgqeklrHkQQi0jYkr6q8ox-S9AvMufw/43fPfw80OKo.jpg?size=1080x666&quality=96&proxy=1&sign=de275fb81f842d16ada497fd530b9ade',
    'https://sun9-58.userapi.com/impg/Ge_wi4KvX97_Mo2AK1x_huPWt-wQIDfu68GFfQ/dbRl2qa06hc.jpg?size=1080x1005&quality=96&proxy=1&sign=f1ef399c50d1ec3561a12db5a0e1ab0b',
    'https://sun9-7.userapi.com/impg/wR6aLJ051JI4NyIGt8UO0XtX18KD0r-y3UA5Fg/7tR7ORAQ6Hw.jpg?size=1080x1015&quality=96&proxy=1&sign=853a28cb87415e2d715eb2f4ff954de3',
    'https://sun9-59.userapi.com/impg/fI9LE6p7O6ZkU26umjZPvuPPBYHya8zBPkqABQ/s3s3mh01_h0.jpg?size=1090x1006&quality=96&proxy=1&sign=d81b115621b15d44da598941bf006c85',
    'https://sun9-23.userapi.com/impg/p-KDl5trgkXA63I-8WRwtxSyCl_m8uUOJx0EnQ/wVJkbksLOVA.jpg?size=1080x998&quality=96&proxy=1&sign=df944fdfc6e4f527827f9702f07bd839',
    'https://sun9-35.userapi.com/impg/14X-alQvtBEBOezAaz8d6J92yI2cEyC14Cnwew/b-dLJ00Y7ac.jpg?size=493x441&quality=96&proxy=1&sign=f7c3ee73d805e3d7a52cd0013a03cc9f',
]

def func(t, url) :
    a = YandexAPI_detection(url, t)
    b = a.text_detection()
    return (url, b)


def parl(token, dic) :
    now1 = time.time()
    with multiprocessing.Pool(processes=len(urls)) as p :
        dic['parallel'] = {'value' : dict(p.map(functools.partial(func, token), urls)), 'sec' : time.time() - now1}

def seq(token, dic) :
    now1 = time.time()
    r = []
    for u in urls :
        a = YandexAPI_detection(u, token)
        r.append((u, a.text_detection()))
    dic['sequence'] = {'value' : dict(r), 'sec' : time.time() - now1}

if __name__ == "__main__":
    YandexAPI_detection.create_new_token()
    dic = {}

    seq(YandexAPI_detection.iam_token, dic)
    parl(YandexAPI_detection.iam_token, dic)

    dic['equal'] = True
    for x in dic['sequence']['value'].keys() :
        if dic['sequence']['value'][x] != dic['parallel']['value'][x] :
            dic['equal'] = False
     
    with open(r'C:\GitRep\bet_bot\web_part\user_data\test.json', 'w') as f :
        json.dump(dic, f, indent=4)

    