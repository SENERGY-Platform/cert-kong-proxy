coverage run -m unittest discover tests
TEST_RESULT=$?
coverage xml -o coverage.xml 
coverage report 
coverage html
mv coverage.xml /coverage/coverage.xml
mv htmlcov /coverage
exit $TEST_RESULT