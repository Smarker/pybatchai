from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

import cli.notify

def resource_group_exists(context):
    for item in context.obj['resource_client'].resource_groups.list():
        print(item)
    return True

def create_rg_if_not_exists(context):
    """Create a new resource group."""
    resource_group_name = context.obj['resource_group']
    location = context.obj['location']
    context.obj['resource_client'] = ResourceManagementClient(
        credentials=context.obj['aad_credentials'],
        subscription_id=context.obj['subscription_id'],
        base_url=AZURE_PUBLIC_CLOUD.endpoints.resource_manager)

    if not resource_group_exists:
        context.obj['resource_client'].resource_groups.create_or_update(resource_group_name,
                                                                        {'location': location})
        cli.notify.print_created(resource_group_name)
    else:
        cli.notify.print_already_exists(resource_group_name)
