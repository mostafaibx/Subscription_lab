# Subscription Analytics - Makefile
# Simple commands for local dev and CI

.PHONY: all install generate load dbt-deps dbt-build build clean help

# Default target
all: build

# Install all Python dependencies
install:
	pip install -q -r requirements.txt

# Generate synthetic data
generate:
	python data_generation/generate.py

# Load CSVs into DuckDB
load:
	python scripts/load_duckdb_raw.py

# Install dbt packages
dbt-deps:
	cd warehouse && dbt deps

# Run dbt models + tests
dbt-build:
	cd warehouse && dbt build

# Full pipeline: install → generate → load → dbt
build: install generate load dbt-deps dbt-build
	@echo "✓ Full build complete"

# Clean generated artifacts
clean:
	rm -rf data_generation/output/*.csv
	rm -rf warehouse/target
	rm -rf warehouse/logs
	rm -f warehouse/warehouse.duckdb
	rm -f warehouse/warehouse.duckdb.wal
	@echo "✓ Cleaned artifacts"

# Show available commands
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build      Full pipeline (default): install → generate → load → dbt build"
	@echo "  install    Install all Python dependencies"
	@echo "  generate   Generate synthetic data"
	@echo "  load       Load CSVs into DuckDB"
	@echo "  dbt-deps   Install dbt packages"
	@echo "  dbt-build  Run dbt models and tests"
	@echo "  clean      Remove generated artifacts"
	@echo "  help       Show this message"
