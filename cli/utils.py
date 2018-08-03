RG_NAME_PATTERN = '^[-\w\._\(\)]{1,90}[^\.]$'
LOCATION_PATTERN = '^[a-zA-Z]+2?$'

def already_exists(resource_type, resource_name):
    return '{} {} already exists.'.format(resource_type, resource_name)

def created(resource_type, resource_name):
    return 'Created {} {}.'.format(resource_type, resource_name)

def create_failed(resource_type, resource_name, error_message):
    return 'Failed to create {} {}. Exception:{}'.format(resource_type,
                                                         resource_name,
                                                         error_message)
