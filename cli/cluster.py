import logging

from msrestazure.azure_exceptions import CloudError
from azure.mgmt.batchai import models

import cli.utils

LOGGER = logging.getLogger(__name__)
CLUSTER_TYPE = 'cluster'

def create_cluster(context):
    params = models.ClusterCreateParameters(
        vm_size=context.obj['vm_size'],
        user_account_settings=models.UserAccountSettings(
            admin_user_name=context.obj['user_name'],
            admin_user_password=context.obj['password'],
            admin_user_ssh_public_key=context.obj['ssh_key'],
        ),
        vm_priority=context.obj['vm_priority'],
        # scale_settings=models.ScaleSettings(
        #     manual=models.ManualScaleSettings(target_node_count=context.obj['node_count'])
        # ),
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=context.obj['image']
        )
    )

    cluster_status = context.obj['batchai_client'].clusters.create(
        context.obj['resource_group'],
        context.obj['workspace'],
        context.obj['cluster_name'],
        params
    ).result()
    print(cluster_status)

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
