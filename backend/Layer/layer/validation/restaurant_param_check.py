from validation.param_check import ParamCheck


class RestaurantParamCheck(ParamCheck):
    def __init__(self, params):
        self.shop_id = params['shopId'] if 'shopId' in params else None
        self.preferred_year_month = params['preferredYearMonth'] if 'preferredYearMonth' in params else None  # noqa:E501
        self.preferred_day = params['preferredDay'] if 'preferredDay' in params else None  # noqa:E501
        self.access_token = params['accessToken'] if 'accessToken' in params else None  # noqa: E501
        self.course_id = params['courseId'] if 'courseId' in params else None
        self.reservation_date = params['reservationDate'] if 'reservationDate' in params else None  # noqa:E501
        self.reservation_starttime = params['reservationStarttime'] if 'reservationStarttime' in params else None  # noqa:E501
        self.reservation_endtime = params['reservationEndtime'] if 'reservationEndtime' in params else None  # noqa:E501
        self.reservation_people_number = params['reservationPeopleNumber'] if 'reservationPeopleNumber' in params else None  # noqa:E501
        self.course_name = params['courseName'] if 'courseName' in params else None  # noqa: E501
        self.shop_name = params['shopName'] if 'shopName' in params else None
        self.user_name = params['userName'] if 'userName' in params else None

        self.error_msg = []

    def check_api_shop_calendar(self):
        self.check_shop_id()
        self.check_preferred_year_month()

        return self.error_msg

    def check_api_reservation_time(self):
        self.check_shop_id()
        self.check_preferred_day()

        return self.error_msg

    def check_api_course_list(self):
        self.check_shop_id()

        return self.error_msg

    def check_api_reservation_put(self):
        self.check_access_token()
        self.check_course_id()
        self.check_reservation_date()
        self.check_reservation_starttime()
        self.check_reservation_endtime()
        self.check_reservation_people_number()
        self.check_shop_name()
        self.check_course_name()
        self.check_user_name()

        return self.error_msg

    def check_shop_id(self):
        if error := self.check_required(self.shop_id, 'shopId'):
            self.error_msg.append(error)
            return

        if error := self.check_int(self.shop_id, 'shopId'):
            self.error_msg.append(error)

    def check_preferred_year_month(self):
        if error := self.check_required(self.preferred_year_month,
                                        'preferredYearMonth'):
            self.error_msg.append(error)
            return

        if error := self.check_year_month(self.preferred_year_month,
                                          'preferredYearMonth'):
            self.error_msg.append(error)

    def check_preferred_day(self):
        if error := self.check_required(self.preferred_day, 'preferredDay'):
            self.error_msg.append(error)
            return

        if error := self.check_year_month_day(self.preferred_day,
                                              'preferredDay'):
            self.error_msg.append(error)

    def check_access_token(self):
        if error := self.check_required(self.access_token, 'accessToken'):
            self.error_msg.append(error)
            return

        if error := self.check_length(self.access_token,
                                      'accessToken', 1, None):
            self.error_msg.append(error)

    def check_course_id(self):
        if error := self.check_required(self.course_id, 'courseId'):
            self.error_msg.append(error)
            return

        if error := self.check_int(self.course_id, 'courseId'):
            self.error_msg.append(error)

    def check_shop_name(self):
        if error := self.check_required(self.shop_name, 'shopName'):
            self.error_msg.append(error)
            return

        if error := self.check_length(self.shop_name, 'shopName', 1, None):
            self.error_msg.append(error)

    def check_course_name(self):
        if error := self.check_required(self.course_name, 'courseName'):
            self.error_msg.append(error)
            return

        if error := self.check_length(self.course_name, 'courseName', 1, None):
            self.error_msg.append(error)

    def check_user_name(self):
        if error := self.check_required(self.user_name, 'userName'):
            self.error_msg.append(error)
            return

        if error := self.check_length(self.user_name, 'userName', 1, None):
            self.error_msg.append(error)

    def check_reservation_date(self):
        if error := self.check_required(self.reservation_date, 'reservationDate'):  # noqa 501
            self.error_msg.append(error)
            return

        if error := self.check_year_month_day(self.reservation_date, 'reservationDate'):  # noqa 501
            self.error_msg.append(error)

    def check_reservation_starttime(self):
        if error := self.check_required(self.reservation_starttime, 'reservationStarttime'):  # noqa 501
            self.error_msg.append(error)
            return

        if error := self.check_time_format(self.reservation_starttime, 'reservationStarttime', '%H%M'):  # noqa 501
            self.error_msg.append(error)
            return

    def check_reservation_endtime(self):
        if error := self.check_required(self.reservation_endtime, 'reservationEndtime'):  # noqa 501
            self.error_msg.append(error)
            return

        if error := self.check_time_format(self.reservation_endtime, 'reservationEndtime', '%H%M'):  # noqa 501
            self.error_msg.append(error)
            return

    def check_reservation_people_number(self):
        if error := self.check_required(self.reservation_people_number, 'reservationPeopleNumber'):  # noqa 501
            self.error_msg.append(error)
            return

        if error := self.check_int(self.reservation_people_number,
                                   'reservationPeopleNumber'):
            self.error_msg.append(error)
