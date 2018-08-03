import logging
import time

from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    SkuName,
    Kind
)

import cli.utils

LOGGER = logging.getLogger(__name__)
STORAGE_ACCOUNT_TYPE = 'storage account'
ONE_SECOND = 1

def set_storage_client(context):
    if 'storage_client' not in context.obj:
        context.obj['storage_client'] = StorageManagementClient(
            credentials=context.obj['aad_credentials'],
            subscription_id=context.obj['subscription_id']
        )

def set_storage_account_key(context):
    storage_keys = context.obj['storage_client'].storage_accounts.list_keys(
        context.obj['resource_group'],
        context.obj['storage_account']
    )
    storage_keys = {v.key_name: v.value for v in storage_keys.keys}
    storage_account_key = storage_keys['key1']
    context.obj['storage_account_key'] = storage_account_key

def create_acct_if_not_exists(context):
    storage_acct_name = context.obj['storage_account']
    storage_client = context.obj['storage_client']
    availability = storage_client.storage_accounts.check_name_availability(
        storage_acct_name)
    if not availability.name_available:
        if availability.reason.value == 'AlreadyExists':
            LOGGER.info(cli.utils.already_exists(STORAGE_ACCOUNT_TYPE,
                                                 storage_acct_name))
            set_storage_account_key(context)
        else:
            LOGGER.warning(cli.utils.create_failed(STORAGE_ACCOUNT_TYPE,
                                                   storage_acct_name,
                                                   availability.message))
            return False
    else:
        storage_client.storage_accounts.create(
            context.obj['resource_group'],
            storage_acct_name,
            StorageAccountCreateParameters(
                sku=Sku(SkuName.standard_ragrs),
                kind=Kind.storage,
                location=context.obj['location']
            )
        )
        LOGGER.info(cli.utils.created(STORAGE_ACCOUNT_TYPE, storage_acct_name))

        # wait for storage account to be provisioning state 'Succeeded'
        print('Storage account is being allocated...')
        provisioning_state = get_storage_account_state(context)
        while provisioning_state != 'Succeeded':
            time.sleep(ONE_SECOND)
            print('Waiting on storage account allocation...')
            provisioning_state = get_storage_account_state(context)
        set_storage_account_key(context)
    return True

def get_storage_account_state(context):
    return context.obj['storage_client'].storage_accounts.get_properties(
        context.obj['resource_group'],
        context.obj['storage_account']).provisioning_state.value
