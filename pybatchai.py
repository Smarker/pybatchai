import logging

from azure.common.credentials import ServicePrincipalCredentials
import azure.mgmt.batchai as training
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
import click
import coloredlogs

<<<<<<< HEAD
import cli.blob_storage
import cli.cluster
=======
#import cli.cluster
import cli.blob_storage
>>>>>>> 6e5bddff3b689b782de248bd9053f6ade7dd67d8
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

@cluster.command(name='create')
@click.option('--afs-mount-path', required=False, type=click.Path(),
              default='afs', help='mount path for azure file share')
@click.option('--afs-name', required=False,
              help='name of afs to be mounted on each node',
              callback=cli.validation.validate_afs_name)
@click.option('--bfs-mount-path', required=False, type=click.Path(),
              default='bfs', help='mount path for storage container')
@click.option('--bfs-name', required=False,
              help='name of storage container to be mounted on each node',
              callback=cli.validation.validate_bfs_name)
@click.option('--image', required=False, help='os image alias',
              callback=cli.validation.validate_image_name)
@click.option('--max', required=False, type=click.IntRange(min=0),
              help='max nodes for auto-scale cluster')
@click.option('--min', required=False, type=click.IntRange(min=0),
              help='min nodes for auto-scale cluster')
@click.option('--password', required=False,
              help='optional password for admin user on each node',
              callback=cli.validation.validate_password)
@click.option('--ssh-key', required=False, type=click.Path(exists=True),
              help='optional path to SSH public key')
@click.option('--storage-account-key', required=False, help='storage account key',
              callback=cli.validation.validate_storage_key)
@click.option('--storage-account-name', required=False,
              help='storage account for azure file shares and/or azure storage containers',
              callback=cli.validation.validate_storage_account_name)
@click.option('--user-name', required=False,
              help='username for admin user on each node',
              callback=cli.validation.validate_user_name)
@click.option('--vm-priority', required=False, help='VM priority',
              type=click.Choice(['dedicated', 'lowpriority']))
@click.option('--vm-size', required=False, help='VM size for nodes',
              callback=cli.validation.validate_vm_size)
def create_cluster(
        workspace: str,
        afs_path: str,
        afs_name: str,
        bfs_path: str,
        bfs_name: str,
        image_name: str,
        max_nodes: int,
        min_nodes: int,
        admin_pass: str,
        ssh_key: str,
        storage_key: str,
        storage_name: str,
        admin_uname: str,
        vm_priority: str,
        vm_size: str
    ) -> None:
    """Create a cluster."""
    print(
        'workspace:', workspace,
        'afs_path:', afs_path,
        'afs_name:', afs_name,
        'bfs_path:', bfs_path,
        'bfs_name:', bfs_name,
        'image_name:', image_name,
        'max_nodes:', max_nodes,
        'min_nodes:', min_nodes,
        'admin_pass:', admin_pass,
        'ssh_key:', ssh_key,
        'storage_key:', storage_key,
        'storage_name:', storage_name,
        'admin_uname:', admin_uname,
        'vm_priority:', vm_priority,
        'vm_size:', vm_size
    )

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
