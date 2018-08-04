import logging

from azure.common.credentials import ServicePrincipalCredentials
import click
import coloredlogs

#import cli.cluster
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
@click.pass_context
def cluster(
        context: object,
    ) -> None:
    """Cluster."""
    pass

@cluster.command(name='create')
@click.option('--name', required=True, help='cluster name',
              callback=cli.validation.validate_cluster_name)
@click.option('--workspace', required=True, help='name of workspace',
              callback=cli.validation.validate_workspace_name)
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

main.add_command(storage)
storage.add_command(fileshare)
fileshare.add_command(upload_to_fileshare)
fileshare.add_command(download_fileshare)

if __name__ == '__main__':
    main()
