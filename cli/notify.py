def print_already_exists(resource_name):
    print('{} already exists.'.format(resource_name))

def print_created(resource_name):
    """Print resource was successfully created."""
    print('Created resource {}.'.format(resource_name))

def print_create_failed(resource_name, exception):
    """Print resource was unable to be created."""
    print('Failed to create {}. Exception:{}'.format(resource_name, exception))
