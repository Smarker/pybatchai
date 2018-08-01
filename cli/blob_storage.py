from azure.storage.blob import (
    BlockBlobService,
    PublicAccess
)
import blobxfer.api
import blobxfer.models.azure as azmodels
import blobxfer.models.options as options

def set_blob_storage_service(context):
    context.obj['blob_storage_service'] = BlockBlobService(
        account_name=context.obj['storage_account_name'],
        account_key=context.obj['storage_account_key'])

def create_container_if_not_exists(context):
    context.obj['blob_storage_service'].create_container(
        context.obj['container_name'])
    set_container_public_access_level(context)

def set_container_public_access_level(context):
    context.obj['blob_storage_service'].set_container_acl(
        context.obj['container_name'], public_access=PublicAccess.Container)

DOWNLOAD = 1
UPLOAD = 2
timeout = blobxfer.api.TimeoutOptions(
    connect=None,
    read=None,
    max_retries=1000
)
skip_on_options = blobxfer.api.SkipOnOptions(
    filesize_match=None,
    lmt_ge=None,
    md5_match=None
)
def upload(context):
    concurrency = blobxfer.api.ConcurrencyOptions(
        crypto_processes=0,
        md5_processes=0,
        disk_threads=16,
        transfer_threads=32,
        action=UPLOAD
    )
    general_options = blobxfer.api.GeneralOptions(
        log_file='log.txt',
        progress_bar=True,
        concurrency=concurrency,
        timeout=timeout
    )
    upload_options = blobxfer.api.UploadOptions(
        access_tier=None,
        chunk_size_bytes=0,
        delete_extraneous_destination=False,
        mode=azmodels.StorageModes.Block,
        one_shot_bytes=0,
        overwrite=True,
        recursive=True,
        rename=False,
        rsa_public_key=None,
        stdin_as_page_blob_size=None,
        store_file_properties=options.FileProperties(
            attributes=False,
            md5=False,
        ),
        strip_components=0,
        vectored_io=blobxfer.api.VectoredIoOptions(
            stripe_chunk_size_bytes=0,
            distribution_mode='stripe'
        )
    )

    local_source_path = blobxfer.api.LocalSourcePath()
    local_source_path.add_includes(['*.*'])
    local_source_path.add_excludes([])
    local_source_path.add_paths([context.obj['data_dir']])

    specification = blobxfer.api.UploadSpecification(upload_options,
                                                     skip_on_options,
                                                     local_source_path)

    credentials = blobxfer.api.AzureStorageCredentials(general_options)
    credentials.add_storage_account(name=context.obj['storage_account_name'],
                                    key=context.obj['storage_account_key'],
                                    endpoint='core.windows.net')

    azure_dest_path = blobxfer.api.AzureDestinationPath()
    azure_dest_path.add_path_with_storage_account(
        remote_path=context.obj['container_name'],
        storage_account=context.obj['storage_account_name']
    )
    specification.add_azure_destination_path(azure_dest_path)
    blobxfer.api.Uploader(
        general_options,
        credentials,
        specification
    ).start()

    set_container_public_access_level(context)

def download(context):
    concurrency = blobxfer.api.ConcurrencyOptions(
        crypto_processes=0,
        md5_processes=0,
        disk_threads=16,
        transfer_threads=32,
        action=DOWNLOAD
    )
    general_options = blobxfer.api.GeneralOptions(
        log_file='log.txt',
        progress_bar=True,
        concurrency=concurrency,
        timeout=timeout
    )
    download_options = blobxfer.api.DownloadOptions(
        check_file_md5=False,
        chunk_size_bytes=4194304,
        delete_extraneous_destination=False,
        mode=azmodels.StorageModes.Block,
        overwrite=True,
        recursive=True,
        rename=False,
        restore_file_attributes=False,
        rsa_private_key=None,
        strip_components=0
    )

    local_destination_path = blobxfer.api.LocalDestinationPath()
    local_destination_path.is_dir=True
    local_destination_path.path = context.obj['local_download_path']

    specification = blobxfer.api.DownloadSpecification(download_options,
                                                     skip_on_options,
                                                     local_destination_path)

    credentials = blobxfer.api.AzureStorageCredentials(general_options)
    credentials.add_storage_account(name=context.obj['storage_account_name'],
                                    key=context.obj['storage_account_key'],
                                    endpoint='core.windows.net')

    azure_src_path = blobxfer.api.AzureSourcePath()
    azure_src_path.add_path_with_storage_account(
        remote_path=context.obj['container_name'],
        storage_account=context.obj['storage_account_name']
    )
    specification.add_azure_source_path(azure_src_path)
    blobxfer.api.Downloader(
        general_options,
        credentials,
        specification
    ).start()
