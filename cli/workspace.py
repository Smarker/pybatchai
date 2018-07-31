import cli.notify

def created_workspace(context):
    all_workspaces = list(context.obj['batchai_client'].workspaces.list())
    return any(context.obj['workspace'] == workspace.name for workspace in all_workspaces)

def create_workspace_if_not_exists(context):
    workspace_name = context.obj['workspace']
    if not created_workspace(context):
        try:
            context.obj['batchai_client'].workspaces.create(context.obj['resource_group'], workspace_name, context.obj['location'])
            cli.notify.print_created(workspace_name)
        except Exception as e:
            cli.notify.print_create_failed(workspace_name, e)
            return False
    else:
        cli.notify.print_already_exists(workspace_name)
    return True