SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:


.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: unit_tests ## 🔍 Run unit tests
unit_tests:
	pytest -v exptools_demo/tests/unit_tests

.PHONY: integration_tests ## 🔗 Run integration tests
integration_tests:
	pytest -v exptools_demo/tests/integration_tests

.PHONY: functional_tests ## ⚙️ Run functional tests
functional_tests:
	behave exptools_demo/tests/functional_tests/features

.PHONY: tests ## 🚦 Run all tests
tests:
	make unit_tests && make integration_tests && make functional_tests

.PHONY: instrument ## 🔬 Start instrument server
instrument:
	cd instrument_server && uvicorn main:app --reload --port=8000

.PHONY: instrument_test ## 🔬 Start instrument server for testing
instrument_test:
	cd instrument_server && uvicorn main:app --reload --port=8001

