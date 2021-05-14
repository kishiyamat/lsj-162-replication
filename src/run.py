# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## 促音便
#
# ## ToDo
#
# phonetic minimality を明示的に表せる
#
# * 規則・制約なしに再現できるか. durationで上がるはず
#     -  kuwu + ta -> ku?ta
#     -  kuwu + ta -> koota
# * u_trinsic と duration の交互作用はあるか -> 心理言語学の予測
#     - /u/ の intrinsic time を制御
#     - 知識としてあるか。交互作用が肝心。
# * どのようなタブローが作成出来るか -> 音韻論の candidates
#
# ## Future Studies
#
# - generation のときの調音結合などをいじる
#     - 経済性の組み込みで koota なども出てくるはず。
# - /sd/ を制御(まずは正確に聞き取れるようになるまで)
# - 入力(産出)にはノイズが乗る
# - パラメータのdir は chmod 777 しておく

# ## Materials and Methods
#
# * モデルを複数作成
#     - データ: 産出・知覚する音声
#     - モデル: 産出・知覚が依存する知識
# * 一回サイクルする
# * 100回実行してサンプリング
# * 50回回して統計を取る

import sys

try:
    exp_id = sys.argv[1]
except:
    print("実験idを引数に渡してください。デフォルトの1を実行します。")
    # もしnotebook上で編集する場合は以下を編集
    exp_id = 1

# +
# %load_ext autoreload
# %autoreload 2

from hydra.experimental import initialize, compose
from agent import Agent
# https://hydra.cc/docs/next/experimental/compose_api

with initialize(config_path="../artifact"):
    config = compose(config_name="config.yml")

with initialize(config_path="../param"):
    exp_config = compose(config_name=f"exp{exp_id}.yml")

agent_sample = Agent(config)
# -

# ### u の duration を操作して実験
#
# - 産出の時の duraion の変化か
# - 知識として学習されないのか。されるならどう問題が起きるのか
# - koota, ka?ta, kawuta の割合を調査

# +
from itertools import product
import numpy as np
from collections import Counter
from joblib import Parallel, delayed

trial = list(range(exp_config.n_trial))
durations = exp_config.durations
switches = exp_config.switches
n_iter = list(range(exp_config.n_iter))
target = exp_config.target
delete = exp_config.delete # 削除する対象の音素

# 高速化
# ベースラインの速度測定: 808.2551259994507[sec]
## 測定: https://qiita.com/fantm21/items/3dc7fbf4e935311488bc
# 並列化: 437.15462827682495[sec]
# assertやumapをinit時に実施: 12.637521743774414[sec]

import time

def perception(prod, perc, symbol):
    phoneme, obs, states = prod.production(symbol)
    obs = np.array(obs).astype('double')
    phoneme_hat, obs, states_hat = perc.perception(obs)
    return phoneme_hat

results_list = []
for t in trial:
    # start: 一回のiterにXs かかる。これから終わる時間を推定する
    start = time.time()

    if t % 5 == 0:
        print(f"trial: {t}")
    for duration, switch in product(durations, switches):
        # duration を制御
        with initialize(config_path="../artifact"):
            config_u_reduced = compose(config_name="config.yml", overrides=[f"{delete}_duration={duration}"])
            
        a = Agent(config_u_reduced)
        if switch == "production":  # production のときのみ短くする
            with initialize(config_path="../artifact"):
                config = compose(config_name="config.yml")
            b = Agent(config)
        elif switch == "update":
            b = Agent(config_u_reduced)
        else:
            raise ValueError

        perceptions = Parallel(n_jobs=-1)(delayed(perception)(prod=a, perc=b, symbol=target) for n in n_iter)

        settings =  {
            "trial": t,
            f"{delete}_duration": duration,
            "intrinsic": switch,
            "n_kawuta": perceptions.count("kawuta"),
            "n_kawta": perceptions.count("kawta"),
            "n_kaQta": perceptions.count("kaQta"),
            "n_kauta": perceptions.count("kauta"),
            "n_koota": perceptions.count("koota"),
            "counter": Counter(perceptions),
        }
        results_list.append(settings)
        print(Counter(perceptions))
        
    # end
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    # end
# -

import pandas as pd
results = pd.DataFrame(results_list)

# ## 結果
#
# ### Intrinsic
#
# ここではデータの吐き出しのみ。整形とグラフ化、統計分析は results.Rmd を参照
#
# 1. 他の音便変化の比較
# 1. そもそもどのくらい正しい知覚がされるか
# 1. 促音便の頻度
# 1. 内在時間長の表現方法の違い

# +
# 分析は results.md の
intrinsic = results[["trial", f"{delete}_duration", "intrinsic", "n_kawuta", "n_kawta","n_kaQta", "n_kauta", "n_koota"]]

intrinsic.to_csv(f'../artifact/intrinsic_{exp_id}.csv', index=False)
intrinsic.head()


# -

# ## タブロー
#
#
# ここではデータの吐き出しのみ。整形とグラフ化、統計分析は results.Rmd を参照
#
# 1. 認知的に妥当なモデルだけで Candidates は生成できる
# 1. その際、

def flatten_dict(count_i):
    flat = []
    count_dict_i = dict(count_i)
    for k, v in count_dict_i.items():
        flat += [k]*v
    return flat


# +
recognized = []
for cound_dict in results.counter.to_numpy():
    recognized += flatten_dict(cound_dict)

len(recognized) # 100*900 だから
# -

# https://stackoverflow.com/questions/31111032/transform-a-counter-object-into-a-pandas-dataframe
d = dict(Counter(recognized))
df = pd.DataFrame.from_dict(d, orient='index').reset_index()
candidate = df.rename(columns={'index': 'candidate', 0:'count'})
candidate.to_csv(f'../artifact/candidate_{exp_id}.csv', index=False)

# ## Referecnce
#
# - https://www.researchgate.net/figure/Statistics-on-the-Vowel-Formant-Frequenc_tbl1_300346463
# - https://slideplayer.com/slide/3359572/
# - https://www.fon.hum.uva.nl/rob/Courses/InformationInSpeech/CDROM/Literature/LOTwinterschool2006/speech.bme.ogi.edu/tutordemos/SpectrogramReading/cse551html/cse551/node38.html
