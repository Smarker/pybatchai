import logging

from azure.common.credentials import ServicePrincipalCredentials
import azure.mgmt.batchai as training
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
import click
import coloredlogs

import cli.blob_storage
import cli.cluster
import cli.fileshare
import cli.resource_group
import cli.storage
import cli.validation

@click.group()
@click.option('--subscription-id', required=True,
              callback=cli.validation.validate_uuid)
@click.option('--resource-group', required=True, help='resource group name',
              callback=cli.validation.validate_rg_name)
@click.option('--location', required=True, default='eastus',
              callback=cli.validation.validate_location)
@click.option('--aad-app-id', required=True,
              callback=cli.validation.validate_uuid)
@click.option('--aad-key', required=True)
@click.option('--aad-directory-id', required=True,
              callback=cli.validation.validate_uuid)
@click.pass_context
def main(
        context: object,
        subscription_id: str,
        resource_group: str,
        location: str,
        aad_app_id: str,
        aad_key: str,
        aad_directory_id: str
    ) -> None:
    """A Python tool for Batch AI.

    At minimum you must have:

    1. An Azure Subscription with an Owner or User Access Administrator role to
    assign a role to an Azure Active Directory (AAD) App.

    2. An AAD application created to obtain an aad app id, aad key,
     aad directory id. The AAD app must have a contributor role.

    For 1. see:
    https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal

    For 2. see:
    https://github.com/Azure/BatchAI/blob/master/recipes/Preparation.md#using-portal
    """

    coloredlogs.install()
    logging.basicConfig(level=logging.INFO)

    aad_token_uri = 'https://login.microsoftonline.com/{0}/oauth2/token'.format(aad_directory_id)
    credentials = ServicePrincipalCredentials(client_id=aad_app_id,
                                              secret=aad_key,
                                              token_uri=aad_token_uri)
    context.obj = {
        'subscription_id': subscription_id,
        'resource_group': resource_group,
        'location': location,
        'aad_credentials': credentials
    }

    cli.resource_group.create_rg_if_not_exists(context)

@main.group()
@click.option('--name', required=True, help='storage account name',
              callback=cli.validation.validate_storage_name)
@click.pass_context
def storage(
        context: object,
        name: str
    ) -> None:
    """Storage options."""
    context.obj['storage_account'] = name
    cli.storage.set_storage_client(context)
    valid_storage_acct = cli.storage.create_acct_if_not_exists(context)
    if not valid_storage_acct:
        return
    cli.storage.set_storage_account_key(context)

@storage.group()
@click.option('--name', required=True, help='fileshare name',
              callback=cli.validation.validate_fileshare_name)
@click.pass_context
def fileshare(
        context: object,
        name: str
    ) -> None:
    """Fileshare."""
    context.obj['fileshare'] = name

@fileshare.command(name='upload')
@click.option('--local-path', required=True, type=click.Path(exists=True),
              help='upload files or a directory at this path')
@click.pass_context
def upload_to_fileshare(
        context: object,
        local_path: str
    ) -> None:
    """Upload directory or file to fileshare."""
    context.obj['local_path'] = local_path
    cli.fileshare.upload(context)

@fileshare.command(name='download')
@click.option('--local-path', required=True, type=click.Path(),
              help='download files or a directory at this path')
@click.pass_context
def download_fileshare(
        context: object,
        local_path: str
    ) -> None:
    """Download directory or file from fileshare."""
    context.obj['local_path'] = local_path
    cli.fileshare.download(context)

@storage.group()
@click.option('--container', required=True, help='container name',
              callback=cli.validation.validate_container_name)
@click.pass_context
def blobstorage(
        context: object,
        container: str
    ) -> None:
    """Blob Storage."""
    cli.blob_storage.set_blob_storage_service(context)
    context.obj['container_name'] = container

@blobstorage.command(name='upload')
@click.option('--local-path', required=True, type=click.Path(exists=True))
@click.pass_context
def upload_to_blob_container(
        context: object,
        local_path: str
    ) -> None:
    """Upload directory or file to blob container."""
    context.obj['local_path'] = local_path
    cli.blob_storage.upload(context)

@blobstorage.command(name='download')
@click.option('--local-path', required=True, type=click.Path())
@click.pass_context
def download_from_blob_container(
        context: object,
        local_path: str
    ) -> None:
    """Download directory or file from blob container."""
    context.obj['local_path'] = local_path
    cli.blob_storage.download(context)

@main.group()
@click.option('--name', required=True, help='cluster name',
              callback=cli.validation.validate_cluster_name)
@click.option('--workspace', required=True, help='workspace name',
              callback=cli.validation.validate_workspace_name)
@click.pass_context
def cluster(
        context: object,
        name: str,
        workspace: str
    ) -> None:
    """Cluster."""
    context.obj['cluster_name'] = name
    context.obj['workspace'] = workspace
    create_batchai_client(context)

@cluster.command(name='delete')
@click.pass_context
def delete_cluster(
        context: object
    ) -> None:
    """Delete your batchai cluster."""
    cli.cluster.delete_cluster(context)

@cluster.command(name='show')
@click.pass_context
def show_cluster(
    context:object
) -> None:
    """Show details of your batchai cluster."""
    cli.cluster.show_cluster(context)

def create_batchai_client(context: object) -> None:
    """Client to create batchai resources."""
    if 'batchai_client' not in context.obj:
        batchai_client = training.BatchAIManagementClient(
            credentials=context.obj['aad_credentials'],
            subscription_id=context.obj['subscription_id'],
            base_url=AZURE_PUBLIC_CLOUD.endpoints.resource_manager)
        context.obj['batchai_client'] = batchai_client

main.add_command(storage)
storage.add_command(fileshare)
fileshare.add_command(upload_to_fileshare)
fileshare.add_command(download_fileshare)
storage.add_command(blobstorage)
blobstorage.add_command(upload_to_blob_container)
blobstorage.add_command(download_from_blob_container)
main.add_command(cluster)
cluster.add_command(delete_cluster)
cluster.add_command(show_cluster)

if __name__ == '__main__':
    main()
