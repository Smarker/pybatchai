import logging

from azure.common.credentials import ServicePrincipalCredentials
import click
import coloredlogs

import cli.resource_group
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
def main(context: object,
         subscription_id: str,
         resource_group: str,
         location: str,
         aad_app_id: str,
         aad_key: str,
         aad_directory_id: str) -> None:
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
def storage(context: object) -> None:
    pass

@storage.group()
@click.pass_context
def fileshare(context: object) -> None:
    pass

@fileshare.command(name='upload')
@click.pass_context
def upload_to_fileshare(context: object) -> None:
    pass


main.add_command(storage)
storage.add_command(fileshare)
fileshare.add_command(upload_to_fileshare)

if __name__ == '__main__':
    main()
