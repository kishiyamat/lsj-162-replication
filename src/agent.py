import numpy as np
import pandas as pd
import umap
from hsmmlearn.hsmm import MultivariateGaussianHSMM
from scipy.stats import poisson
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from omegaconf.dictconfig import DictConfig
from dataclasses import dataclass


@dataclass
class Agent:
    config: DictConfig

    def __post_init__(self):
        """
        u_reduction: デフォルトから引く値. 割合にしてintするほうが安全
        scale: デフォルトから引く値
        """
        self.phoneme_df = pd.read_csv("../data/phonemes.csv", sep=",")
        self.poisson_df = pd.read_csv("../data/poisson.csv", sep=",")
        self.tmat_df = pd.read_csv("../data/tmat.csv", sep=",")
        self.startprob_df = pd.read_csv("../data/startprob.csv", sep=",")
        self.means = self._means()
        assert self.well_formed
        # self.scale_path = "../data/scales.csv"

    @property
    def model(self):
        """
        [HSMMのチュートリアル][hsmm] を参照.
        [hsmm]: https://github.com/jvkersch/hsmmlearn/blob/master/docs/source/tutorial.rst
        こいつが Experiment の property を読めば良いのでは
        """
        # return GaussianHSMM(self.means, self.scales, self.durations, self.tmat)
        return MultivariateGaussianHSMM(self.means, self.scales, self.durations, self.tmat, self.startprob)

    def well_formed(self):
        states_phoneme = self.phoneme_df.to_numpy()[:, 0]
        states_poisson = self.poisson_df.to_numpy()[:, 0]
        states_tmat = self.tmat_df.to_numpy()[:, 0]
        assert len(set(states_phoneme)) == len(
            states_phoneme), f"{states_phoneme} is not unique"
        assert len(set(states_poisson)) == len(
            states_poisson), f"{states_poisson} is not unique"
        assert len(set(states_tmat)) == len(
            states_tmat), f"{states_tmat} is not unique"
        assert all(states_phoneme ==
                   states_poisson), f"{states_phoneme} and {states_poisson}"
        assert all(states_poisson ==
                   states_tmat), f"{states_poisson} and {states_tmat}"
        return True

    @property
    def states(self):
        return self.phoneme_df.to_numpy()[:, 0]

    def _means(self):
        """
        多次元は未対応だが、クラスを追加するか multinomial を作成して対応可能
        """
        phoneme = self.phoneme_df.to_numpy()[:, 0]
        features = self.phoneme_df.to_numpy()[:, 1:]

        features = SimpleImputer(
            missing_values=np.nan, strategy='mean').fit_transform(features)
        features = StandardScaler().fit_transform(features)
        # UMAP
        means = umap.UMAP(**self.config.umap).fit_transform(features)
        # means = PCA(n_components=self.umap_params.n_components).fit_transform(features)
        means = StandardScaler().fit_transform(means)
        return means

    @property
    def features(self):
        # phoneme = self.phoneme_df.to_numpy()[:, 0]
        # (n_cateagory, n_features)
        return self.phoneme_df.to_numpy()[:, 1:].astype('double')

    @property
    def startprob(self):
        # TODO: sd も要因にする
        # (n_cateagory, )
        return self.startprob_df.to_numpy()[:, 1].astype('double')

    @property
    def scales(self):
        n_state, n_dim = self.means.shape
        scales = np.array([np.identity(n_dim) for _ in range(n_state)])
        # TODO: sd も要因にする
        # sds = np.linspace(start=0, stop=3, num=10)
        # sds  # 音素間で統一
        return scales * self.config.scale

    @property
    def poisson_params(self):
        poisson_df = self.poisson_df
        poisson_arr = poisson_df.to_numpy()[:, 1]
        poisson_arr = np.where(
            self.states == "u", self.config.u_duration, poisson_arr)
        poisson_arr = np.where(
            self.states == "w", self.config.w_duration, poisson_arr)
        return poisson_arr

    @property
    def durations(self):
        """
        持続時間の分布のsdも確率的に生成させたほうが良さそう。
        20msを1としたとき、20, 100, 150, 200 あたりが
        ただし /u/ の「内在時間長」は「とりわけ」短い。
        poisson のつかいかたは [poisson] を参照
        [poisson]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html
        """
        eps = np.finfo(float).eps
        mu_range = np.arange(poisson.ppf(eps, min(self.poisson_params)),
                             poisson.ppf(1 - eps, max(self.poisson_params)))
        return np.array([poisson.pmf(mu_range, pa) for pa in self.poisson_params])

    @property
    def tmat(self):
        return self.tmat_df.to_numpy()[:, 1:].astype("float")

    def production(self, phonemes) -> np.array:
        """
        phonemes: kawuta
        returns: observations, states
        """
        n_state, n_dim = self.means.shape
        phoneme_idxs = [np.where(self.states == phoneme)[0][0]
                        for phoneme in phonemes]
        # durationは1はじまりなのに対して random.choiceは0はじまりなので1を足して合わせる
        observations, state_idxs = [], []
        for state in phoneme_idxs:
            duration = self.poisson_params[state]
            arr = self.model.emissions.sample_for_state(
                state, size=duration).reshape(-1, n_dim)
            observations.append(arr)
            state_idxs.extend([state] * duration)
        try:
            return phonemes, np.concatenate(observations), state_idxs
        except:
            print(observations)

    def perception(self, observations):
        """
        phonemes: kawuta
        returns: observations, states
        """
        # FIXME: koota -> kota
        state_hat_idxs = self.model.decode(observations)
        phonemes = self._rle_encode("".join(self.states[state_hat_idxs]))
        return phonemes, observations, state_hat_idxs

    @staticmethod
    def _rle_encode(data):
        # https://stackoverflow.com/questions/18948382/run-length-encoding-in-python
        encoding = ''
        prev_char = ''
        if not data:
            return ''

        for char in data:
            if char != prev_char:
                if prev_char:
                    encoding += prev_char
                prev_char = char
            else:
                continue
        else:
            encoding += prev_char
            return encoding
