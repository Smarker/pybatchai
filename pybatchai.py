import logging

from azure.common.credentials import ServicePrincipalCredentials
import click
import coloredlogs

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
@click.pass_context
def blobstorage(
        context: object
    ) -> None:
    """Blob Storage."""
    cli.blob_storage.set_blob_storage_service(context)

@blobstorage.command(name='upload')
@click.option('--container', required=True, help='container name')
@click.option('--local-path', required=True)
@click.pass_context
def upload_to_blob_container(context: object, container: str,
    local_path: str) -> None:
    """Upload directory or file to blob container."""
    context.obj['container_name'] = container
    context.obj['local_path'] = local_path
    cli.blob_storage.upload(context)

@blobstorage.command(name='download')
@click.option('--container', required=True, help='container name')
@click.option('--local-path', required=True)
@click.pass_context
def download_from_blob_container(context: object, container: str,
    local_path: str) -> None:
    """Download directory or file from blob container."""
    context.obj['container_name'] = container
    context.obj['local_path'] = local_path
    cli.blob_storage.download(context)

main.add_command(storage)
storage.add_command(fileshare)
fileshare.add_command(upload_to_fileshare)
fileshare.add_command(download_fileshare)
storage.add_command(blobstorage)
blobstorage.add_command(upload_to_blob_container)
blobstorage.add_command(download_from_blob_container)

if __name__ == '__main__':
    main()
