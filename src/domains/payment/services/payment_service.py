from fastapi import BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Any, List, Dict, Optional
import json
from ..configs.constants import *
from ...cache import ICache
from ...service_api import IServiceApi
from ..models import dtos, value_objects as vo
from ..models.stripe import stripe_dtos
from ....infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from ....configs.exceptions import *
from ....configs.conf import SHORT_TERM_TTL, LONG_TERM_TTL
from ....routers.res.response import res_success
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class PaymentService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache
        self.sign_header = 'Stripe-Signature'

    def __get_cache(self, role_id: int) -> (Optional[Dict]):
        return self.cache.get(key=f'pay:{role_id}')

    def __set_cache(self, role_id: int, payment_status: Dict) -> (bool):
        return self.cache.set(key=f'pay:{role_id}', val=payment_status, ex=SHORT_TERM_TTL)
    
    def __delete_cache(self, role_id: int) -> (bool):
        return self.cache.delete(key=f'pay:{role_id}')

    def __get_role_id_by_cus_id(self, customer_id: str) -> (Optional[int]):
        role_id_str = self.cache.get(key=f'pay_handling:{customer_id}')
        return int(role_id_str)

    def __set_role_id_by_cus_id(self, customer_id: str, role_id: int) -> (bool):
        return self.cache.set(key=f'pay_handling:{customer_id}', val=str(role_id), ex=SHORT_TERM_TTL)

    def __delete_role_id_by_cus_id(self, customer_id: str) -> (bool):
        return self.cache.delete(key=f'pay_handling:{customer_id}')

    '''
    1. Upsert customer:
        1. Get payment status (with customer_id) from cache
        2. Cache missed:  
            1. Call PUT customer API
            2. Call GET subscribe API
            3. Cache payment status and return
        3. Cache hit:
            1. return payment status (with customer_id)
    '''

    def payment_method(self, host: str, user_data: stripe_dtos.StripeUserPaymentRequestDTO) -> (Dict):
        role_id = user_data.role_id
        payment_status = self.__get_cache(role_id)
        if payment_status is None:
            # create customer
            url = f'{host}/{STRIPE}/payment-method'
            self.req.simple_put(url=url, json=user_data.dict())
            
            # get payment status & cache it
            payment_status = self.__get_latest_cached_payment_status(host, role_id)

        return payment_status
    
    def __get_latest_cached_payment_status(self, host: str, role_id: int) -> (Dict):
        url = f'{host}/{STRIPE}/subscribe'
        payment_status = self.req.simple_get(url=url, params={
            'role_id': role_id,
        })
        self.__set_cache(role_id, payment_status)
        
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
            payment_status = self.__get_latest_cached_payment_status(host, role_id)

        return payment_status
            

    def __bg_processing(self, bg_tasks: BackgroundTasks, url: str, json: Dict, role_id: int) -> (None):
        bg_tasks.add_task(self.req.simple_post, url=url, json=json)
        bg_tasks.add_task(log.error, msg=f'role_id:{role_id}, req:{url}')
        bg_tasks.add_task(self.__delete_cache, role_id=role_id)
        bg_tasks.add_task(log.error, msg=f'role_id:{role_id}, delete payment cache')


    def __refresh_payment_status(self, host: str, role_id: int) -> (Dict):
        self.__delete_cache(role_id)
        return self.__get_latest_cached_payment_status(host, role_id)


    def subscribe(self, bg_tasks: BackgroundTasks, host: str, subscription: stripe_dtos.StripeSubscribeRequestDTO) -> (None):
        role_id = subscription.role_id
        payment_status = self.__refresh_payment_status(host, role_id)
        
        status = PaymentStatusEnum(payment_status['status'])
        if status in UNABLE_TO_SUBSCRIBE:
            raise ClientException(msg=status)
        
        if payment_status['valid']:
            raise ClientException(msg='not_yet_expired')
        
        self.__set_role_id_by_cus_id(payment_status['customer_id'], role_id)
        self.__bg_processing(
            bg_tasks, f'{host}/{STRIPE}/subscribe', subscription.dict(), role_id)


    def unsubscribe(self, bg_tasks: BackgroundTasks, host: str, unsubscription: dtos.UnsubscribeRequestDTO) -> (None):
        role_id = unsubscription.role_id
        payment_status = self.__refresh_payment_status(host, role_id)
        
        status = PaymentStatusEnum(payment_status['status'])
        if status in UNABLE_TO_CANCEL_SUBSCRIBE:
            raise ClientException(msg=status)
        
        self.__set_role_id_by_cus_id(payment_status['customer_id'], role_id)
        self.__bg_processing(
            bg_tasks, f'{host}/{STRIPE}/unsubscribe', unsubscription.dict(), role_id)

    '''
    6. Stripe -> gateway -> payment service
    '''
    async def webhook(self, host: str, req: Request) -> (JSONResponse):
        byte_data: Optional[bytes] = None
        try:
            byte_data = await req.body()
            customer_id = self.__parse_stripe_customer_id(byte_data)
            role_id = self.__get_role_id_by_cus_id(customer_id)
            if role_id is None:
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
            
            self.__delete_role_id_by_cus_id(customer_id)
            self.__delete_cache(role_id)
            return JSONResponse(content=event_data, status_code=201)
        
        except Exception as e:
            log.error(f'webhook error: host:%s, req_header:%s, req_body:%s, error:%s', 
                      host, req.headers, byte_data.decode(), e.__str__())
            raise ServerException(msg='internal server error')
        
        
    def __parse_stripe_customer_id(self, byte_data: bytes) -> (str):
        s = byte_data.decode()
        j = json.loads(s)
        return j['data']['object']['customer']

  
class PaymentPlanService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache


    async def __get_cache(self) -> (Optional[Dict]):
        return await self.cache.get(key='pay_plans')

    async def __set_cache(self, payment_plans: List[Dict], exipre: int) -> (bool):
        return await self.cache.set(key='pay_plans', val=payment_plans, ex=exipre)

    '''
    long term cache: 14 days as default
    '''
    def list_plans(self, host: str) -> (List[Dict]):
        plans = self.__get_cache()
        if plans is None:
            url = f'{host}/{STRIPE}/plans'
            plans = self.req.simple_get(url=url)
            self.__set_cache(plans, exipre=LONG_TERM_TTL)
            
        return plans
