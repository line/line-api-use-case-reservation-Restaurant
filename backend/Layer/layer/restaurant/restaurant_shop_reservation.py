"""
RestaurantShopReservation操作用モジュール

"""
import os
from datetime import datetime
from dateutil.tz import gettz

from aws.dynamodb.base import DynamoDB
from common import utils


class RestaurantShopReservation(DynamoDB):
    """RestaurantShopReservation操作用クラス"""
    __slots__ = ['_table']

    def __init__(self):
        """初期化メソッド"""
        table_name = os.environ.get("SHOP_RESERVATION_TABLE")
        super().__init__(table_name)
        self._table = self._db.Table(table_name)

    def put_item(self, shop_id, reserved_day, reserved_year_month,
                 reserved_info, total_reserved_number, vacancy_flg):
        """
        データ登録

        Parameters
        ----------
        shop_id : int
            店舗ID
        reserved_day : str
            予約日
        reserved_year_month : str
            予約年月
        reserved_info : list
            30分毎の人数、時間等の予約情報
        total_reserved_number : int
            指定日の合計予約人数
        vacancy_flg : int
            空き状況フラグ -> 0:空き無し, 1:空きあり, 2:空き少し

        Returns
        -------
        response : dict
            レスポンス情報

        """
        item = {
            'shopId': shop_id,
            'reservedDay': reserved_day,
            'reservedYearMonth': reserved_year_month,
            'reservedInfo': reserved_info,
            'totalReservedNumber': total_reserved_number,
            'vacancyFlg': vacancy_flg,
            "expirationDate": utils.get_ttl_time(datetime.strptime(reserved_day, '%Y-%m-%d')),
            'createdTime': datetime.now(
                gettz('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"),
            'updatedTime': datetime.now(
                gettz('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"),
        }

        try:
            response = self._put_item(item)
        except Exception as e:
            raise e
        return response

    def update_item(self, shop_id, reserved_day, reserved_info,
                    total_reserved_number, vacancy_flg):
        """
        データ更新

        Parameters
        ----------
        shop_id : int
            店舗ID
        reserved_day : str
            予約日
        reserved_info : list
            30分毎の人数、時間等の予約情報
        total_reserved_number : int
            指定日の合計予約人数
        vacancy_flg : int
            空き状況フラグ -> 0:空き無し, 1:空きあり, 2:空き少し

        Returns
        -------
        response : dict
            レスポンス情報

        """
        key = {'shopId': shop_id, 'reservedDay': reserved_day}
        expression = ('set reservedInfo=:reserved_info, '
                      'totalReservedNumber=:total_reserved_number, '
                      'vacancyFlg=:vacancy_flg, '
                      'updatedTime=:updated_time')
        expression_value = {
            ':reserved_info': reserved_info,
            ':total_reserved_number': total_reserved_number,
            ':vacancy_flg': vacancy_flg,
            ':updated_time': datetime.now(
                gettz('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S")
        }
        return_value = "UPDATED_NEW"

        try:
            response = self._update_item(key, expression,
                                         expression_value, return_value)
        except Exception as e:
            raise e
        return response

    def get_item(self, shop_id, reserved_day):
        """
        データ取得

        Parameters
        ----------
        shop_id : int
            店舗ID
        reserved_day : str
            予約日

        Returns
        -------
        item : dict
            特定日の予約情報

        """
        key = {'shopId': shop_id, 'reservedDay': reserved_day}

        try:
            item = self._get_item(key)
        except Exception as e:
            raise e
        return item

    def query_index_shop_id_reserved_year_month(self, shop_id, reserved_year_month):  # noqa: E501
        """
        queryメソッドを使用してshopId-reservedYearMonth-indexのインデックスからデータ取得

        Parameters
        ----------
        shop_id : int
            店舗ID
        reserved_year_month : str
            予約年月

        Returns
        -------
        items : list
            特定年月の予約情報のリスト

        """
        index = 'shopId-reservedYearMonth-index'
        expression = 'shopId = :shop_id AND reservedYearMonth = :reserved_year_month'  # noqa: E501
        expression_value = {
            ':shop_id': shop_id,
            ':reserved_year_month': reserved_year_month
        }

        try:
            items = self._query_index(index, expression, expression_value)
        except Exception as e:
            raise e
        return items
