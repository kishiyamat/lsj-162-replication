# lsj-162-replication
日本言語学会第162回大会での研究の再現用リポジトリ

```sh
docker build -t kishiyamat/lsj-162-replication .
docker run -it --rm kishiyamat/lsj-162-replication bash  # bash に入る
$ cd lsj-162-replication
$ make hypara
$ make exp1
$ make exp2
$ make results
$ exit
$ docker ps
> CONTAINER ID        IMAGE                            COMMAND             CREATED             STATUS              PORTS               NAMES
> 93ad197fcfae        kishiyamat/lsj-162-replication   "bash"              5 seconds ago       Up 4 seconds                            friendly_wilson
$ docker cp 93ad197fcfae:/opt/app/lsj-162-replication/artifact/ artifact/
$ mv artifact/artifact/* artifact/ # 結果をコピーして終了
```
