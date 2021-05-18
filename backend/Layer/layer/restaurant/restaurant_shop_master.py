"""
RestaurantShopMaster操作用モジュール

"""
import os
from aws.dynamodb.base import DynamoDB


class RestaurantShopMaster(DynamoDB):
    """RestaurantShopMaster操作用クラス"""
    __slots__ = ['_table']

    def __init__(self):
        """初期化メソッド"""
        table_name = os.environ.get("SHOP_INFO_TABLE")
        super().__init__(table_name)
        self._table = self._db.Table(table_name)

    def get_item(self, shop_id):
        """
        データ取得

        Parameters
        ----------
        shop_id : int
            店舗ID

        Returns
        -------
        item : dict
            店舗情報

        """
        key = {'shopId': shop_id}

        try:
            item = self._get_item(key)
        except Exception as e:
            raise e
        return item

    def scan(self, shop_id=None):
        """
        scanメソッドを使用してデータ取得

        Parameters
        ----------
        shop_id : int, optional
            店舗ID, by default ''

        Returns
        -------
        items : list
            店舗情報のリスト

        """
        key = 'shop_id'

        try:
            items = self._scan(key, shop_id)
        except Exception as e:
            raise e
        return items
