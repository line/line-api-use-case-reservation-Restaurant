/**
 * レストランアプリケーションプラグイン
 *
 * @param {Object} $axios
 * @param {Object} app
 * @param {Object} store
 * @param {Object} env
 * @return {VueRestaurant} 
 */
const VueRestaurant = ($axios, app, store, env) => {
    /** @type {string} 通信モジュール */
    const _module = env.AJAX_MODULE ? env.AJAX_MODULE : "axios";
    /** @type {string} APIGatewayステージ名 */
    const _stage = `/${env.APIGATEWAY_STAGE}`;
    /** @type {Object} ロケール */
    let _i18n = app.i18n.messages[store.state.locale];

    return {
        /**
         * エリア＆店舗情報取得
         *
         * @return {Object} エリア&店舗情報 
         */
        async getAreaShops() {
            let ret = { areas: [], restaurants: {} };
            // エリアレコード
            const arecord = ()=>{ return { code: null, name: null }; };
            // 店舗レコード
            const srecord = ()=>{
                return { 
                    id: null,
                    name: null,
                    img: null,
                    address: null,
                    start: null,
                    end: null,
                    holiday: null,
                    budget: null,
                    seats: null,
                    smoking: null,
                    tel: null,
                    line: null,
                    map: null,
                }; 
            };

            // エリア＆店舗データ取得
            const data = await this[_module].areaData();
            if (!data) { return ret };

            for (const record of data) {
                const areaId = record.areaId;
                const areaName = record.areaName;
                // エリア情報
                if (!(areaId in ret.restaurants)) {
                    let area = arecord();
                    area.code = areaId;
                    area.name = areaName;
                    ret.areas.push(area);
                    ret.restaurants[record.areaId] = [];
                }

                // 並び順変更
                record.shop.sort((previous, after)=>{
                    const val1 = previous.displayOrder;
                    const val2 = after.displayOrder;
                    if (val1 < val2) return -1;
                    if (val1 > val2) return 1;
                    return 0;
                });
                
                for (const shopRecord of record.shop) {
                    // 店舗情報
                    let shop = srecord();
                    shop.id = shopRecord.shopId;
                    shop.name = shopRecord.shopName;
                    shop.img = shopRecord.imageUrl;
                    shop.address = shopRecord.shopAddress;
                    shop.start = shopRecord.openTime;
                    shop.end = shopRecord.closeTime;
                    shop.holiday = app.$restaurant.utils.convertWeekdays(shopRecord.closeDay);
                    shop.tel = shopRecord.shopTel;
                    shop.line = shopRecord.lineAccountUrl;
                    shop.budget = shopRecord.averageBudget;
                    shop.seats = shopRecord.seatsNumber;
                    shop.smoking = shopRecord.smokingFlg==1 ? _i18n.restaurant.allowed : _i18n.restaurant.not_allowed;
                    shop.map = shopRecord.coordinate ? shopRecord.coordinate : null;
                    ret.restaurants[record.areaId].push(shop);
                }
            }

            return ret;
        },

        /**
         * コース情報取得
         *
         * @param {number} shopId 店舗ID
         * @return {Array<Object>} コース情報 
         */
        async getCourses(shopId) {
            let ret = [];

            // コースレコード
            const crecord = () => {
                return {
                    id: null,
                    name: null,
                    time: null,
                    price: null,
                    comment: null,
                    text: null,
                    value: null,                    
                }
            };

            // コースなし
            ret.push({
                id: 0,
                name: _i18n.restaurant.no_course,
                time: 0,
                price: 0,
                comment: null,
                text: _i18n.restaurant.no_course,
                value: 0
            });

            // コースデータ取得
            const data = await this[_module].courseData(shopId);
            if (!data) { return ret };

            for (const record of data) {
                let course = crecord();
                course.id = record.courseId;
                course.name = record.courseName;
                course.time = parseInt(record.courseMinutes, 10);
                course.price = parseInt(record.price, 10);
                course.comment= record.comment;
                course.text = `${course.name} (${_i18n.restaurant.yen.replace("{price}", course.price.toLocaleString())})`;
                course.value = course.id;
                ret.push(course);
            }

            return ret;
        },

        /**
         * 店舗月別予約状況取得
         *
         * @param {number} shopId 店舗ID
         * @param {number} month 対象月
         * @param {Object} restaurant レストラン店舗情報
         * @return {Object} 店舗月月予約状況 
         */
        async getMonthlyReservationStatus(shopId, month, restaurant) {
            let ret = {};

            // 月別予約状況データ取得
            const data = await this[_module].shopStatusCalendar(shopId, month);
            if (!data) { return ret };

            // 予約状況データ格納
            const yyyymm = new String(data.reservedYearMonth);
            const calendar = data.reservedDays;

            for (const dayRecord of calendar) {
                // 日別営業状態＆予約状況
                const dd = ("000"+dayRecord.day).slice(-2);
                const day = `${yyyymm}-${dd}`;
                const vacancyStatus = dayRecord.vacancyFlg;
                const workingStatus = app.$restaurant.utils.isHoliday(day, restaurant.holiday);

                let reservation = app.$restaurant.utils.createStatusRecord();
                reservation.status = workingStatus ? 0 : (vacancyStatus==0 ? 3 : vacancyStatus);
                reservation.name = "";
                reservation.start = restaurant.start;
                reservation.end = restaurant.end;
                ret[day] = reservation;
            }

            return ret;
        },

        /**
         *　店舗日別予約状況取得
         *
         * @param {number} shopId 店舗ID
         * @param {number} day 予約日
         * @param {Object} restaurant レストラン店舗情報
         * @return {Array<Object>} 店舗日別予約状況
         */
        async getDailyReservationStatus(shopId, day, restaurant) {
            let ret = [];

            // 日別別予約状況データ取得
            const data = await this[_module].shopDailyStatus(shopId, day);
            if (!data) { return ret };

            let events = [];
            for (const record of data) {
                if (!("status" in record)) {
                    record['status'] = 0;   // 空き有
                    const reservedNumber = record.reservedNumber;
                    const reservedLimit = restaurant.seats;
                    const percentage = reservedNumber / reservedLimit; 
                    if (percentage >= 1.0) {
                        record['status'] = 2;   // 空き無
                    } else if (percentage >= 0.8) {
                        record['status'] = 1;   // 空き少
                    }
                }
                // 空き状況
                let name = _i18n.restaurant.vacant;
                let color = "success";
                switch (record.status) {
                case 1:
                    name = _i18n.restaurant.vacant_little;
                    color = "orange lighten-1";
                    break;
                case 2:
                    name = _i18n.restaurant.full;
                    color = "error";
                    break;
                }
                // 予約
                let event = app.$restaurant.utils.createEventRecord();
                event.shopId = restaurant.id; 
                event.name = name;
                event.start = `${day} ${record.reservedStartTime}`;
                event.end = `${day} ${record.reservedEndTime}`;
                event.color = color;
                event.reserved = record.reservedNumber;
                events.push(event);
            }

            // 1日分時間帯イベント取得
            ret = app.$restaurant.utils.createEvents(day, restaurant);
            for (const event of events) {
                let targetEvent = ret.find((v) => v.start == event.start);
                if (targetEvent) {
                    // 予約状況イベント反映
                    targetEvent.shopId = event.shopId;
                    targetEvent.name = event.name;
                    targetEvent.start = event.start;
                    targetEvent.end = event.end;
                    targetEvent.color = event.color;
                    targetEvent.reserved = event.reserved;
                }
            }

            return ret;
        },

        /**
         * 予約登録
         *
         * @param {string} token アクセストークン
         * @param {number} shopId 店舗ID
         * @param {number} day 予約日
         * @param {string} start 予約開始時間
         * @param {string} end 予約終了時間
         * @param {number} courseId 予約コースID
         * @param {number} people 予約人数
         * @param {Object} names ユーザー、店舗、コース名称
         * @return {Object} 予約ID
         */
        async updateReserve(token, shopId, day, start, end, courseId, people, names) {
            // LIFF ID Token取得
            const idToken = store.state.lineUser.idToken;

            const params = {
                idToken: idToken,
                accessToken: token,
                shopId: shopId,
                shopName: names.shopName,
                reservationDate: day,
                reservationStarttime: start,
                reservationEndtime: end,
                reservationPeopleNumber: parseInt(people, 10),
                courseId: courseId,
                courseName: names.courseName,
                userName: names.userName,
            };

            // 予約登録
            const data = await this[_module].reserve(params);
            if (!data) { return null };

            // メッセージ
            let message = {
                reservationId: data.reservationId,
            };

            return message;
        },

        // ============================================
        //     ユーティリティ
        // ============================================
        utils: {
            /**
             *　年月リスト
             *
             * @param {number} count 月数
             * @return {Array<Object>} 年月リスト
             */
            monthList(count) {
                let months = [];
                let yyyymmdd = app.$utils.now("yyyymmdd");

                let yyyy = yyyymmdd.substr(0, 4);
                let mm = yyyymmdd.substr(4, 2).replace(/^0/, " ");
                if (_i18n.type == "en") { mm = app.$utils.englishMonth(mm); }
                months.push({ text: _i18n.restaurant.yyyymm.replace("{year}", yyyy).replace("{month}", mm), value: `${yyyymmdd.substr(0, 6)}` });

                for (let i=0; i<count; i++) {
                    yyyymmdd = app.$utils.now("yyyymmdd", i+1);
                    yyyy = yyyymmdd.substr(0, 4);
                    mm = yyyymmdd.substr(4, 2).replace(/^0/, " ");
                    if (_i18n.type == "en") { mm = app.$utils.englishMonth(mm); }
                    months.push({ text: _i18n.restaurant.yyyymm.replace("{year}", yyyy).replace("{month}", mm), value: `${yyyymmdd.substr(0, 6)}` });
                }
                
                return months;
            },

            /**
             *　時間帯リスト
             *
             * @param {string} fromTime 開始時間
             * @param {string} toTime 終了時間
             * @return {Array<Object>} 時間帯リスト 
             */
            timeList(fromTime, toTime) {
                let ret = [];
    
                let ftime = parseInt(fromTime.split(":")[0], 10);
                let ttime = parseInt(toTime.split(":")[0], 10);
    
                for (let tm=ftime; tm<=ttime; tm++) {
                    let time = ("00" + tm).slice(-2) + ":00";
                    let mtime = ("00" + tm).slice(-2) + ":30";
                    if (time >= fromTime) {
                        ret.push({ text: time, value: time });
                    }
                    if (mtime <= toTime) {
                        ret.push({ text: mtime, value: mtime });
                    }
                }
    
                return ret;
            },

            /**
             * 時間大小比較
             *
             * @param {string} from 開始時刻
             * @param {string} to 終了時刻
             * @return {boolean} 真偽値 
             */
            checkFromToTime(from, to) {
                let ret = false;

                if (from < to) {
                    ret = true;
                }

                return ret;
            },

            /**
             * 曜日値変換（レストラン仕様 --> Javascript仕様）
             *
             * @param {Array<number>} weekdays
             * @return {Array<number>} 変換済曜日配列 
             */
            convertWeekdays(weekdays) {
                let ret = [];

                for (let weekday of weekdays) {
                    switch (weekday) {
                    case 0: ret.push(-1); break;  // 休日なし
                    case 1: ret.push(1); break;  // 月
                    case 2: ret.push(2); break;  // 火
                    case 3: ret.push(3); break;  // 水
                    case 4: ret.push(4); break;  // 木
                    case 5: ret.push(5); break;  // 金
                    case 6: ret.push(6); break;  // 土
                    case 7: ret.push(0); break;  // 日
                    case 9: ret.push(9); break;  // 祝
                    }
                }

                return ret;
            },

            /**
             *　休日判定
             *
             * @param {string} yyyymmdd 日付
             * @param {Array<number>} holiday 休日曜日情報
             * @return {boolean} 真偽値
             */
            isHoliday(yyyymmdd, holiday) {
                let ret = false;
                let date = new Date(yyyymmdd.replace(/-/g, "/"))
                let weekday = date.getDay();
                if (holiday != null && holiday.length > 0 && holiday.indexOf(weekday) >= 0) {
                    ret = true;
                }
                return ret;
            },

            /**
             *　Storage読み込み
             *
             * @param {string} name ストレージ要素名
             * @return {any} 値 
             */
            readStore(name) {
                let restaurant = app.$utils.ocopy(store.state.restaurant);
                if (!restaurant) { restaurant = {}; }
                return (name in restaurant) ? restaurant[name] : null;
            },

            /**
             * Storage書き込み
             *
             * @param {string} name ストレージ要素名
             * @param {any} value 値
             */
            writeStore(name, value) {
                let restaurant = app.$utils.ocopy(store.state.restaurant);
                if (!restaurant) { restaurant = {}; }
                restaurant[name] = value;
                store.commit("restaurant", restaurant);
            },

            /**
             * ステータスレコード生成
             *
             * @return {Object} ステータスレコード
             */
            createStatusRecord() {
                return { 
                    status: null,
                    name: null,
                    start: null,
                    end: null,
                    events: [],
                }; 
            },

            /**
             * イベントレコード生成
             *
             * @return {Object} イベントレコード 
             */
            createEventRecord() {
                return {
                    shopId: null,
                    name: null,
                    start: null,
                    end: null,
                    color: null,
                    reserved: null,
                };
            },

            /**
             * 一日分イベント生成（30分間隔）
             *
             * @param {number} day 予約日
             * @param {Object} restaurant レストラン店舗情報
             * @return {Array<Object>} 一日分イベント 
             */
            createEvents(day, restaurant) {
                let ret = [];

                // レストラン開始・終了時間
                const start = `${day.replace(/-/g, "/")} ${restaurant.start}`;
                const end = `${day.replace(/-/g, "/")} ${restaurant.end}`;
                let fdate = new Date(start);
                let tdate = new Date(end);
                // 営業時間帯
                let ftime = fdate.getTime();
                let ttime = tdate.getTime();

                // 時間帯ループ
                for (let dt=ftime; dt<ttime; dt=(dt+(1000 * 60 * 30))) {
                    const startDate = new Date(dt);
                    const endDate = new Date(dt+(1000 * 60 * 30));
                    const stime = `${day} ${("00"+startDate.getHours()).slice(-2)}:${("00"+startDate.getMinutes()).slice(-2)}`;
                    const etime = `${day} ${("00"+endDate.getHours()).slice(-2)}:${("00"+endDate.getMinutes()).slice(-2)}`;

                    // イベント
                    let event = app.$restaurant.utils.createEventRecord();
                    event.shopId = restaurant.id; 
                    event.name = _i18n.restaurant.vacant;
                    event.start = stime;
                    event.end = etime;
                    event.color = "success";
                    ret.push(event);
                }

                return ret;
            },

            /**
             * ロケール設定
             *
             * @param {string} locale
             */
            setLocale(locale) {
                _i18n = app.i18n.messages[locale];
            }
        },

        // ============================================
        //     Lambdaアクセス (Axios)
        // ============================================
        axios: {
            /**
             *　店舗一覧取得API
             *
             * @return {Object} APIレスポンス内容
             */
            areaData: async() => {
                // 送信パラメーター
                const params = {
                    locale: store.state.locale,
                };
                // GET送信
                const response = await $axios.get(`${_stage}/shop_list_get`, { params: params });
                return response.status==200 ? response.data : null;
            },

            /**
             *　コース詳細情報取得API
             *
             * @param {number} shopId
             * @return {Object} APIレスポンス内容
             */
            courseData: async(shopId) => {
                // 送信パラメーター
                const params = {
                    locale: store.state.locale,
                    shopId: shopId,
                };
                // GET送信
                const response = await $axios.get(`${_stage}/course_list_get`, { params: params });
                return response.status==200 ? response.data : null;
            },

            /**
             * 店舗予約状況カレンダー取得API
             *
             * @param {number} shopId 店舗ID
             * @param {string} month 年月
             * @return {Object} APIレスポンス内容 
             */
            shopStatusCalendar: async(shopId, month) => {
                // 送信パラメーター
                const params = {
                    locale: store.state.locale,
                    shopId: shopId,
                    preferredYearMonth: `${month.substr(0, 4)}-${month.substr(4, 2)}`,
                };
                const response = await $axios.get(`${_stage}/shop_calendar_get`, { params: params });
                return response.status==200 ? response.data : null;
            },

            /**
             * 店舗日別予約状況取得API
             *
             * @param {number} shopId 店舗ID
             * @param {string} day 予約日
             * @return {Object} APIレスポンス内容
             */
            shopDailyStatus: async(shopId, day) => {
                // 送信パラメーター
                const params = {
                    locale: store.state.locale,
                    shopId: shopId,
                    preferredDay: day,
                };
                const response = await $axios.get(`${_stage}/reservation_time_get`, { params: params });
                return response.status==200 ? response.data : null;
            },

            /**
             * 予約登録API
             *
             * @param {Object} params 送信パラメーター
             * @return {Object} APIレスポンス内容 
             */
            reserve: async(params) => {
                // 送信パラメーター
                params['locale'] = store.state.locale;
                // POST送信
                const response = await $axios.post(`${_stage}/reservation_put`, params);
                return response.status==200 ? response.data : null;
            },
        },

        // ============================================
        //     Lambdaアクセス (Amplify API)
        // ============================================
        amplify: {
            /**
             *　店舗一覧取得API
             *
             * @return {Object} APIレスポンス内容
             */
            areaData: async() => {
                let response = null;
                // 送信パラメーター
                const myInit = {
                    queryStringParameters: {
                        locale: store.state.locale,                        
                    },
                };
                // GET送信
                try {
                    response = await app.$amplify.API.get("LambdaAPIGateway", `${_stage}/shop_list_get`, myInit);
                } catch (error) {
                    app.$utils.showHttpError(error);
                }

                return response;
            },

            /**
             *　コース詳細情報取得API
             *
             * @param {number} shopId
             * @return {Object} APIレスポンス内容
             */
            courseData: async(shopId) => {
                let response = null;
                // 送信パラメーター
                const myInit = {
                    queryStringParameters: {
                        locale: store.state.locale,                        
                        shopId: shopId,
                    },
                };
                // GET送信
                try {
                    response = await app.$amplify.API.get("LambdaAPIGateway", `${_stage}/course_list_get`, myInit);
                } catch (error) {
                    app.$utils.showHttpError(error);
                }

                return response;
            },

            /**
             * 店舗予約状況カレンダー取得API
             *
             * @param {number} shopId 店舗ID
             * @param {string} month 年月
             * @return {Object} APIレスポンス内容 
             */
            shopStatusCalendar: async(shopId, month) => {
                let response = null;
                // 送信パラメーター
                const myInit = {
                    queryStringParameters: {
                        locale: store.state.locale,                        
                        shopId: shopId,
                        preferredYearMonth: `${month.substr(0, 4)}-${month.substr(4, 2)}`,
                    },
                };
                // GET送信
                try {
                    response = await app.$amplify.API.get("LambdaAPIGateway", `${_stage}/shop_calendar_get`, myInit);
                } catch (error) {
                    app.$utils.showHttpError(error);
                }

                return response;
            },

            /**
             * 店舗日別予約状況取得API
             *
             * @param {number} shopId 店舗ID
             * @param {string} day 予約日
             * @return {Object} APIレスポンス内容
             */
            shopDailyStatus: async(shopId, day) => {
                let response = null;
                // 送信パラメーター
                const myInit = {
                    queryStringParameters: {
                        locale: store.state.locale,                        
                        shopId: shopId,
                        preferredDay: day,
                    },
                };
                // GET送信
                try {
                    response = await app.$amplify.API.get("LambdaAPIGateway", `${_stage}/reservation_time_get`, myInit);
                } catch (error) {
                    app.$utils.showHttpError(error);
                }

                return response;
            },

            /**
             * 予約登録API
             *
             * @param {Object} params 送信パラメーター
             * @return {Object} APIレスポンス内容 
             */
            reserve: async(params) => {
                let response = null;
                // 送信パラメーター
                params['locale'] = store.state.locale;
                const myInit = {
                    body: params,
                };
                // POST送信
                try {
                    response = await app.$amplify.API.post("LambdaAPIGateway", `${_stage}/reservation_put`, myInit);
                } catch (error) {
                    app.$utils.showHttpError(error);
                }

                return response;
            },
        },
    }
}

export default ({ $axios, app, store, env }, inject) => {
    inject("restaurant", VueRestaurant($axios, app, store, env));
}
