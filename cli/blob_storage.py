def set_blob_storage_service():
    resource_group_name = context.obj['resource_group']
    storage_account_name = context.obj['storage_account_name']
    cached_key = (resource_group_name, storage_account_name)
    blob_service = self._cached_blob_services.get(cached_key)

    if blob_service is None:
        with self._blob_services_lock:
            blob_service = self._cached_blob_services.get(cached_key)
            if blob_service is None:
                blob_service = BlockBlobService(account_name=storage_account_name,
                                                account_key=context.obj['storage_account_key'])
                self._cached_blob_services[cached_key] = blob_service
    context.obj['blob_storage_service'] = blob_service
    