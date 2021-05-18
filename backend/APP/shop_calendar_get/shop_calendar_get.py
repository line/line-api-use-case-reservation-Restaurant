import logging
import json
import datetime
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


def get_shop_calendar(shop_id, preferred_year_month):
    """
    店舗の予約情報カレンダーを取得する。


    Parameters
    ----------
    shop_id : str
        店舗ID
    preferred_year_month : str
        カレンダーで選択した年月
        YYYY-MM の形式

    Returns
    -------
    result_calendar: dict
        予約情報が存在する日の空き状況

    """
    shop_calendar = shop_reservation_table_controller.query_index_shop_id_reserved_year_month(  # noqa:E501
        int(shop_id), preferred_year_month
    )

    result_calendar = {
        'reservedYearMonth': preferred_year_month, 'reservedDays': []
    }

    if not shop_calendar:
        return result_calendar

    for one_day_info in shop_calendar:
        # 日付を数値のみの形式に加工
        reservedDay = datetime.datetime.strptime(
            one_day_info['reservedDay'], '%Y-%m-%d').day
        # フロントに返却する名称に変更
        result_calendar['reservedDays'].append(
            {'day': reservedDay, 'vacancyFlg': one_day_info['vacancyFlg']})

    return result_calendar


def lambda_handler(event, context):
    """
    DynamoDBテーブルから指定年月の予約情報を取得して返却する。

    Parameters
    ----------
    event : dict
        フロントから送られたパラメータ等の情報
    context : __main__.LambdaContext
        Lambdaランタイムや関数名等のメタ情報

    Returns
    -------
    response: dict
        正常の場合、指定年月の予約情報を返却する。
        エラーの場合、エラーコードとエラーメッセージを返却する。
    """
    # パラメータログ
    logger.info(event)

    # パラメータを取得
    req_param = event['queryStringParameters']
    if req_param is None:
        error_msg_disp = common_const.const.MSG_ERROR_NOPARAM
        return utils.create_error_response(error_msg_disp, 400)
    # パラメータのバリデーションチェック
    param_checker = RestaurantParamCheck(req_param)
    if error_msg := param_checker.check_api_shop_calendar():
        error_msg_disp = ('\n').join(error_msg)
        logger.error(error_msg_disp)
        return utils.create_error_response(error_msg_disp, status=400)  # noqa: E501

    try:
        shop_reserved_calendar = get_shop_calendar(
            req_param['shopId'], req_param['preferredYearMonth'])

    except Exception as e:
        logger.exception('Occur Exception: %s', e)
        return utils.create_error_response('ERROR')
    return utils.create_success_response(json.dumps(
        shop_reserved_calendar, default=utils.decimal_to_int,
        ensure_ascii=False))
