from fastapi import BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Any, List, Dict, Optional
import json
from ..configs.constants import *
from ...cache import ICache
from ...service_api import IServiceApi
from ..models import dtos, value_objects as vo
from ....infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from ....configs.exceptions import *
from ....configs.conf import SHORT_TERM_TTL
from ....routers.res.response import res_success
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class PaymentService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache
        self.sign_header = 'Stripe-Signature'

    def __get_cache(self, role_id: int) -> (Optional[Dict]):
        return self.cache.get(key=f'pay:{str(role_id)}')

    def __set_cache(self, role_id: int, payment_status: Dict) -> (bool):
        return self.cache.set(key=f'pay:{str(role_id)}', val=payment_status, ex=SHORT_TERM_TTL)

    def __get_customer(self, customer_id: str) -> (Optional[bool]):
        return self.cache.get(key=f'pay_handling:{customer_id}')

    def __set_customer(self, customer_id: str) -> (bool):
        return self.cache.set(key=f'pay_handling:{customer_id}', val='1', ex=SHORT_TERM_TTL)

    def __delete_customer(self, customer_id: str) -> (bool):
        return self.cache.delete(key=f'pay_handling:{customer_id}')

    '''
    1. Upsert customer:
        1. Get payment status (with customer_id) from cache
        2. Cache missed:  
            1. Call PUT customer API
            2. [step 2:  Get payment status]
        3. Cache hit:
            1. return payment status (with customer_id)
    '''

    def upsert_customer(self, host: str, user: dtos.UserDTO) -> (Dict):
        payment_status = self.__get_cache(user.role_id)
        if payment_status is None:
            url = f'{host}/{STRIPE}/customer'
            self.req.simple_put(url=url, json=user.dict())
            payment_status = self.get_payment_status(host, user.role_id)

        return payment_status

    '''
    2. Get payment status:
        1. Get payment status from cache
        2. Cache missed:  
            1. Call GET subscribe API
            2. Cache payment status and return
        3. Cache hit: 
            1. return payment status
    '''

    def get_payment_status(self, host: str, role_id: int) -> (Dict):
        payment_status = self.__get_cache(role_id)
        if payment_status is None:
            url = f'{host}/{STRIPE}/subscribe'
            payment_status = self.req.simple_get(url=url, params={
                'role_id': role_id,
            })
            self.__set_cache(role_id, payment_status)

        return payment_status

    def __handling_status(self, host: str, role_id: int) -> (Dict):
        payment_status = self.get_payment_status(host, role_id)
        if payment_status['status'] == 'handling':
            raise ClientException(msg='subscription_is_being_handled')

        else:
            payment_status['status'] = 'handling'
            self.__set_cache(role_id, payment_status)
            self.__set_customer(payment_status['customer_id'])
            
        return payment_status

    def __bg_post_request(self, bg_tasks: BackgroundTasks, url: str, json: Dict) -> (None):
        bg_tasks.add_task(self.req.simple_post, url=url, json=json)

    '''
    3. Subscribe (耗時操作)
        1. [step 2:  Get payment status]
            1. Reject if payment_status: handling (不允許用戶頻繁改變策略或不斷重試)
            2. Set payment_status: handling if UNPAID/PAID/CANCELED;
            3. 當需要 Stripe 透過 gateway callback 時：
                1. Set cache:  <costumer_id:True>
        2. Return 202(accepted)
        3. [async] 
            1. Call POST subscribe API
    '''

    def subscribe(self, bg_tasks: BackgroundTasks, host: str, subscription: dtos.SubscribeRequestDTO) -> (None):
        self.__handling_status(host, subscription.role_id)
        self.__bg_post_request(
            bg_tasks, f'{host}/{STRIPE}/subscribe', subscription.dict())

    '''
    4. Unsubscribe (耗時操作)
        1. [step 2:  Get payment status] 
            1. Reject if payment_status: handling (不允許用戶頻繁改變策略或不斷重試)
            2. Set payment_status: handling if UNPAID/PAID/CANCELED;
            3. 當需要 Stripe 透過 gateway callback 時：
                1. Set cache:  <costumer_id:True>
        2. Return 202(accepted) 
        3. [async] 
            1. Call POST unsubscribe API
    '''

    def unsubscribe(self, bg_tasks: BackgroundTasks, host: str, unsubscription: dtos.UnsubscribeRequestDTO) -> (None):
        self.__handling_status(host, unsubscription.role_id)
        self.__bg_post_request(
            bg_tasks, f'{host}/{STRIPE}/unsubscribe', unsubscription.dict())

    '''
    6. Stripe -> gateway -> payment service
    '''
    async def webhook(self, host: str, req: Request) -> (JSONResponse):
        byte_data: bytes = None
        try:
            byte_data = await req.body()
            customer_id = self.__parse_stripe_customer_id(byte_data)
            if self.__get_customer(customer_id) is None:
                res_body = res_success(msg='accepted', code='20200')
                return JSONResponse(content=res_body, status_code=202)

            headers = {
                self.sign_header: req.headers.get(self.sign_header),
            }
            
            event_data = self.req.post_data(
                url=f'{host}/{STRIPE}/webhook',
                byte_data=byte_data,
                headers=headers,
            )
            
            self.__delete_customer(customer_id)
            return JSONResponse(content=event_data, status_code=201)
        
        except Exception as e:
            log.error(f'webhook error: host:%s, req_header:%s, req_body:%s, error:%s', 
                      host, req.headers, byte_data.decode(), e.__str__())
            raise ServerException(msg='internal server error')
        
    def __parse_stripe_customer_id(self, byte_data: bytes) -> (str):
        s = byte_data.decode()
        j = json.loads(s)
        return j['data']['object']['customer']
        
