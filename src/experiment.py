class Experiment:
    def __init__(self, n_iteration):
        pass

    def run(self, n_iteration):
        # ### Model
        # kuwu +ta -> katta の各データを表現させるため、
        # IPAを参考にfeatureの表を作ってPCAで一次元に圧縮して「平均」、つまりP(S|c)のmuとする。
        # sd は指定できないので要因とする。
        results = []
        # TODO: n_iter*要因でデカルト積をとればネストが一回で済む。
        for i in range(n_iteration):
            # 要因が増えたときはここで
            # ここ adversarial point
            production = self.production("kawuta")
            perception = self.model.decode(production)
            results.append(perception)
    pass
