import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_restaurant_remind(**kwargs):
    """
    Messaging APIに渡すリマインド通知用メッセージの取得

    Parameters
    ----------
    shop_name
        店名
    reservation_date
        予約日
    course_name
        コース名
    remind_status
        リマインドの種類（前日/当日）
    number_of_people
        予約人数
    Returns
    -------
    result : dict
        Flexmessageの元になる辞書型データ
    """
    logger.info(kwargs)
    shop_name = kwargs['shop_name']
    reservation_date = kwargs['reservation_date']
    course_name = kwargs['course_name']
    number_of_people = kwargs['number_of_people']
    remind_date_difference = kwargs['remind_date_difference']

    # 予約日当日とそれ以外のメッセージで文言を変える
    if remind_date_difference < 0:
        remind_header_msg = 'ご予約日の' + \
            str(abs(remind_date_difference)) + '日前となりました'
        remind_last_msg = "当日は、お会いできることを心よりお待ちしています。\n\n※このメッセージは、Use Case 予約（レストラン）デモアプリが送信したリマインド通知です。"  # noqa: E501
    else:
        remind_header_msg = 'ご予約日の当日となりました'
        remind_last_msg = "本日は、お会いできることを心よりお待ちしています。\nどうぞお気をつけてお越しください。\n\n※このメッセージは、Use Case 予約（レストラン）デモアプリが送信したリマインド通知です。"  # noqa: E501

    flex_msg = {
        "type": "flex",
        "altText": remind_header_msg,
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "flex": 0,
                "contents": [
                    {
                        "type": "text",
                        "text": "リマインド通知",
                        "size": "sm",
                        "weight": "bold",
                        "color": "#36DB34"
                    },
                    {
                        "type": "text",
                        "text": remind_header_msg,
                        "size": "lg",
                        "weight": "bold"
                    }
                ]
            },
            "hero": {
                "type": "image",
                "url": "https://media.istockphoto.com/photos/modern-room-with-tables-and-chairs-picture-id639067562",  # noqa: E501
                "size": "full",
                "aspectRatio": "2:1",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "label": "Action",
                    "uri": "https://line.me/ja/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "margin": "xs",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "店舗名:",
                                        "flex": 1,
                                        "size": "sm",
                                        "align": "start",
                                        "color": "#5B5B5B"
                                    },
                                    {
                                        "type": "text",
                                        "text": shop_name,
                                        "flex": 2,
                                        "size": "sm",
                                        "align": "start",
                                        "color": "#666666",
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "日時:",
                                        "flex": 1,
                                        "size": "sm",
                                        "color": "#5B5B5B"
                                    },
                                    {
                                        "type": "text",
                                        "text": reservation_date,
                                        "flex": 2,
                                        "size": "sm",
                                        "align": "start",
                                        "color": "#666666",
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "コース:",
                                        "flex": 1,
                                        "size": "sm",
                                        "color": "#5B5B5B"
                                    },
                                    {
                                        "type": "text",
                                        "text": course_name,
                                        "flex": 2,
                                        "size": "sm",
                                        "align": "start",
                                        "color": "#666666",
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "人数:",
                                        "flex": 1,
                                        "size": "sm",
                                        "color": "#5B5B5B"
                                    },
                                    {
                                        "type": "text",
                                        "text": number_of_people,
                                        "flex": 2,
                                        "size": "sm",
                                        "align": "start",
                                        "color": "#666666",
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "lg",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": remind_last_msg,
                                        "size": "sm",
                                        "color": "#4A4141",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }

    return flex_msg
