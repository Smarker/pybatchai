from azure.storage.file import FileService
import blobxfer.models.azure as azmodels

import cli.notify
import cli.blobxfer_util

def set_fileshare_service(context):
    context.obj['fileshare_service'] = FileService(
        context.obj['storage_account_name'],
        context.obj['storage_account_key'])

def created_fileshare(context):
    shares = list(context.obj['fileshare_service'].list_shares(include_snapshots=True))
    return any(context.obj['fileshare_name'] == share.name for share in shares)

def create_fileshare_if_not_exists(context):
    fileshare_name = context.obj['fileshare_name']
    if not created_fileshare(context):
        context.obj['fileshare_service'].create_share(fileshare_name,
                                                      fail_on_exist=False)
        cli.notify.print_created(fileshare_name)
    else:
        cli.notify.print_already_exists(fileshare_name)

def upload(context):
    cli.blobxfer_util.start_uploader(context,
                                     azmodels.StorageModes.File,
                                     context.obj['fileshare_name'])

def download(context):
    cli.blobxfer_util.start_downloader(context,
                                       azmodels.StorageModes.File,
                                       context.obj['fileshare_name'])
