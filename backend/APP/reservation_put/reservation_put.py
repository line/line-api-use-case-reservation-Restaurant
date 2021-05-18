import logging
import json
import os
import datetime

import flex_message_builder
from common import (common_const, line, utils)
from validation.restaurant_param_check import RestaurantParamCheck
# DynamoDB操作クラスのインポート
from common.channel_access_token import ChannelAccessToken
from common.remind_message import RemindMessage
from restaurant.restaurant_reservation_info import RestaurantReservationInfo
from restaurant.restaurant_shop_reservation import RestaurantShopReservation
from restaurant.restaurant_shop_master import RestaurantShopMaster


# 環境変数
REMIND_DATE_DIFFERENCE = int(os.getenv('REMIND_DATE_DIFFERENCE'))
CHANNEL_ID = os.getenv('OA_CHANNEL_ID')
LIFF_CHANNEL_ID = os.getenv('LIFF_CHANNEL_ID')

# ログ出力の設定
LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL")
logger = logging.getLogger()
if LOGGER_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# 定数の宣言
THIRTY_MINUTES = datetime.timedelta(minutes=30)
ONE_WEEK = datetime.timedelta(days=7)
JST_UTC_TIMEDELTA = datetime.timedelta(hours=9)
VACANCY_FLG_MAP = {'AVAILABLE_NOTHING': 0,
                   'AVAILABLE_MUCH': 1, 'AVAILABLE_FEW': 2}
RESERVED_PROPORTION_MAP = {'RESERVED_MUCH': 0.8, 'RESERVED_FULL': 1}
ON_DAY_REMIND_DATE_DIFFERENCE = 0

# テーブル操作クラスの初期化
shop_master_table_controller = RestaurantShopMaster()
reservation_info_table_controller = RestaurantReservationInfo()
shop_reservation_table_controller = RestaurantShopReservation()
channel_access_token_table_controller = ChannelAccessToken()
message_table_controller = RemindMessage()


def put_customer_reservation_info(body, shop_info):
    """
    顧客予約情報テーブルに予約情報の登録を行う。

    Parameters
    ----------
    body : dict
        ユーザーが選択した予約情報
    shop_info: dict
        予約する店舗の情報

    Returns
    -------
    reservation_id: str
        予約情報を一意に判別するID
    """

    customer_reservation_item = {
        "shop_id": body['shopId'],
        "shop_name": body['shopName'],
        "user_id": body['userId'],
        "user_name": body['userName'],
        "course_id": body['courseId'],
        "course_name": body['courseName'],
        "reservation_people_number": body['reservationPeopleNumber'],
        "reservation_date": body['reservationDate'],
        "reservation_starttime": body['reservationStarttime'],
        "reservation_endtime": body['reservationEndtime'],
        "amount": get_course_price(shop_info, body['courseId']),
    }
    reservation_id = reservation_info_table_controller.put_item(
        **customer_reservation_item)
    return reservation_id


def get_course_price(shop_info, course_id):
    """
    店舗情報のテーブルから、コースの値段を取得する。

    Parameters
    ----------
    shop_info: dict
        shop_idを指定した取得した店舗の情報
    course_id : int
        予約するコースのID

    Returns
    -------
    course_price: int
        コースの値段
    """
    course_price = [course_list['price']
                    for course_list in shop_info['course']
                    if course_list['courseId'] == course_id]

    if not course_price:
        return 0
    return course_price[0]


def put_shop_reservation_info(body, shop_info):
    """
    カレンダーに予約情報を登録する。
    既に指定した月日に予約情報がある場合、Updateを行い、
    予約情報がない場合、Insertを行う。

    Parameters
    ----------
    body : dict
        ユーザーが選択した予約情報
    shop_info: dict
        shop_idを指定した取得した店舗の情報
    """
    # shopIdと予約日でそのデータがあるか検索する
    reservation_item = shop_reservation_table_controller.get_item(
        body['shopId'], body['reservationDate'])

    new_reservation_list, new_total_reserved_number = divide_thirty_minutes(
        body['reservationStarttime'], body['reservationEndtime'],
        body['reservationPeopleNumber']
    )

    # 店舗の1日の予約可能人数を算出する 計算:席数*営業時間の30分区切り
    openTime = datetime.datetime.strptime(
        shop_info['shop']['openTime'], "%H:%M")
    closeTime = datetime.datetime.strptime(
        shop_info['shop']['closeTime'], "%H:%M")
    restaurant_open_term = int((closeTime - openTime) / THIRTY_MINUTES)
    max_reservable_number = int(
        shop_info['shop']['seatsNumber']) * restaurant_open_term

    # if->指定した予約日に予約情報がある場合：更新
    # else->指定した予約日に予約情報がない場合：新規作成
    if reservation_item:
        # 新規データと元データを統合するため、重複している時間の検索用に
        # 予約開始時刻をkeyとして予約情報をvalueに持ったデータを作成する。
        start_time_index = {}
        for reserved_time_info in reservation_item['reservedInfo']:
            start_time_index[reserved_time_info['reservedStartTime']
                             ] = reserved_time_info

        # if->予約がある時間帯：予約人数を足す
        # else->予約が無い時間帯：その時間を新たに追加する
        for new_reservation_info in new_reservation_list:
            reservation_start_time = new_reservation_info['reservedStartTime']
            if reservation_start_time in start_time_index:
                start_time_index[reservation_start_time]['reservedNumber'] +=\
                    new_reservation_info['reservedNumber']
            else:
                start_time_index[reservation_start_time] = new_reservation_info

        # 一日の予約合計数と席数に対する予約合計数の比率を算出する(カレンダーの空き状況出力時に使用)
        sum_total_reserved_number = reservation_item['totalReservedNumber'] + \
            new_total_reserved_number
        reserved_proportion = sum_total_reserved_number / max_reservable_number

        key = {
            'shop_id': body['shopId'],
            'reserved_day': body['reservationDate']
        }
        update_value = {
            'reserved_info': list(start_time_index.values()),
            'total_reserved_number': sum_total_reserved_number,
            'vacancy_flg': get_vacancy_flg(reserved_proportion)
        }
        shop_reservation_table_controller.update_item(**key, **update_value)
    else:
        # 席数に対する予約合計数の比率を算出する(カレンダーの空き状況出力時に使用)
        reserved_proportion = new_total_reserved_number / max_reservable_number
        new_reservation_item = {
            'shop_id': body['shopId'],
            'reserved_day': body['reservationDate'],
            'reserved_year_month': utils.format_date(body['reservationDate'],
                                                     '%Y-%m-%d', '%Y-%m'),
            'reserved_info': new_reservation_list,
            'total_reserved_number': new_total_reserved_number,
            'vacancy_flg': get_vacancy_flg(reserved_proportion),
        }
        shop_reservation_table_controller.put_item(**new_reservation_item)


def divide_thirty_minutes(reservation_start_time, reservation_end_time,
                          reservation_people_number):
    """
    数時間単位の予約情報を、30分単位の予約情報に分割し、listで返却する。
    データ:予約開始時間,予約終了時間,予約人数

    Parameters
    ----------
    reservation_start_time : str
        予約の希望開始時間
    reservation_end_time : str
        予約の希望終了時間
    reservation_people_number : int
        予約人数

    Returns
    -------
    reservation_info_list: list
        30分単位に分割された予約情報。
        すべての時間帯で、予約人数は同じになる。
    total_people_number: int
        30分ごとの予約人数の合計
    """

    start_time = datetime.datetime.strptime(
        reservation_start_time, "%H:%M")
    end_time = datetime.datetime.strptime(
        reservation_end_time, "%H:%M")
    thirty_minutes = datetime.timedelta(minutes=30)

    # 時間のデータを30分毎の時間に分割してリストを作成する。
    reservation_info_list = []
    tmp_start_time = start_time
    tmp_end_time = start_time + thirty_minutes
    total_people_number = 0
    while tmp_end_time <= end_time:
        reservation_info = {
            'reservedStartTime': tmp_start_time.strftime('%H:%M'),
            'reservedEndTime': tmp_end_time.strftime('%H:%M'),
            'reservedNumber': reservation_people_number
        }
        reservation_info_list.append(reservation_info)

        total_people_number += reservation_people_number
        tmp_start_time += thirty_minutes
        tmp_end_time += thirty_minutes

    return reservation_info_list, total_people_number


def get_vacancy_flg(reserved_proportion):
    """
    予約割合から判断し、空き状況のフラグを取得する。

    Parameters
    ----------
    reserved_proportion : float
        予約数/席数で計算した予約済み率

    Returns
    -------
    vacancy_flg: int
        空き状況フラグ
    """
    if(reserved_proportion < RESERVED_PROPORTION_MAP['RESERVED_MUCH']):
        vacancy_flg = VACANCY_FLG_MAP['AVAILABLE_MUCH']
    elif(reserved_proportion >= RESERVED_PROPORTION_MAP['RESERVED_MUCH'] and
         reserved_proportion < RESERVED_PROPORTION_MAP['RESERVED_FULL']):
        vacancy_flg = VACANCY_FLG_MAP['AVAILABLE_FEW']
    else:
        vacancy_flg = VACANCY_FLG_MAP['AVAILABLE_NOTHING']
    return vacancy_flg


def create_flex_message(body, remind_date_difference):
    """
    LINEメッセージで送信するフレックスメッセージを作成する

    Parameters
    ----------
    body : dict
        メッセージ送信にuser_id等の必要なデータ
    remind_date_difference : int
        リマインドを送信する日付と当日の差分

    Returns
    -------
    flex_message : str
        フレックスメッセージの形式に整形したjson型データ
    """
    reservation_datetime = body['reservationDate'] + ' ' + \
        body['reservationStarttime'] + '-' + body['reservationEndtime']

    flex_prm = {'shop_name': body['shopName'],
                'reservation_date': reservation_datetime,
                'course_name': body['courseName'],
                'number_of_people': str(body['reservationPeopleNumber']),
                'remind_date_difference': remind_date_difference
                }
    flex_message = flex_message_builder.create_restaurant_remind(**flex_prm)

    return flex_message


def get_channel_access_token(channel_id):
    """
    短期チャネルアクセストークンをチャネル情報のテーブルから取得する

    Parameters
    ----------
    channel_id : str
        LINE公式アカウントもしくはMINIアプリのチャネルID
        LINE Developersコンソールにて確認可能

    Returns
    -------
    channelAccessToken : str
        access_token:短期のチャネルアクセストークン
    """
    item = channel_access_token_table_controller.get_item(channel_id)
    return item['channelAccessToken']


def put_push_messages_to_dynamo(body, remind_date_difference):
    """
    プッシュメッセージのメッセージ情報を作成し、DynamoDBに登録する。
    DynamoDBへの登録処理自体は共通処理にて行っている。

    Parameters
    ----------
    body : dict
        フロントから渡ってきたパラメータ
    remind_date_difference : int
        当日以前のリマインド行う日付の差分
        予約日以降のメッセージ送信を考慮し、マイナス値を許可（ex:3日前→-3）
    """
    remind_date_on_day = body['reservationDate']

    # 当日のリマインドメッセージを登録
    flex_message_on_day = create_flex_message(body, ON_DAY_REMIND_DATE_DIFFERENCE)  # noqa:E501
    message_table_controller.put_push_message(
        body['userId'], CHANNEL_ID, flex_message_on_day,
        remind_date_on_day)

    # 指定日のリマインドメッセージを登録
    flex_message_day_before = create_flex_message(body, remind_date_difference)  # noqa:E501
    remind_date_day_before = utils.calculate_date_str_difference(
        remind_date_on_day, remind_date_difference)
    message_table_controller.put_push_message(
        body['userId'], CHANNEL_ID, flex_message_day_before,
        remind_date_day_before)


def lambda_handler(event, context):
    """
    予約情報のデータ登録とLINEメッセージの送信を行う。

    Parameters
    ----------
    event : dict
        フロントから送られたパラメータ等の情報
    context : __main__.LambdaContext
        Lambdaランタイムや関数名等のメタ情報

    Returns
    -------
    response: dict
        正常の場合、予約IDを返却する。
        エラーの場合、エラーコードとエラーメッセージを返却する。
    """
    # パラメータログ
    logger.info(event)

    if event['body'] is None:
        error_msg_disp = common_const.const.MSG_ERROR_NOPARAM
        return utils.create_error_response(error_msg_disp, 400)
    body = json.loads(event['body'])
    #ユーザーID取得
    try:
        user_profile = line.get_profile(
            body['idToken'], LIFF_CHANNEL_ID)
        if 'error' in user_profile and 'expired' in user_profile['error_description']:  # noqa 501
            return utils.create_error_response('Forbidden', 403)
        else:
            body['userId'] = user_profile['sub']
    except Exception:
        logger.exception('不正なIDトークンが使用されています')
        return utils.create_error_response('Error')

    # パラメータチェック
    param_checker = RestaurantParamCheck(body)
    if error_msg := param_checker.check_api_reservation_put():
        error_msg_disp = ('\n').join(error_msg)
        logger.error(error_msg_disp)
        return utils.create_error_response(error_msg_disp, 400)

    try:
        # 予約情報のデータ登録
        shop_info = shop_master_table_controller.get_item(body['shopId'])
        put_shop_reservation_info(body, shop_info)
        reservation_id = put_customer_reservation_info(body, shop_info)

        # pushメッセージをDynamoに保存
        put_push_messages_to_dynamo(body, REMIND_DATE_DIFFERENCE)

    except Exception as e:
        logger.error('Occur Exception: %s', e)
        return utils.create_error_response('ERROR')

    return utils.create_success_response(
        json.dumps({'reservationId': reservation_id}))
