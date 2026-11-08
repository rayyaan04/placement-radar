# pytest loads this file before tets, gives every test a fixture("name.json") that loads a saved testing response
import json
from pathlib import Path

import pytest

# folder holding sample json files
FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture
def fixture():
    def load(name):
        #read tests/fixtures and turns the json into python data
        return json.loads((FIXTURES / name).read_text())
    return load