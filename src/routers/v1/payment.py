import requests
from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks, \
    Request, Depends, Header, Path, Query, Body, Form
from ..req.authorization import AuthRoute, \
    token_required, \
    verify_token_by_subscribe_status, \
    verify_token_by_payment_operation
from ..res.response import *
from ...domains.payment.models import dtos, value_objects as vo
from ...domains.payment.models.stripe import stripe_dtos, stripe_vos
from ...domains.payment.services.payment_service import PaymentService, PaymentPlanService
from ...apps.service_api_dapter import ServiceApiAdapter
from ...infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from ...configs.conf import *
from ...configs.dynamodb import dynamodb
from ...configs.region_hosts import get_payment_region_host
import logging as log

log.basicConfig(filemode='w', level=log.INFO)

_payment_service = PaymentService(
    ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb)
)
_payment_plan_service = PaymentPlanService(
    ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb)
)

router = APIRouter(
    prefix='/payment',
    tags=['Payment'],
    responses={404: {'description': 'Not found'}},
)


def get_payment_host(current_region: str = Header(...)):
    return get_payment_region_host(current_region)


@router.get('/plans', responses=idempotent_response('plans', List[stripe_vos.StripePlanVO]))
def list_plans(payment_host=Depends(get_payment_host)):
    data = _payment_plan_service.list_plans(payment_host)
    return res_success(data=data)


@router.put('/strong-customer-authentication')
def strong_customer_authentication(
    body: dtos.UserDTO = Body(...),
    payment_host=Depends(get_payment_host),
    verify=Depends(verify_token_by_payment_operation),
):
    data = _payment_service.strong_customer_authentication(
        payment_host, body)
    return res_success(data=data)


@router.put('/payment-method', responses=idempotent_response(f'payment_method', vo.PaymentStatusVO))
def payment_method(
    body: stripe_dtos.StripeUserPaymentRequestDTO = Body(...),
    payment_host=Depends(get_payment_host),
    verify=Depends(verify_token_by_payment_operation),
):
    data = _payment_service.payment_method(payment_host, body)
    return res_success(data=data)


@router.get('/subscribe', responses=idempotent_response('subscribe_status', vo.PaymentStatusVO))
def subscribe_status(
    role_id: int = Query(...),
    payment_host=Depends(get_payment_host),
    verify=Depends(verify_token_by_subscribe_status),
):
    data = _payment_service.get_payment_status(payment_host, role_id)
    return res_success(data=data)


@router.post('/subscribe', status_code=202)
async def subscribe(
    bg_tasks: BackgroundTasks,
    body: stripe_dtos.StripeSubscribeRequestDTO = Body(...),
    payment_host=Depends(get_payment_host),
    verify=Depends(verify_token_by_payment_operation),
):
    _payment_service.subscribe(bg_tasks, payment_host, body)
    return res_success(msg='processing', code='20200')


@router.post('/unsubscribe', status_code=202)
async def unsubscribe(
    bg_tasks: BackgroundTasks,
    body: dtos.UnsubscribeRequestDTO = Body(...),
    payment_host=Depends(get_payment_host),
    verify=Depends(verify_token_by_payment_operation),
):
    _payment_service.unsubscribe(bg_tasks, payment_host, body)
    return res_success(msg='canceling', code='20200')

'''
TODO: deprecated
'''
# @router.post('/webhook', status_code=201)
async def webhook(
    req: Request,
    payment_host=Depends(get_payment_host)
):
    return await _payment_service.webhook(payment_host, req)
