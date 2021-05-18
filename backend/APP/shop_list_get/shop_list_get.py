import logging
import json
import os

from common import utils
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


def get_shop_list():
    """
    店舗一覧情報を返却する

    Returns
    -------
    area_shop_list: list of dict
        地域毎の店舗情報のリスト
    """

    shop_list = shop_master_table_controller.scan()

    # フロントに返却する形式にデータ加工
    area_shop_dict = {}
    for shop in shop_list:
        areaId = shop['areaId']
        # エリアIDをKeyとして、エリアとショップの情報を紐づけたdictを作成する
        if areaId in area_shop_dict:
            area_shop_dict[areaId]['shop'].append(shop['shop'])
        else:
            area_shop_dict[areaId] = create_area_shop_info(
                areaId, shop['areaName'], shop['shop'])

    # 検索用KeyのエリアIDを外し、返却する
    return list(area_shop_dict.values())


def create_area_shop_info(areaId, areaName, shop):
    """
    地域毎の店舗情報を作成する

    Parameters
    ----------
    areaId : int
        エリアID
    areaName : str
        地域名（関東・近畿等）
    shop : dict
        店舗情報

    Returns
    -------
    area_shop_dict: dict
        エリア-ショップ形式のデータ
    """
    return {
        'areaId': areaId,
        'areaName': areaName,
        'shop': [shop]
    }


def lambda_handler(event, context):
    """
    DynamoDBテーブルから全店舗一覧を取得して返却する。

    Parameters
    ----------
    event : dict
        フロントから送られたパラメータ等の情報
    context : __main__.LambdaContext
        Lambdaランタイムや関数名等のメタ情報

    Returns
    -------
    response: dict
        正常の場合、店舗情報一覧を返却する。
        エラーの場合、エラーコードとエラーメッセージを返却する。
    """
    # パラメータログ
    logger.info(event)
    try:
        shop_list = get_shop_list()
    except Exception as e:
        logger.exception('Occur Exception: %s', e)
        return utils.create_error_response('ERROR')

    return utils.create_success_response(json.dumps(
        shop_list, default=utils.decimal_to_int,
        ensure_ascii=False))
