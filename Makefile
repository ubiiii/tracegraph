PYTHON ?= python3

.PHONY: install install-dev test prepare-demo build-graph retrieve answer evaluate ablations report

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,embeddings,pretty]"

test:
	pytest

prepare-demo:
	$(PYTHON) -m tracegraph.cli prepare-demo

build-graph:
	$(PYTHON) -m tracegraph.cli build-graph --config configs/default.yaml

retrieve:
	$(PYTHON) -m tracegraph.cli retrieve --question "What decision did we make about data retention, and which compliance clause justified it?" --config configs/retrieval/bm25_graph.yaml

answer:
	$(PYTHON) -m tracegraph.cli answer --question "What decision did we make about data retention, and which compliance clause justified it?" --config configs/retrieval/bm25_graph_callbacks.yaml

evaluate:
	$(PYTHON) -m tracegraph.cli evaluate --config configs/evaluation/demo.yaml

ablations:
	$(PYTHON) -m tracegraph.cli ablations --config configs/evaluation/demo.yaml

report:
	$(PYTHON) -m tracegraph.cli report --results-dir data/outputs/runs/latest
