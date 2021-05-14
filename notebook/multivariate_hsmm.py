#%%
import sys
sys.path.append('..')
from src.agent import Agent
#%%

from plotnine import *
import numpy as np
import pandas as pd
import umap
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

phoneme_path = "../data/phonemes.csv"
poisson_path = "../data/poisson.csv"
tmat_path = "../data/tmat.csv"
scale_path = "../data/scales.csv"
startprob_path = "../data/startprob.csv"
states = pd.read_csv(phoneme_path, sep=",").to_numpy()[:, 0]

df = pd.read_csv(phoneme_path, sep=",")
phoneme = df.to_numpy()[:, 0]
features = df.to_numpy()[:, 1:]
features = SimpleImputer(missing_values=np.nan, strategy='mean').fit_transform(features)
features = StandardScaler().fit_transform(features)

import umap

"umap":
    "n_components": 2,
    "random_state": 42,
    "n_neighbors": 6
    min_dist: 0.24041677639819287
scale: 0.6299924747454009
u_duration: 9
w_duration: 3



umap_params = {
    "n_components": 2,
    "random_state": 42,
    # "n_neighbors": study.best_params["n_neighbors"],
    # "min_dist": study.best_params["min_dist"],
}
means = umap.UMAP(**umap_params).fit_transform(features)
means = StandardScaler().fit_transform(means)
df = pd.DataFrame({"states":states, "x1": means[:, 0], "x2": means[:, 1]})
(ggplot(df, aes(x='x2', y='x1', color='states'))
 + geom_point()
)
#%%
n_state, n_dim = means.shape
scales = np.array([np.identity(n_dim), np.identity(n_dim), np.identity(n_dim)])


#%%
from hsmmlearn.hsmm import MultivariateGaussianHSMM
#%%
import numpy as np
# 3つの状態があり、4次元
means = [[0.,0.,0.,0.],[5.,5.,5.,5.], [10.,10.,10.,10.]]
# これが共分散行列になっている
scales = np.array([np.identity(4), np.identity(4), np.identity(4)])
# ポワソン
durations = np.array([
    [0.1, 0.0, 0.0, 0.9],
    [0.1, 0.0, 0.9, 0.0],
    [0.1, 0.9, 0.0, 0.0]
])
tmat = np.array([
    [0.0, 0.5, 0.5],
    [0.3, 0.0, 0.7],
    [0.6, 0.4, 0.0]
])

print(means)
print(scales)
print(durations)
print(tmat)

# %%
