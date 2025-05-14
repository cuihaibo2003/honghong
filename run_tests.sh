#!/bin/bash
clean_allure_cache() {
    if [ -d "$1" ]; then
        echo "Cleaning Allure cache: $1"
        rm -rf "$1"
    fi
}

export PYTHONPATH=$(pwd)
if [ "$1" == "admin" ]; then
    echo "Running pytest for admin portal"
    clean_allure_cache "admin_portal/testresult/allure-results"
    pytest admin_portal/tests --alluredir=admin_portal/testresult/allure-results --maxfail=1 --disable-warnings -q
    allure serve admin_portal/testresult/allure-results
elif [ "$1" == "snapper" ]; then
    echo "Running pytest for snapper portal"
    clean_allure_cache "snapper_portal/testresult/allure-results"
    pytest snapper_portal/tests --alluredir=snapper_portal/testresult/allure-results --maxfail=1 --disable-warnings -q
    allure serve snapper_portal/testresult/allure-results
else
    echo "Please specify 'admin' or 'snapper' to run the respective tests."
fi

# Record: playwright codegen --target python https://me-dev-1.snapsendsolve.com
# run: ./run_tests.sh snapper
# run: ./run_tests.sh admin