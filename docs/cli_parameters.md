# CLI Parameters

## Required parameters for all cli commands

| parameter       | type | description |
| --------------- | ---- | ----------- |
| `subscription-id` | str  | [Sign up](https://azure.microsoft.com/en-us/free/) to get an Azure subscription id |
| `resource-group` | str | Azure resource group name. An Azure [resource group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-overview#resource-groups) is a logical grouping of Azure resources. |
| `location` | str | Azure region to create resources. `eastus` is recommended as this region supports Azures `NC-Series` or GPU-enabled machines. |
| `aad-app-id` | str | AAD Application Id. |
| `aad-key` | str | AAD Secret Key. |
| `aad-directory-id` | str | AAD Directory Id. |

**NOTE:** The application **MUST** be assigned a `Contributor Role`.

### Azure Active Directory (AAD)

To use `pybatchai`, you must obtain Azure Active Directory (AAD) Credentials
 (`aad_app_id`, `aad_key`, `aad_directory_id`) in the `Azure Portal`.

AAD manages application permissions. As `pybatchai` will create and manages
 resources, this application will need to be assigned a [Contributor role](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#contributor),
  otherwise you will not be able to use this cli.

To obtain AAD credentials refer either this [brief guide](https://github.com/Azure/BatchAI/blob/master/recipes/Preparation.md#using-portal)
or [detailed guide](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal).