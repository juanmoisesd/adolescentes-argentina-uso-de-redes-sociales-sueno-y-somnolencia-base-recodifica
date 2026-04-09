import json
import pytest
from jsonschema import validate

def test_schema_validity():
    with open('schema.json', 'r') as f:
        schema = json.load(f)
    # Simple check if schema itself is valid (or at least readable)
    assert schema['title'] is not None

def test_datapackage_validity():
    with open('datapackage.json', 'r') as f:
        datapackage = json.load(f)
    assert 'resources' in datapackage
