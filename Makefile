bash:
	docker build -t kishiyamat/lsj-162-replication .
	docker run -it --rm kishiyamat/lsj-162-replication bash
hypara:
	cd src; python hyparams.py
exp1:
	cd src; python run.py 1
exp2:
	cd src; python run.py 2
results:
	cd src; Rscript -e 'library(rmarkdown); rmarkdown::render("./results.Rmd")'
	cd src; rm results.md
