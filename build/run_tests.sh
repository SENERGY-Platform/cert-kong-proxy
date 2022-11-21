coverage run -m unittest discover tests
coverage xml -o coverage.xml --omit="*/test*"
coverage report --omit="*/test*"
coverage html --omit="*/test*"
mv coverage.xml /coverage/coverage.xml
mv htmlcov /coverage/htmlcov