import logging

from msrestazure.azure_exceptions import CloudError
from azure.mgmt.batchai import models

import cli.utils

LOGGER = logging.getLogger(__name__)
CLUSTER_TYPE = 'cluster'

def create_cluster(context):
    azure_file_shares, azure_blob_file_systems = None, None

    if not (context.obj['password'] or context.obj['ssh_key']):
        LOGGER.error('Cluster creation requires password or ssh_key')
        return

    parameters = models.ClusterCreateParameters(
        vm_size=context.obj['vm_size'],
        vm_priority=context.obj['vm_priority'],
        scale_settings=models.ScaleSettings(
            auto_scale=models.AutoScaleSettings(
                minimum_node_count=context.obj['min_nodes'],
                maximum_node_count=context.obj['max_nodes']
            )
        ),
        user_account_settings=models.UserAccountSettings(
            admin_user_name=context.obj['user_name'],
            admin_user_password=context.obj['password'],
            admin_user_ssh_public_key=context.obj['ssh_key']
        )
    )

    if context.obj['image']:
        parameters['virtual_machine_configuration'] \
          = models.VirtualMachineConfiguration(
              image_reference=context.obj['image']
        )

    if context.obj['afs_name']:
        if not context.obj['storage_account_name']:
            LOGGER.error('Use of AFS requires --storage-account-name')
            return

        afs_url = 'https://{}.file.core.windows.net/{}'.format(
            context.obj['storage_account_name'],
            context.obj['afs_name']
        )

        azure_file_shares = [
            models.AzureFileShareReference(
                account_name=context.obj['storage_account_name'],
                azure_file_url=afs_url,
                credentials=models.AzureStorageCredentialsInfo(
                    account_key=context.obj['storage_account_key']
                ),
                relative_mount_path=context.obj['afs_mount_path']
            )
        ]

    if context.obj['bfs_name']:
        if not context.obj['storage_account_name']:
            LOGGER.error('Use of BFS requires --storage-account-name')
            return

        azure_blob_file_systems = [
            models.AzureBlobFileSystemReference(
                account_name=context.obj['storage_account_name'],
                container_name=context.obj['bfs_name'],
                credentials=models.AzureStorageCredentialsInfo(
                    account_key=context.obj['storage_account_key']
                ),
                relative_mount_path=context.obj['bfs_mount_path']
            )
        ]

    if context.obj['afs_name'] or context.obj['bfs_name']:
        parameters['node_setup'] = models.NodeSetup(
            mount_volumes=models.MountVolumes(
                azure_blob_file_systems=azure_blob_file_systems,
                azure_file_shares=azure_file_shares
            )
        )

    cluster_status = context.obj['batchai_client'].clusters.create(
        context.obj['resource_group'],
        context.obj['workspace'],
        context.obj['cluster_name'],
        parameters
    ).result()
    LOGGER.info(cluster_status)

def delete_cluster(context):
    cluster_name = context.obj['cluster_name']
    if cluster_exists(context):
        context.obj['batchai_client'].clusters.delete(
            context.obj['resource_group'],
            context.obj['workspace'],
            cluster_name)
        LOGGER.info(cli.utils.deleted(CLUSTER_TYPE, cluster_name))

def show_cluster(context):
    cluster_details = cluster_exists(context)
    if cluster_details:
        print_cluster_status(context, cluster_details)

def print_cluster_status(context, cluster):
    """Print the status of your batchai cluster."""
    LOGGER.info('''
cluster name:  %s
cluster state: %s
--------------------
Target:           %d
Allocated:        %d
Idle:             %d
Unusable:         %d
Running:          %d
Preparing:        %d
Leaving:          %d''',
                context.obj['cluster_name'],
                cluster.allocation_state,
                cluster.scale_settings.manual.target_node_count,
                cluster.current_node_count,
                cluster.node_state_counts.idle_node_count,
                cluster.node_state_counts.unusable_node_count,
                cluster.node_state_counts.running_node_count,
                cluster.node_state_counts.preparing_node_count,
                cluster.node_state_counts.leaving_node_count)
    if not cluster.errors:
        return
    for error in cluster.errors:
        LOGGER.error(cli.utils.create_failed(CLUSTER_TYPE,
                                             context.obj['cluster_name'],
                                             error.message))
        if error.details:
            LOGGER.error('Error Details:')
            for detail in error.details:
                LOGGER.error('%s: %s', detail.name, detail.value)

def cluster_exists(context):
    cluster_name = context.obj['cluster_name']
    try:
        cluster_details = context.obj['batchai_client'].clusters.get(
            context.obj['resource_group'],
            context.obj['workspace'],
            cluster_name)
        return cluster_details
    except CloudError:
        LOGGER.warning(cli.utils.does_not_exist(CLUSTER_TYPE, cluster_name))
        return False
