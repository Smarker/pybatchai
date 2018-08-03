from hypothesis import given, example
from hypothesis.strategies import fixed_dictionaries, text, from_regex, uuids

from cli.utils import RG_NAME_PATTERN, LOCATION_PATTERN
from cli.validation import validate_uuid, validate_rg_name, validate_location

@example(fixed_dictionaries({}), text(), 'a2cfad07-90d4-4e4c-9227-095d90fcc7dd')
@given(fixed_dictionaries({}), text(), uuids(version=4))
def test_validate_uuid(context, param, value):
    assert validate_uuid(context, param, value)

@example(fixed_dictionaries({}), text(), 'rg_name')
@example(fixed_dictionaries({}), text(), 'rg.name')
@example(fixed_dictionaries({}), text(), 'rg-name')
@given(fixed_dictionaries({}), text(), from_regex(RG_NAME_PATTERN))
def test_validate_rg_name(context, param, value):
    assert validate_rg_name(context, param, value)

@example(fixed_dictionaries({}), text(), 'eastus')
@example(fixed_dictionaries({}), text(), 'eastus2')
@given(fixed_dictionaries({}), text(), from_regex(LOCATION_PATTERN))
def test_validate_location(context, param, value):
    assert validate_location(context, param, value)
