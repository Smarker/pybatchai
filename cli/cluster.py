'''
import azure.mgmt.batchai.models as models

import cli.notify

def create_cluster(context):
    """Create a batchai cluster."""
    parameters = models.ClusterCreateParameters(
        vm_size=context.obj['vm_size'],
        user_account_settings=models.UserAccountSettings(
            admin_user_name=context.obj['admin_username'],
            admin_user_password=context.obj['admin_password'],
            admin_user_ssh_public_key=context.obj['admin_ssh_public_key'],
        ),
        vm_priority='dedicated',
        scale_settings=models.ScaleSettings(
            manual=models.ManualScaleSettings(target_node_count=context.obj['node_count'])
        ),
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=context.obj['image']
        )
    )

    cluster_status = context.obj['batchai_client'].clusters.create(
        context.obj['resource_group'],
        context.obj['workspace'],
        context.obj['cluster_name'],
        parameters
    ).result()
    print(cluster_status)

def monitor_cluster(context):
    """Monitor the status of your batchai cluster."""
    cluster = context.obj['batchai_client'].clusters.get(
        context.obj['resource_group'],
        context.obj['workspace'],
        context.obj['cluster_name'])
    print_cluster_status(context, cluster)

def print_cluster_status(context, cluster):
    """Print the status of your batchai cluster."""
    print(
        'Cluster state: {0} Target: {1}; Allocated: {2}; Idle: {3}; '
        'Unusable: {4}; Running: {5}; Preparing: {6}; Leaving: {7}'.format(
            cluster.allocation_state,
            cluster.scale_settings.manual.target_node_count,
            cluster.current_node_count,
            cluster.node_state_counts.idle_node_count,
            cluster.node_state_counts.unusable_node_count,
            cluster.node_state_counts.running_node_count,
            cluster.node_state_counts.preparing_node_count,
            cluster.node_state_counts.leaving_node_count))
    if not cluster.errors:
        return
    for error in cluster.errors:
        cli.notify.print_create_failed(context.obj['cluster_name'],
                                       error.message)
        if error.details:
            print('Details:')
            for detail in error.details:
                print('{0}: {1}'.format(detail.name, detail.value))
'''

import logging

from msrestazure.azure_exceptions import CloudError

import cli.utils

LOGGER = logging.getLogger(__name__)
CLUSTER_TYPE = 'cluster'

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
