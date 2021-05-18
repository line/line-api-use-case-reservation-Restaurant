import logging
import json
import os

from common import (common_const, utils)
from validation.restaurant_param_check import RestaurantParamCheck
from restaurant.restaurant_shop_master import RestaurantShopMaster

# ログ出力の設定
LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL")
logger = logging.getLogger()
if LOGGER_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# テーブル操作クラスの初期化
shop_master_table_controller = RestaurantShopMaster()


def get_course_list(shop_id):
    """
    該当店舗のコース一覧情報を返却する

    Parameters
    ----------
    shop_id : str
        コースを取得する店舗のID

    Returns
    -------
    course_list : list of dict
        値段、コース名などのコース情報
    """
    course_list = shop_master_table_controller.get_item(int(shop_id))['course']
    return course_list


def lambda_handler(event, context):
    """
    DynamoDBテーブルからコース情報一覧を取得して返却する。

    Parameters
    ----------
    event : dict
        フロントから送られたパラメータ等の情報
    context : __main__.LambdaContext
        Lambdaランタイムや関数名等のメタ情報

    Returns
    -------
    response: dict
        正常の場合、予約情報を返却する。
        エラーの場合、エラーコードとエラーメッセージを返却する。
    """
    logger.info(event)
    req_param = event['queryStringParameters']

    if req_param is None:
        error_msg_disp = common_const.const.MSG_ERROR_NOPARAM
        return utils.create_error_response(error_msg_disp, 400)
    # パラメータのバリデーションチェック
    param_checker = RestaurantParamCheck(req_param)
    if error_msg := param_checker.check_api_course_list():
        error_msg_disp = ('\n').join(error_msg)
        logger.error(error_msg_disp)
        return utils.create_error_response(error_msg_disp, status=400)  # noqa: E501

    try:
        course_list = get_course_list(req_param['shopId'])
    except Exception as e:
        logger.exception('Occur Exception: %s', e)
        return utils.create_error_response('ERROR')

    return utils.create_success_response(json.dumps(
        course_list, default=utils.decimal_to_int,
        ensure_ascii=False))
