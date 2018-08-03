import logging

from azure.storage.file import FileService
import blobxfer.models.azure as azmodels

import cli.utils
import cli.blobxfer_util

LOGGER = logging.getLogger(__name__)
FILESHARE_TYPE = 'fileshare'

def set_fileshare_service(context):
    context.obj['fileshare_service'] = FileService(
        context.obj['storage_account'],
        context.obj['storage_account_key']
    )

def created_fileshare(context):
    shares = list(context.obj['fileshare_service'].list_shares(include_snapshots=True))
    return any(context.obj['fileshare'] == share.name for share in shares)

def create_fileshare_if_not_exists(context):
    fileshare = context.obj['fileshare']
    if not created_fileshare(context):
        context.obj['fileshare_service'].create_share(fileshare,
                                                      fail_on_exist=False)
        LOGGER.info(cli.utils.created(FILESHARE_TYPE, fileshare))
    else:
        LOGGER.info(cli.utils.already_exists(FILESHARE_TYPE, fileshare))

def upload(context):
    cli.blobxfer_util.start_uploader(context,
                                     azmodels.StorageModes.File,
                                     context.obj['fileshare'])

def download(context):
    cli.blobxfer_util.start_downloader(context,
                                       azmodels.StorageModes.File,
                                       context.obj['fileshare'])
