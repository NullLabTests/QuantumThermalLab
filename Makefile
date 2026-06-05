.PHONY: all run test lint clean report sweep

all: run

run:
	python run.py

run-bottleneck:
	python run.py --bottleneck

test:
	python -m pytest tests/ -v --tb=short

test-all:
	python -m pytest tests/ -v -x --tb=long

test-cover:
	python -m pytest tests/ --cov=qta --cov-report=term-missing

lint:
	python -m py_compile qta/*.py run.py run_qta_full_sim.py
	@echo "lint OK"

report:
	python run.py report

sweep:
	python run.py sweep --out outputs/sweep.csv

ci: test lint

clean:
	rm -rf outputs/ __pycache__/ .pytest_cache/
	find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete
	@echo "clean OK"
