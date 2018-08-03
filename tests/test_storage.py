from hypothesis import given, example
from hypothesis.strategies import fixed_dictionaries, text, from_regex

from cli.regex import REGEX_DICT
from cli.validation import validate_storage_name

@example(fixed_dictionaries({}), text(), 'mystorage')
@example(fixed_dictionaries({}), text(), 'ab3')
@given(fixed_dictionaries({}), text(),
       from_regex(REGEX_DICT['storage_account_name']))
def test_validate_storage_name(context, param, value):
    assert validate_storage_name(context, param, value)
