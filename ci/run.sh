#!/bin/bash

set -x
set -e

if [ ! -z "$TRAVIS_TAG" ]
then
    sed -i 's/__tag__ = ""/__tag__ = "'${TRAVIS_TAG}'"/g' binalyzer_template_provider/__init__.py
    sed -i 's/__tag__ = ""/__tag__ = "'${TRAVIS_TAG}'"/g' setup.py
else
    sed -i 's/__tag__ = ""/__tag__ = "'0.0.7a${TRAVIS_BUILD_NUMBER}'"/g' binalyzer_template_provider/__init__.py
    sed -i 's/__tag__ = ""/__tag__ = "'0.0.7a${TRAVIS_BUILD_NUMBER}'"/g' setup.py
fi

if [ ! -z "$TRAVIS_BUILD_NUMBER" ]
then
    sed -i 's/__build__ = 0/__build__ = '${TRAVIS_BUILD_NUMBER}'/g' binalyzer_template_provider/__init__.py
    sed -i 's/__build__ = 0/__build__ = '${TRAVIS_BUILD_NUMBER}'/g' setup.py
fi

if [ ! -z "$TRAVIS_COMMIT" ]
then
    sed -i 's/__commit__ = \"0000000\"/__commit__ = \"'${TRAVIS_COMMIT::7}'\"/g' binalyzer_template_provider/__init__.py
fi

curl -O https://www.antlr.org/download/antlr-4.8-complete.jar
java -jar antlr-4.8-complete.jar \
        -Dlanguage=Python3 \
        resources/XMLLexer.g4 \
        resources/XMLParser.g4
mv resources/*.py binalyzer_template_provider/generated
rm antlr-4.8-complete.jar

pip3 install binalyzer-core

python3 -m pytest tests --cov=binalyzer_template_provider --cov-fail-under=20
