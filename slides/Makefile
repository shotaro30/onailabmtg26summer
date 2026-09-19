.PHONY: all clean
PYTHON := .venv/bin/python
VENV_STAMP := .venv/.richmedia-ready

all: $(VENV_STAMP)
	latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
	$(PYTHON) scripts/embed_richmedia.py build/main.pdf talk.pdf buildabstract-demo-1min.mp4 --page 12
	mkdir -p presentation
	cp talk.pdf buildabstract-demo-1min.mp4 presentation/

$(VENV_STAMP): requirements.txt
	test -x $(PYTHON) || uv venv .venv
	uv pip install --python $(PYTHON) -r requirements.txt
	touch $(VENV_STAMP)

clean:
	latexmk -C -outdir=build main.tex
