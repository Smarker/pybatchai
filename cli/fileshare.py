from azure.storage.file import FileService
import blobxfer.api
import blobxfer.models.azure as azmodels
import blobxfer.models.options as options

import cli.notify

def set_fileshare_service(context):
    context.obj['fileshare_service'] = FileService(
        context.obj['storage_account_name'],
        context.obj['storage_account_key'])

def created_fileshare(context):
    shares = list(context.obj['fileshare_service'].list_shares(include_snapshots=True))
    return any(context.obj['fileshare_name'] == share.name for share in shares)

def create_file_share_if_not_exists(context):
    fileshare_name = context.obj['fileshare_name']
    if not created_fileshare(context):
        try:
            context.obj['fileshare_service'].create_share(fileshare_name,
                                                          fail_on_exist=False)
            cli.notify.print_created(fileshare_name)
        except Exception as e:
            cli.notify.print_create_failed(fileshare_name, e)
            return
    else:
        cli.notify.print_already_exists(fileshare_name)

def created_directory(context):
    directories_and_files = context.obj['fileshare_service'].list_directories_and_files(context.obj['fileshare_name'])
    return any(context.obj['fileshare_directory'] == dir_or_file.name for dir_or_file in directories_and_files)

def create_directory_if_not_exists(context):
    fileshare_directory = context.obj['fileshare_directory']
    if not created_directory(context):
        try:
            context.obj['fileshare_service'].create_directory(
                context.obj['fileshare_name'],
                fileshare_directory,
                fail_on_exist=False)
            cli.notify.print_created(fileshare_directory)
        except Exception as e:
            cli.notify.print_create_failed(fileshare_directory, e)
    else:
        cli.notify.print_already_exists(fileshare_directory)

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
        mode=azmodels.StorageModes.File,
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
        remote_path=context.obj['fileshare_directory'],
        storage_account=context.obj['storage_account_name']
    )
    specification.add_azure_destination_path(azure_dest_path)
    blobxfer.api.Uploader(
        general_options,
        credentials,
        specification
    ).start()

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
        mode=azmodels.StorageModes.File,
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
        remote_path=context.obj['fileshare_directory'],
        storage_account=context.obj['storage_account_name']
    )
    specification.add_azure_source_path(azure_src_path)
    blobxfer.api.Downloader(
        general_options,
        credentials,
        specification
    ).start()
