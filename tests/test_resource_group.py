from hypothesis import given, example
from hypothesis.strategies import fixed_dictionaries, text, from_regex, uuids

from cli.regex import REGEX_DICT
import cli.resource_group
from cli.validation import validate_uuid, validate_rg_name, validate_location

@example(fixed_dictionaries({}), text(), 'a2cfad07-90d4-4e4c-9227-095d90fcc7dd')
@given(fixed_dictionaries({}), text(), uuids(version=4))
def test_validate_uuid(context, param, value):
    assert validate_uuid(context, param, value)

@example(fixed_dictionaries({}), text(), 'rg_name1')
@example(fixed_dictionaries({}), text(), 'rg.mylongername')
@example(fixed_dictionaries({}), text(), 'rg-aNoTher--name')
@given(fixed_dictionaries({}), text(),
       from_regex(REGEX_DICT['resource_group_name']))
def test_validate_rg_name(context, param, value):
    assert validate_rg_name(context, param, value)

@example(fixed_dictionaries({}), text(), 'eastus')
@example(fixed_dictionaries({}), text(), 'eastus2')
@given(fixed_dictionaries({}), text(),
       from_regex(REGEX_DICT['location']))
def test_validate_location(context, param, value):
    assert validate_location(context, param, value)
