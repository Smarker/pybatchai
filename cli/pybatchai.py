from colorama import init
import click
from . import resource_group, workspace
from . import storage, blob_storage, fileshare
from . import cluster, job
from . import logging
import azure.mgmt.batchai as training
from azure.common.credentials import ServicePrincipalCredentials
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

def create_batchai_client(context: object) -> None:
    """Client to create batchai resources."""
    if 'batchai_client' not in context.obj:
        batchai_client = training.BatchAIManagementClient(
            credentials=context.obj['aad_credentials'],
            subscription_id=context.obj['subscription_id'],
            base_url=AZURE_PUBLIC_CLOUD.endpoints.resource_manager)
        context.obj['batchai_client'] = batchai_client

@main.group()
@click.pass_context
def cluster(context: object) -> None:
    """Cluster."""
    pass

@cluster.command(name='create')
@click.pass_context
@click.option('--cluster-name', required=True)
@click.option('--node-count', required=True, default=1)
@click.option('--vm-size', required=True, default='STANDARD_NC6')
@click.option('--admin-username', required=True)
@click.option('--admin-password', required=True)
@click.option('--admin-ssh-public-key', required=True)
@click.option('--workspace', required=True)
@click.option('--storage-account-name', required=True)
@click.option('--fileshare-name', required=True)
def create_cluster(context: object, cluster_name: str, node_count: int,
    vm_size: str, admin_username: str, admin_password: str, admin_ssh_public_key: str, workspace: str, storage_account_name: str,
    fileshare_name: str) -> None:
    """Set up a batch ai cluster."""
    context.obj['cluster_name'] = cluster_name
    context.obj['node_count'] = node_count
    context.obj['vm_size'] = vm_size
    context.obj['admin_username'] = admin_username
    context.obj['admin_password'] = admin_password
    context.obj['admin_ssh_public_key'] = admin_ssh_public_key
    context.obj['workspace'] = workspace
    context.obj['storage_account_name'] = storage_account_name
    context.obj['fileshare_name'] = fileshare_name

    create_batchai_client(context)
    workspace_exists = workspace_service.create_workspace_if_not_exists(context)
    if not workspace_exists:
        return

    cluster_service.create_cluster(context)

@cluster.command(name='monitor')
@click.pass_context
@click.option('--cluster-name', required=True)
@click.option('--workspace', required=True)
def monitor_cluster(context: object, cluster_name: str, workspace: str) -> None:
    """Monitor the status of your batchai cluster."""
    context.obj['cluster_name'] = cluster_name
    context.obj['workspace'] = workspace
    create_batchai_client(context)
    cluster_service.monitor_cluster(context)

@main.group()
@click.pass_context
def job(context: object) -> None:
    """Job."""
    pass

@job.command(name='create')
@click.option('--storage-account-name', required=True)
@click.pass_context
def job_create(context: object) -> None:
    """Create a batchai job."""
    pass

@main.group()
@click.option('--storage-account-name', required=True)
@click.pass_context
def storage(context: object, storage_account_name: str) -> None:
    """Storage options."""
    context.obj['storage_account_name'] = storage_account_name
    storage_service.set_storage_client(context)
    storage_service.set_storage_account_key(context)

@storage.group()
@click.option('--fileshare-name', required=True)
@click.pass_context
def fileshare(context: object, fileshare_name: str) -> None:
    """Fileshare."""
    context.obj['fileshare_name'] = fileshare_name

@fileshare.command(name='create')
@click.pass_context
def create_fileshare(context: object) -> None:
    """Create an Azure File Share."""
    valid_storage_acct = storage_service.create_storage_acct_if_not_exists(context)
    if not valid_storage_acct:
        return
    fileshare_service.set_fileshare_service(context)
    fileshare_service.create_file_share_if_not_exists(context)

@fileshare.group()
@click.option('--directory-name', required=True)
@click.pass_context
def directory(context: object, directory_name: str) -> None:
    """Directory."""
    context.obj['fileshare_directory'] = directory_name

@fileshare.command(name='create')
@click.pass_context
def create_fileshare_directory(context: object) -> None:
    """Create an Azure File Share Directory."""
    fileshare_service.set_fileshare_service(context)
    fileshare_service.create_directory_if_not_exists(context)

'''
@storage.group()
@click.option('--fileshare-name', required=True)
@click.pass_context
def blob_storage(context: object, fileshare_name: str) -> None:
    """Blob Storage."""
    blob_storage_service.set_blob_storage_service()

@blobstorage.command(name='create')
@click.pass_context
def create_blob_storage(context: object) -> None:
    """Create an Azure Blob Storage."""
    valid_storage_acct = storage_service.create_storage_acct_if_not_exists(context)
    if not valid_storage_acct:
        return
    pass #  TODO: add func
'''

@click.group()
@click.option('--subscription-id', required=True)
@click.option('--resource-group-name', required=True)
@click.option('--location', required=True)
@click.option('--aad-client-id', required=True)
@click.option('--aad-secret-key', required=True)
@click.option('--aad-tenant-id', required=True)
@click.pass_context
def main(context: object, subscription_id: str, resource_group_name: str,
    location: str, aad_client_id: str, aad_secret_key:str, aad_tenant_id: str) -> None:
    """A Python tool for Batch AI.

    At minimum you must have:

    1. An Azure Subscription with an Owner or User Access Administrator role to
    assign a role to an Azure Active Directory (AAD) App

    2. An AAD application created to obtain an aad client id, aad secret key,
     aad tenant id. The AAD app must have a contributor role.

    For 1 see:
    https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal

    For 2 see:
    https://github.com/Azure/BatchAI/blob/master/recipes/Preparation.md#using-portal
    """
    init(autoreset=True)

    aad_token_uri = 'https://login.microsoftonline.com/{0}/oauth2/token'.format(aad_tenant_id)
    credentials = ServicePrincipalCredentials(client_id=aad_client_id,
                                              secret=aad_secret_key,
                                              token_uri=aad_token_uri)
    context.obj = {
        'subscription_id': subscription_id,
        'resource_group': resource_group_name,
        'location': location,
        'aad_credentials': credentials
    }

    rg_service.create_resource_group_if_not_exists(context)


main.add_command(cluster)
main.add_command(storage)
storage.add_command(fileshare)
fileshare.add_command(create_fileshare)
fileshare.add_command(directory)
directory.add_command(create_fileshare_directory)
cluster.add_command(create_cluster)
cluster.add_command(monitor_cluster)

if __name__ == '__main__':
    main()
