# lsj-162-replication

日本言語学会第162回大会での研究の再現用リポジトリです。
モデルで定義した値とそのリンクは以下になります。

* [音素の分布](https://github.com/kishiyamat/lsj-162-replication/blob/main/data/phonemes.csv)
* [音素列の尤度](https://github.com/kishiyamat/lsj-162-replication/blob/main/data/tmat.csv)
* [持続時間](https://github.com/kishiyamat/lsj-162-replication/blob/main/data/poisson.csv)

以下の再現実験では `Docker` が必要になりますので、
[公式ページ](https://docs.docker.com/get-docker/)
からインストールするとコマンドが実行可能になります。

## 再現実験

本リポジトリをクローンしたのち、この`README.md`と同じ階層で
以下のコマンドを実行します。

```sh
docker build -t kishiyamat/lsj-162-replication .
docker run -it --rm kishiyamat/lsj-162-replication bash  # bash に入る
$ cd lsj-162-replication
$ make hypara   # ハイパーパラメータの設定
$ make exp1     # 促音便
$ make exp2     # ウ音便
$ make results  # グラフ描画
$ exit
$ docker ps
> CONTAINER ID        IMAGE                            COMMAND             CREATED             STATUS              PORTS               NAMES
> 93ad197fcfae        kishiyamat/lsj-162-replication   "bash"              5 seconds ago       Up 4 seconds                            friendly_wilson
$ docker cp 93ad197fcfae:/opt/app/lsj-162-replication/artifact/ artifact/
$ mv artifact/artifact/* artifact/ # 結果をコピーして終了
```

## ハイパーパラメータの設定

* [分布の分散やumapのハイパーパラメータの設定](https://github.com/kishiyamat/lsj-162-replication/blob/main/param/hyparam.yml)

## 引用

```
@inproceedings{kishiyama2021computational,
  author={岸山 健},
  title={音韻論的記述への計算モデルのアプローチ ---音便変化のモデリングによる検証---},
  pages={26--32},
  year={2021},
  journal = {日本言語学会第162回予稿集},
}
```
