RG_NAME_PATTERN = '^[-\w\._\(\)]{1,90}[^\.]$'
STORAGE_NAME_PATTERN = '^[a-z0-9]{3,24}$'
# String ahead does not contain two dashes
DOES_NOT_CONTAIN_TWO_DASH = '(?!.+--)'
# String ahead does not start with a dash
DOES_NOT_START_WITH_DASH = '(?!^-)'
# Either literal root or a combination approved letters.
APPROVED_SHARE_CONTAINER_LETTERS = '(\$root|[a-z\d-]{3,63})'
# Fileshare or container pattern
SHARE_OR_CONTAINER_PATTERN = '^{}{}{}$'.format(DOES_NOT_CONTAIN_TWO_DASH,
                                               DOES_NOT_START_WITH_DASH,
                                               APPROVED_SHARE_CONTAINER_LETTERS)
CLUSTER_NAME_PATTERN = '^[\w-]{1,64}$'
WORKSPACE_NAME_PATTERN = '^[\w-]{1,64}$'

REGEX_DICT = {
    'resource_group_name': RG_NAME_PATTERN,
    'storage_account_name': STORAGE_NAME_PATTERN,
    'fileshare_name': SHARE_OR_CONTAINER_PATTERN,
    'container_name': SHARE_OR_CONTAINER_PATTERN,
    'cluster_name': CLUSTER_NAME_PATTERN,
    'workspace': WORKSPACE_NAME_PATTERN
}
