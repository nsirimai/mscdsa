PDFLATEX=pdflatex
LATEX=latex
BIBTEX=bibtex
MAIN=$(shell ls *.tex | cut -d'.' -f1)
VIEWER=evince

all: pdf

view: $(MAIN).pdf
	$(VIEWER) $(MAIN).pdf

clean: 
	/bin/rm -f *~ .*~ *.out *.idx *.bbl *.blg *.aux *.log *.toc *.nav *.snm *.vrb *.ini _region_.* *.run.xml *-blx.bib *.nlo *.lot *.lof *.ist *.glo *.brf *.ind *.fls *.ilg *.fdb_latexmk *.synctex.gz

.SUFFIXES: .tex .pdf



pdf: $(MAIN).tex
	$(PDFLATEX) $(MAIN).tex
	$(PDFLATEX) $(MAIN).tex
