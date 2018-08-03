import blobxfer.api
import blobxfer.models.azure as azmodels
import blobxfer.models.options as options

DOWNLOAD = 1
UPLOAD = 2
TIMEOUT = blobxfer.api.TimeoutOptions(
    connect=None,
    read=None,
    max_retries=1000
)
SKIP_ON_OPTIONS = blobxfer.api.SkipOnOptions(
    filesize_match=None,
    lmt_ge=None,
    md5_match=None
)
def start_uploader(context, mode, remote_path):
    concurrency = create_concurrency_options(action=UPLOAD)
    general_options = create_general_options(concurrency, TIMEOUT)
    upload_options = create_upload_options(storage_mode=mode)
    local_source_path = create_local_source_path(context)
    specification = blobxfer.api.UploadSpecification(upload_options,
                                                     SKIP_ON_OPTIONS,
                                                     local_source_path)

    credentials = blobxfer.api.AzureStorageCredentials(general_options)
    credentials.add_storage_account(name=context.obj['storage_account'],
                                    key=context.obj['storage_account_key'],
                                    endpoint='core.windows.net')

    azure_dest_path = blobxfer.api.AzureDestinationPath()
    azure_dest_path.add_path_with_storage_account(
        remote_path=remote_path,
        storage_account=context.obj['storage_account']
    )
    specification.add_azure_destination_path(azure_dest_path)

    blobxfer.api.Uploader(
        general_options,
        credentials,
        specification
    ).start()

def start_downloader(context, mode, remote_path):
    concurrency = create_concurrency_options(action=DOWNLOAD)
    general_options = create_general_options(concurrency, TIMEOUT)
    download_options = create_download_options(storage_mode=mode)
    local_destination_path = create_local_dest_path(context)
    specification = blobxfer.api.DownloadSpecification(download_options,
                                                       SKIP_ON_OPTIONS,
                                                       local_destination_path)

    credentials = blobxfer.api.AzureStorageCredentials(general_options)
    credentials.add_storage_account(name=context.obj['storage_account'],
                                    key=context.obj['storage_account_key'],
                                    endpoint='core.windows.net')

    azure_src_path = blobxfer.api.AzureSourcePath()
    azure_src_path.add_path_with_storage_account(
        remote_path=remote_path,
        storage_account=context.obj['storage_account']
    )
    specification.add_azure_source_path(azure_src_path)

    blobxfer.api.Downloader(
        general_options,
        credentials,
        specification
    ).start()

def create_concurrency_options(action=DOWNLOAD):
    return blobxfer.api.ConcurrencyOptions(
        crypto_processes=0,
        md5_processes=0,
        disk_threads=16,
        transfer_threads=32,
        action=action
    )

def create_general_options(concurrency, timeout):
    return blobxfer.api.GeneralOptions(
        log_file='log.txt',
        progress_bar=True,
        concurrency=concurrency,
        timeout=timeout
    )

def create_upload_options(storage_mode=azmodels.StorageModes.Block):
    return blobxfer.api.UploadOptions(
        access_tier=None,
        chunk_size_bytes=0,
        delete_extraneous_destination=False,
        mode=storage_mode,
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

def create_download_options(storage_mode=azmodels.StorageModes.Block):
    return blobxfer.api.DownloadOptions(
        check_file_md5=False,
        chunk_size_bytes=4194304,
        delete_extraneous_destination=False,
        mode=storage_mode,
        overwrite=True,
        recursive=True,
        rename=False,
        restore_file_attributes=False,
        rsa_private_key=None,
        strip_components=0
    )

def create_local_source_path(context):
    local_source_path = blobxfer.api.LocalSourcePath()
    local_source_path.add_includes(['*.*'])
    local_source_path.add_excludes([])
    local_source_path.add_paths([context.obj['local_path']])
    return local_source_path

def create_local_dest_path(context):
    local_destination_path = blobxfer.api.LocalDestinationPath()
    local_destination_path.is_dir = True
    local_destination_path.path = context.obj['local_path']
    return local_destination_path
