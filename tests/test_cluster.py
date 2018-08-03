from hypothesis import given, example
from hypothesis.strategies import fixed_dictionaries, text, from_regex

from cli.regex import REGEX_DICT
from cli.validation import validate_cluster_name, validate_workspace_name

@example(fixed_dictionaries({}), text(), 'my-cluster')
@example(fixed_dictionaries({}), text(), 'an0ther_cluster2')
@given(fixed_dictionaries({}), text(), from_regex(REGEX_DICT['cluster_name']))
def test_validate_cluster_name(context, param, value):
    assert validate_cluster_name(context, param, value)

@example(fixed_dictionaries({}), text(), 'my-workspace')
@example(fixed_dictionaries({}), text(), 'an0ther_workspace2')
@given(fixed_dictionaries({}), text(), from_regex(REGEX_DICT['workspace']))
def test_Validate_workspace_name(context, param, value):
    assert validate_workspace_name(context, param, value)
