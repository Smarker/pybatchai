from azure.storage.blob import (
    BlockBlobService,
    PublicAccess
)
import blobxfer.models.azure as azmodels

import cli.blobxfer_util

def set_blob_storage_service(context):
    context.obj['blob_storage_service'] = BlockBlobService(
        account_name=context.obj['storage_account_name'],
        account_key=context.obj['storage_account_key'])

def set_container_public_access(context):
    context.obj['blob_storage_service'].set_container_acl(
        context.obj['container_name'], public_access=PublicAccess.Container)

def upload(context):
    cli.blobxfer_util.start_uploader(context,
                                     azmodels.StorageModes.Block,
                                     context.obj['container_name'])
    set_container_public_access(context)

def download(context):
    cli.blobxfer_util.start_downloader(context,
                                       azmodels.StorageModes.Block,
                                       context.obj['container_name'])
