SRC_DIR=binalyzer_template_provider
TEST_DIR=tests

export PYTHONPATH=.

all:

install-antlr4:
	(mkdir -p ~/antlr4 && \
	curl https://www.antlr.org/download/antlr-4.8-complete.jar -o ~/antlr4/antlr-4.8-complete.jar)

generate-xml-parser:
	cd $(SRC_DIR)/generated && rm -f XMLLexer.py \
					XMLParser.py \
					XMLParserListener.py
	mkdir -p $(SRC_DIR)/generated && \
	java -jar ~/antlr4/antlr-4.8-complete.jar \
		 -Dlanguage=Python3 \
		 resources/XMLLexer.g4 \
		 resources/XMLParser.g4 && \
	mv resources/*.py $(SRC_DIR)/generated && \
	rm resources/*.interp resources/*.tokens

sloc:
	sloccount --duplicates --wide --details $(SRC_DIR) | fgrep -v .git > sloccount.sc || :

test: generate-xml-parser
	python3 -m pytest -v tests --cov=$(SRC_DIR) --cov-report html:cov_html

flakes:
	pyflakes $(SRC_DIR) > pyflakes.log || :

lint:
	pylint $(SRC_DIR) \
		--rcfile=pylint.rc \
		--output-format=parseable --reports=y > pylint.log || :

clone:
	clonedigger --cpd-output $(SRC_DIR) || :

package: generate-xml-parser
	python3 setup.py sdist bdist_wheel


upload-to-test-pypi: package
	python3 -m twine upload --repository testpypi dist/*

upload-to-pypi: package
	python3 -m twine upload --repository pypi dist/*

clean:
	(cd $(SRC_DIR)/generated && rm -f XMLLexer.py \
		XMLParser.py \
		XMLParserListener.py)
	(rm -rf resources/*.interp \
		resources/*.tokens \
		pyflakes.log \
		pylint.log \
		test.log \
		sloccount.sc \
		output.xml \
		coverage.xml \
		xunit.xml \
	 	*.egg-info \
	 	.pytest_cache \
		docs/_build \
	 	build \
	 	dist \
		cov_html \
		.coverage)

.PHONY: all install-antlr4 generate-xml-parser clean sloc test flakes lint clone package install-from-test-pypi upload-to-test-pypi upload-to-pypi
