#!/usr/bin/env bash

# NOTE: pytest and coverage are configured in pyproject.toml
eval "python -m pytest"
TEST_OUTPUT=$?

echo "TEST_OUTPUT:" $TEST_OUTPUT
exit $TEST_OUTPUT
