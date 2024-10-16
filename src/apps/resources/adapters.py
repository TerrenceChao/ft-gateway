from .manager import io_resource_manager
from .handlers.http_resource import HttpResourceHandler
from ...infra.client.service_api_dapter import ServiceApiAdapter
from ...infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter

# service api(service client)
http_resource_handler: HttpResourceHandler = io_resource_manager.get('http')
service_client = ServiceApiAdapter(http_resource_handler)

# cache
cache_resource_handler = io_resource_manager.get('ddb_cache')
gw_cache = DynamoDbCacheAdapter(cache_resource_handler)
