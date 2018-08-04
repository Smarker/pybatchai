from hypothesis import given, example
from hypothesis.strategies import fixed_dictionaries, text, from_regex

import cli.blob_storage
from cli.regex import REGEX_DICT
from cli.validation import validate_container_name

@example(fixed_dictionaries({}), text(), 'mycontainer')
@example(fixed_dictionaries({}), text(), 'another-container')
@given(fixed_dictionaries({}), text(), from_regex(REGEX_DICT['container_name']))
def test_validate_container_name(context, param, value):
    assert validate_container_name(context, param, value)
