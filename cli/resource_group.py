import logging

from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

import cli.utils

LOGGER = logging.getLogger(__name__)
RG_TYPE = 'resource group'

def create_rg_if_not_exists(context):
    """Create a new resource group."""
    resource_group = context.obj['resource_group']
    location = context.obj['location']
    context.obj['resource_client'] = ResourceManagementClient(
        credentials=context.obj['aad_credentials'],
        subscription_id=context.obj['subscription_id'],
        base_url=AZURE_PUBLIC_CLOUD.endpoints.resource_manager)

    if not resource_group_exists:
        context.obj['resource_client'].resource_groups.create_or_update(
            resource_group,
            {'location': location}
        )
        LOGGER.info(cli.utils.created(RG_TYPE, resource_group))
    else:
        LOGGER.info(cli.utils.already_exists(RG_TYPE, resource_group))

def resource_group_exists(context):
    return any(context.obj['resource_group'] == rg.name
               for rg in context.obj['resource_client'].resource_groups.list())
