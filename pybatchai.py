import azure.mgmt.batchai as training
from azure.common.credentials import ServicePrincipalCredentials
import click
import coloredlogs
import logging
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

import cli.blob_storage
import cli.cluster
import cli.fileshare
import cli.job
import cli.resource_group
import cli.storage
import cli.workspace

@click.group()
@click.option('--subscription-id', required=True)
@click.option('--resource-group-name', required=True)
@click.option('--location', required=True)
@click.option('--aad-client-id', required=True)
@click.option('--aad-secret-key', required=True)
@click.option('--aad-tenant-id', required=True)
@click.pass_context
def main(context: object, subscription_id: str, resource_group_name: str,
    location: str, aad_client_id: str, aad_secret_key:str,
    aad_tenant_id: str) -> None:
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

    cli.resource_group.create_rg_if_not_exists(context)

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
    vm_size: str, admin_username: str, admin_password: str, 
    admin_ssh_public_key: str, workspace: str, storage_account_name: str,
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
    cli.workspace.create_workspace_if_not_exists(context)

    cli.cluster.create_cluster(context)

def create_batchai_client(context: object) -> None:
    """Client to create batchai resources."""
    if 'batchai_client' not in context.obj:
        batchai_client = training.BatchAIManagementClient(
            credentials=context.obj['aad_credentials'],
            subscription_id=context.obj['subscription_id'],
            base_url=AZURE_PUBLIC_CLOUD.endpoints.resource_manager)
        context.obj['batchai_client'] = batchai_client

@cluster.command(name='monitor')
@click.pass_context
@click.option('--cluster-name', required=True)
@click.option('--workspace', required=True)
def monitor_cluster(context: object, cluster_name: str, workspace: str) -> None:
    """Monitor the status of your batchai cluster."""
    context.obj['cluster_name'] = cluster_name
    context.obj['workspace'] = workspace
    create_batchai_client(context)
    cli.cluster.monitor_cluster(context)

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
    cli.storage.set_storage_client(context)
    valid_storage_acct = cli.storage.create_acct_if_not_exists(context)
    if not valid_storage_acct:
        return
    cli.storage.set_storage_account_key(context)

@storage.group()
@click.pass_context
def fileshare(context: object) -> None:
    """Fileshare."""
    pass

@fileshare.command(name='create')
@click.option('--fileshare-name', required=True)
@click.pass_context
def create_fileshare(context: object, fileshare_name: str) -> None:
    """Create an Azure File Share."""
    context.obj['fileshare_name'] = fileshare_name
    cli.fileshare.set_fileshare_service(context)
    cli.fileshare.create_file_share_if_not_exists(context)

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
    cli.fileshare.set_fileshare_service(context)
    cli.fileshare.create_directory_if_not_exists(context)

@fileshare.command(name='upload')
@click.option('--fileshare-name', required=True)
@click.option('--fileshare-directory', required=True)
@click.option('--data-dir', required=True)
@click.pass_context
def upload_to_fileshare_directory(context: object, fileshare_name: str,
    fileshare_directory: str, data_dir: str) -> None:
    """Upload directory to fileshare."""
    context.obj['fileshare_name'] = fileshare_name
    context.obj['fileshare_directory'] = fileshare_directory
    context.obj['data_dir'] = data_dir
    cli.fileshare.upload(context)

@fileshare.command(name='download')
@click.option('--fileshare-name', required=True)
@click.option('--fileshare-directory', required=True)
@click.option('--local-download-path', required=True)
@click.pass_context
def download_fileshare_directory(context: object, fileshare_name: str,
    fileshare_directory: str, local_download_path: str) -> None:
    """Download directory from fileshare."""
    context.obj['fileshare_name'] = fileshare_name
    context.obj['fileshare_directory'] = fileshare_directory
    context.obj['local_download_path'] = local_download_path
    cli.fileshare.download(context)

@storage.group()
@click.pass_context
def blobstorage(context: object) -> None:
    """Blob Storage."""
    cli.blob_storage.set_blob_storage_service(context)
    pass

@blobstorage.command(name='create')
@click.option('--container-name', required=True)
@click.pass_context
def create_blob_storage_container(context: object, container_name: str) -> None:
    """Create an Azure Blob Storage Container."""
    context.obj['container_name'] = container_name
    cli.blob_storage.create_container_if_not_exists(context)

@blobstorage.command(name='upload')
@click.option('--container-name', required=True)
@click.option('--data-dir', required=True)
@click.pass_context
def upload_to_blob_container(context: object, container_name: str,
    data_dir: str) -> None:
    """Upload directory to blob container."""
    context.obj['container_name'] = container_name
    context.obj['data_dir'] = data_dir
    cli.blob_storage.upload(context)

@blobstorage.command(name='download')
@click.option('--container-name', required=True)
@click.option('--local-download-path', required=True)
@click.pass_context
def download_from_blob_container(context: object, container_name: str,
    local_download_path: str) -> None:
    """Download directory from blob container."""
    context.obj['container_name'] = container_name
    context.obj['local_download_path'] = local_download_path
    cli.blob_storage.download(context)

main.add_command(cluster)
main.add_command(storage)
storage.add_command(fileshare)
fileshare.add_command(create_fileshare)
fileshare.add_command(directory)
directory.add_command(create_fileshare_directory)
fileshare.add_command(upload_to_fileshare_directory)
fileshare.add_command(download_fileshare_directory)
storage.add_command(blobstorage)
storage.add_command(create_blob_storage_container)
storage.add_command(upload_to_blob_container)
storage.add_command(download_from_blob_container)
cluster.add_command(create_cluster)
cluster.add_command(monitor_cluster)

if __name__ == '__main__':
    main()
