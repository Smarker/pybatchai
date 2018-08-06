from hypothesis import given, example
from hypothesis.strategies import fixed_dictionaries, text, from_regex

import cli.fileshare
from cli.regex import REGEX_DICT
from cli.validation import validate_fileshare_name

@example(fixed_dictionaries({}), text(), 'myfileshare')
@example(fixed_dictionaries({}), text(), 'another-fileshare')
@given(fixed_dictionaries({}), text(), from_regex(REGEX_DICT['fileshare_name']))
def test_validate_fileshare_name(context, param, value):
    assert validate_fileshare_name(context, param, value)
