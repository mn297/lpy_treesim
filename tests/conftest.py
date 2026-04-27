#! /usr/bin/env python3
import pytest
import os

@pytest.fixture
def tmp_path():
    return os.path.dirname(__file__)

@pytest.fixture(autouse=True)
def test_logging_env(tmp_path):
    os.environ["LPY_TREESIM_LOG_FILE"] = os.path.join(tmp_path, "test.log")
    os.environ['LPY_TREESIM_LOG_LEVEL'] = 'DEBUG'
    return