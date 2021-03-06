import click
import re
from uuid import UUID

from cli.regex import REGEX_DICT

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
    return regex_matches(REGEX_DICT['resource_group_name'], value,
                         'Resource group name should be 1-90 characters. Characters may be case insensitive, alphanumeric, underscore, parentheses, hyphen, period (except at end), and Unicode characters.')

def validate_storage_name(context, param, value):
    return regex_matches(REGEX_DICT['storage_account_name'], value,
                         'storage account name must be between 3 and 24 characters in length and may contain numbers and lowercase letters only.')

def validate_fileshare_name(context, param, value):
    return regex_matches(REGEX_DICT['fileshare_name'], value,
                         'See https://docs.microsoft.com/en-us/rest/api/storageservices/Naming-and-Referencing-Shares--Directories--Files--and-Metadata?redirectedfrom=MSDN#share-names for name format')

def validate_container_name(context, param, value):
    return regex_matches(REGEX_DICT['container_name'], value,
                         'See https://docs.microsoft.com/en-us/rest/api/storageservices/Naming-and-Referencing-Shares--Directories--Files--and-Metadata?redirectedfrom=MSDN#share-names for name format')

def validate_cluster_name(context, param, value):
    return regex_matches(REGEX_DICT['cluster_name'], value, 'Names can only contain a combination of alphanumeric characters along with dash (-) and underscore (_). The name must be from 1 through 64 characters long.')

def validate_workspace_name(context, param, value):
    return regex_matches(REGEX_DICT['workspace'], value, 'Names can only contain a combination of alphanumeric characters along with dash (-) and underscore (_). The name must be from 1 through 64 characters long.')

def regex_matches(pattern, value, bad_param_message):
    pattern = re.compile(pattern)
    if pattern.match(value):
        return value
    else:
        raise click.BadParameter(bad_param_message)
