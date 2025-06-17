#!/bin/bash
clean_allure_cache() {
    if [ -d "$1" ]; then
        echo "Cleaning Allure cache: $1"
        rm -rf "$1"
    fi
}

export PYTHONPATH=$(pwd)


PORTAL=$1
TEST_FILE_NAME=$2

# check if the first argument is admin or snapper
if [ "$PORTAL" != "admin" ] && [ "$PORTAL" != "snapper" ]; then
    echo "First argument must be 'admin' or 'snapper'"
    exit 1
fi

# Clear cache
clean_allure_cache "${PORTAL}_portal/testresult/allure-results"

if [ -z "$TEST_FILE_NAME" ]; then
    # if no test file is specified then ran all test
    echo "Running all tests in ${PORTAL}_portal/tests"
    pytest ${PORTAL}_portal/tests --alluredir=${PORTAL}_portal/testresult/allure-results --maxfail=1 --disable-warnings -q
else
    # if a test file is specified then ran the specific test file
    TEST_PATH="${PORTAL}_portal/tests/$TEST_FILE_NAME"
    if [ ! -f "$TEST_PATH" ]; then
        echo "Test file '$TEST_PATH' not found."
        exit 1
    fi
    echo "Running test file $TEST_PATH"
    pytest "$TEST_PATH" --alluredir=${PORTAL}_portal/testresult/allure-results --maxfail=1 --disable-warnings -q
fi

allure serve ${PORTAL}_portal/testresult/allure-results

# Record: playwright codegen --target python https://me-dev-1.snapsendsolve.com
# run: ./run_tests.sh snapper
# run: ./run_tests.sh admin
# run: ./run_tests.sh snapper file_name.py