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

# ## 前準備
#
# * 2次元に圧縮
# * Umap Algorithm と分散のパラメータチューニング
#     * 精度とバリエーション、分散の小ささの交互作用で最適化

# +
# %load_ext autoreload
# %autoreload 2

import sys
sys.path.append('..')
from src.agent import Agent
from omegaconf.dictconfig import DictConfig
from collections import Counter
import numpy as np
from plotnine import *
import numpy as np
import pandas as pd

# +
import optuna


def objective(trial):
    umap_params = {
        "n_components": trial.suggest_categorical('n_components', [2]),
        "random_state": trial.suggest_categorical('random_state', [42]),
        "n_neighbors": trial.suggest_int('n_neighbors', 2, 6),
        "min_dist": trial.suggest_uniform("min_dist", 0.1, 1),  # スケールしてるから1程度
    }
    u_duration = trial.suggest_categorical('u_duration', [0])
    # u_duration = trial.suggest_int('u_duration', 0, 9)
    w_duration = trial.suggest_categorical('w_duration', [3])
    scale = trial.suggest_uniform("scale", 0.1, 0.4)
    config_a = DictConfig({"umap": umap_params, "scale": scale,
                          "u_duration": u_duration, "w_duration": w_duration})
    config_b = DictConfig(
        {"umap": umap_params, "scale": scale, "u_duration": 9, "w_duration": 3})

    a = Agent(config_a)
    b = Agent(config_b)

    n_soku = 0
    # n_u = 0
    n_correct = 0
    perceptions = []
    n_iter = 100  # 精度が増すが計算コストも高くなる
    for n in range(n_iter):
        src = "kawuta"
        phoneme, obs, states = a.production(src)
        obs = np.array(obs).astype('double')
        phoneme_hat, obs, states_hat = b.perception(obs)
        perceptions.append(phoneme_hat)
        # n_correct += phoneme_hat == src  # u_durationが0のときに"kawuta"で最適化する必要はない。
        n_soku += phoneme_hat == 'kaQta'  # 音韻論の知識
        # n_u += phoneme_hat == 'kauta'  # 音韻論の知識

    print(Counter(perceptions))
    return n_soku*(1-scale)  # 0のときの促音便、ウ音便で最大化させる。ただしscale は少ないほどよい。


study = optuna.create_study(
    direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(objective, n_trials=100)
# -

umap_params = {
    "n_components": 2,
    "random_state": 42,
     "n_neighbors": study.best_params["n_neighbors"],
     "min_dist": study.best_params["min_dist"],
}
scale=study.best_params["scale"]
config =  DictConfig({"umap": umap_params, "scale": scale, "u_duration": 9, "w_duration": 3})
config

# +
agent = Agent(config)
means = agent.means
means_df = pd.DataFrame({"states": agent.states, "x1": means[:, 0], "x2": means[:, 1]})
means_df.to_csv('../data/means.csv', index=False)

(ggplot(means_df, aes(x='x2', y='x1', color='states'))
 + geom_point()
)
# -

# save them as yml
from omegaconf.dictconfig import DictConfig
from omegaconf import OmegaConf
yml_dir = "../hyparam/config.yml"
with open(yml_dir, "w" ) as f:
    OmegaConf.save(config=config, f=f.name)
    loaded = OmegaConf.load(f.name)
    assert config == loaded

# ## Load & sample

# +
from hydra.experimental import initialize, compose
# https://hydra.cc/docs/next/experimental/compose_api

with initialize(config_path="../hyparam"):
    config = compose(config_name="config.yml")
# -

config.umap

# +
agent = Agent(config)
means = agent.means
means_df = pd.DataFrame({"states": agent.states, "x1": means[:, 0], "x2": means[:, 1]})
means_df.to_csv('../data/means.csv', index=False)

(ggplot(means_df, aes(x='x1', y='x2', color='states'))
 + geom_point()
)
# -

agent.model.n_states

# +
n_sample = 100
sampled_means = []
for state_idx in range(agent.model.n_states):
    xy = np.array([agent.model.emissions.sample_for_state(state_idx) for _ in range(n_sample)])
    lab = np.array([agent.states[state_idx]]*n_sample).reshape(-1, 1)
    sampled_means.append(np.concatenate([lab, xy], axis=1))
    
sampled_means_arr = np.concatenate(sampled_means)
# -

sampled_means_df = pd.DataFrame({"state": sampled_means_arr[:, 0], "x": sampled_means_arr[:, 1], "y": sampled_means_arr[:, 2]})
sampled_means_df.to_csv('../data/sampled_means.csv', index=False)
