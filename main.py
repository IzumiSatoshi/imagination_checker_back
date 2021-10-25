import itertools
from flask import Flask, request
from flask.json import jsonify
from pymagnitude import Magnitude
from scipy import spatial
from waitress import serve


vectors = Magnitude('./chive-1.2-mc90.magnitude')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['POST'])
def api():
    json_dict = request.json
    word_list = json_dict['word_list']

    response = calc_score(word_list)

    return response


def calc_score(word_list):
    """
    単語リストからスコアを算出し、スコアとその内訳をjsonで返す
    """

    score_sum = 0
    breakdown_dict = dict()
    word_pair_list = list(itertools.combinations(word_list, 2))
    for idx, pair in enumerate(word_pair_list):
        distance = spatial.distance.cosine(
            vectors.query(pair[0]), vectors.query(pair[1])
        )
        # コサイン距離は0 ~ 2のはず。それを100点満点に変換した値をスコアとする。
        score = (distance / 2) * 100

        # socre_sumに加算
        score_sum += score

        # 内訳dictに入れる
        breakdown_dict[idx] = {
            'word1': pair[0],
            'word2': pair[1],
            'score': score,
        }

    # 合計スコアをペア数で割って平均スコアを求める
    score_mean = score_sum / len(word_pair_list)

    json_obj = jsonify({
        'score': score_mean,
        'breakdown': breakdown_dict
    })

    return json_obj


if __name__ == '__main__':
    print('start server')
    serve(app, host='0.0.0.0', port=5000)
