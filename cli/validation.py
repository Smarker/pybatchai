import click
import re
from uuid import UUID

from cli.utils import RG_NAME_PATTERN
from cli.utils import LOCATION_PATTERN

def validate_uuid(context, param, value):
    if is_uuid(value):
        return value
    else:
        raise click.BadParameter('Subscription id must be in uuid4 format.')

def is_uuid(param):
    uuid_str = str(param)
    try:
        uuid_obj = UUID(uuid_str, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str

def validate_rg_name(context, param, value):
    pattern = re.compile(RG_NAME_PATTERN)
    if pattern.match(value):
        return value
    else:
        raise click.BadParameter("""Resource group name should be 1-90
        characters. Characters may be case insensitive, alphanumeric,
        underscore, parentheses, hyphen, period (except at end), and Unicode characters.""")

def validate_location(context, param, value):
    '''location is alphabetic with an optional 2 at the end'''
    pattern = re.compile(LOCATION_PATTERN)
    if pattern.match(value):
        return value
    else:
        raise click.BadParameter('location is one of eastus, eastus2, etc.')
