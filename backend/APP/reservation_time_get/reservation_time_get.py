import logging
import json
import os
from common import (common_const, utils)
from validation.restaurant_param_check import RestaurantParamCheck
from restaurant.restaurant_shop_reservation import RestaurantShopReservation

# ログ出力の設定
LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL")
logger = logging.getLogger()
if LOGGER_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# テーブル操作クラスの初期化
shop_reservation_table_controller = RestaurantShopReservation()


def get_reservation_time(shop_id, preferred_day):
    """
    予約済み時間の情報を取得する

    Parameters
    ----------
    shop_id : str
        予約する店舗のID
    preferred_day : str
        予約する日付

    Returns
    -------
    day_reserved_info_list: list of dict
        指定日の時間毎の予約情報

    Notes
    -------
    指定日に予約がない場合、空のリストを返す
    """
    # 指定日の予約情報を取得
    key = {'shop_id': int(shop_id), 'reserved_day': preferred_day}
    day_reserved_info = shop_reservation_table_controller.get_item(**key)

    # 指定日の予約がない場合空のリストを返す
    if not day_reserved_info:
        return []

    return day_reserved_info['reservedInfo']


def lambda_handler(event, context):
    """
    DynamoDBテーブルから日ごとの予約情報一覧を取得して返却する

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
    if error_msg := param_checker.check_api_reservation_time():
        error_msg_disp = ('\n').join(error_msg)
        logger.error(error_msg_disp)
        return utils.create_error_response(error_msg_disp, status=400)  # noqa: E501

    try:
        day_reserved_list = get_reservation_time(
            req_param['shopId'], req_param['preferredDay'])
    except Exception as e:
        logger.exception('Occur Exception: %s', e)
        return utils.create_error_response('ERROR')

    return utils.create_success_response(json.dumps(
        day_reserved_list, default=utils.decimal_to_int,
        ensure_ascii=False))
