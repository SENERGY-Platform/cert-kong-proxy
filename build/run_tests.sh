coverage run -m unittest discover tests
coverage xml -o coverage.xml
mv coverage.xml /tests/coverage.xml