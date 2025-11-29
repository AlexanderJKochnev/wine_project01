#!/bin/bash


# FAILED tests/test_search.py::test_search - AssertionError: id=2 not in [None, None, None, None, None]
# FAILED tests/test_delete.py::test_delete - AssertionError: {"detail":[{"type":"int_parsing","loc":["path","id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"None"}]}

pytest tests/test_get.py \
       tests/test_update.py \
       tests/test_search.py \
       tests/test_preact.py \
       tests/test_mongodb.py \
       tests/test_delete.py