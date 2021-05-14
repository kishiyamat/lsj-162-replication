hyprara:
	cd src; python hyparam.py
exp1:
	cd src; python run.py 1
exp2:
	cd src; python run.py 2
results:
	cd src; Rscript -e 'library(rmarkdown); rmarkdown::render("./results.Rmd")'
