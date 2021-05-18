/**
 * ユーティリティープラグイン
 *
 * @param {Object} app
 * @param {Object} store
 * @return {Object} 
 */
const VueUtils = (app, store) => {
    /** @type {Object} ロケール */
    let _i18n = app.i18n.messages[store.state.locale];

    // ==============================================
    //  Public Methods
    // ==============================================
    const _functions = {
        /**
         * オブジェクトコピー
         *
         * @param {Object} obj コピー元オブジェクト
         * @return {Object} コピーオブジェクト
         */
        ocopy(obj) {
            let ret = null;
            if (obj != null) {
                ret = JSON.parse(JSON.stringify(obj));
            }
            return ret;
        },

        /**
         * 日付フォーマット
         *
         * @param {Object} date 日付オブジェクト
         * @param {string} format 指定日付フォーマット
         * @return {string} 日付文字列
         */
        dateFormat(date, format) {
            return _dateformat(date, format);
        },

        /**
         * 現在日付取得
         *
         * @param {string} format 指定日付フォーマット
         * @param {number} addMonths 月数加算
         * @return {string} 日付文字列
         */
        now(format, addMonths) {
            let date = new Date();
            if (typeof(addMonths) == "number") {
                // 月末日処理
                const endDayOfMonth = new Date(date.getFullYear(), date.getMonth()+addMonths+1, 0);
                date.setMonth(date.getMonth() + addMonths);
                if (date.getTime() > endDayOfMonth.getTime()) {
                    date = endDayOfMonth;
                }
            }
            return _dateformat(date, format);
        },

        /**
         *　乱数生成
         *
         * @param {number} min 最小値
         * @param {number} max 最大値
         * @return {number} 乱数 
         */
        random(min, max) {
            return Math.floor((max - min + 1) * Math.random()) + min;
        },

        /**
         *　曜日変換（値-->名）
         *
         * @param {number|string} weekday 曜日値
         * @return {string} 曜日名 
         */
        weekdayName(weekday) {
            let name = "";

            switch (parseInt(weekday, 10)) {
            case 0: name = _i18n.utils.sun; break;
            case 1: name = _i18n.utils.mon; break;
            case 2: name = _i18n.utils.tue; break;
            case 3: name = _i18n.utils.wed; break;
            case 4: name = _i18n.utils.thu; break;
            case 5: name = _i18n.utils.fri; break;
            case 6: name = _i18n.utils.sat; break;
            }

            return name;
        },

        /**
         *　月名英語変換（値-->英語名）
         *
         * @param {number|string} month 月値
         * @return {string} 月英語名 
         */
        englishMonth(month) {
            let engMonth = null;

            switch (parseInt(month, 10)) {
            case 1: engMonth = "Jan."; break;   // January
            case 2: engMonth = "Feb."; break;   // February
            case 3: engMonth = "Mar."; break;   // March
            case 4: engMonth = "Apr."; break;   // April
            case 5: engMonth = "May."; break;   // May
            case 6: engMonth = "Jun."; break;   // June
            case 7: engMonth = "Jul."; break;   // July
            case 8: engMonth = "Aug."; break;   // August
            case 9: engMonth = "Sep."; break;   // September
            case 10: engMonth = "Oct."; break;  // October
            case 11: engMonth = "Nov."; break;  // November
            case 12: engMonth = "Dec."; break;  // December
            }

            return engMonth;
        },

        /**
         * 日付分加算
         *
         * @param {string} datetime 日付
         * @param {number} minutes 加算分数
         * @return {Object} 日付オブジェクト
         */
        addMinutes(datetime, minutes) {
            const date = new Date(datetime.replace(/-/g, "/"));
            date.setMinutes(date.getMinutes() + minutes);

            return date;
        },

        /**
         *　iOS判定
         *
         * @return {boolean} 真偽値
         */
        isIOS() {
            const userAgent = navigator.userAgent.toLowerCase();
            return (userAgent.indexOf("iphone")>=0 || userAgent.indexOf("ipad")>=0 || userAgent.indexOf("ipod")>=0); 
        },

        /**
         *　Android判定
         *
         * @return {boolean} 真偽値
         */
        isAndroid() {
            const userAgent = navigator.userAgent.toLowerCase();
            return (userAgent.indexOf("android")>=0);
        },

        /**
         * 地図アプリ起動
         *
         * @param {number} latitude 緯度
         * @param {number} longitude 経度
         * @param {number} zoom ズーム
         * @param {boolean} [markered=true] マーカー有無
         */
        openMapApp(latitude, longitude, zoom, markered=true) {
            let params = `ll=${latitude},${longitude}&z=${zoom}`;
            if (markered) {
                params += `&q=${latitude},${longitude}`;
            }

            if (this.isIOS()) {
                liff.openWindow({ url: `https://maps.apple.com/maps?${params}`, external: true });
            } else if (this.isAndroid()) {
                liff.openWindow({ url: `https://maps.google.com/maps?${params}`, external: true });
            } else {
                window.open(`https://maps.google.com/maps?${params}`, "_blank");
            }
        },

        /**
         * LINE公式アカウント開始
         *
         * @param {*} line
         */
        openLineOA(line) {
            if (this.isIOS()) {
                location.href = line;
            } else if (this.isAndroid()) {
                location.href = line;
            } else {
                window.open(line, "_blank");
            }
        },

        /**
         * HTTPエラー表示
         *
         * @param {Object} error
         */
        showHttpError(error) {
            if (error.response && error.response.status >= 400) {
                // HTTP 403 Topへ画面遷移
                if (error.response.status == 403) {
                    const errmsg = _i18n.error.msg005;
                    window.alert(errmsg);
                    store.commit("lineUser", null);
                    if (liff) liff.logout();
                    window.location = `https://liff.line.me/${process.env.LIFF_ID}`;
                    return true;
                }

                const response = error.response;
                const message = (!response.data && this.httpStatus[response.status]) ? this.httpStatus[response.status].message : response.data;
                setTimeout(() => {
                    store.commit("axiosError", `status=${response.status} ${response.statusText} ${message}`);
                }, 500);
                return true;
            }
            return false;
        },

        /**
         * HTTPステータス情報
         *
         */
        httpStatus: {
            // Client Error
            400: { message: "Bad Request" },
            401: { message: "Unauthorized" },
            402: { message: "Payment Required" },
            403: { message: "Forbidden" },
            404: { message: "Not Found" },
            405: { message: "Method Not Allowed" },
            406: { message: "Not Acceptable" },
            407: { message: "Proxy Authentication Required" },
            408: { message: "Request Timeout" },
            409: { message: "Conflict" },
            410: { message: "Gone" },
            411: { message: "Length Required" },
            412: { message: "Precondition Failed" },
            413: { message: "Request Entity Too Large" },
            414: { message: "Request-URI Too Long" },
            415: { message: "Unsupported Media Type" },
            416: { message: "Requested Range Not Satisfiable" },
            417: { message: "Expectation Failed	Expect" },
            // Server Error
            500: { message: "Internal Server Error" },
            501: { message: "Not Implemented" },
            502: { message: "Bad Gateway" },
            503: { message: "Service Unavailable" },
            504: { message: "Gateway Timeout" },
            505: { message: "HTTP Version Not Supported" },
        },

        /**
         * ロケール設定
         *
         * @param {string} locale
         */
        setLocale(locale) {
            _i18n = app.i18n.messages[locale];
        },
    };

    // ==============================================
    //  Private Methods
    // ==============================================

    /**
     * 日付フォーマット
     *
     * @param {Object} date 日付オブジェクト
     * @param {string} format 指定日付フォーマット
     * @return {string} 日付文字列
     */
    const _dateformat = (date, format) => {
        const yyyy = date.getFullYear();
        const mm = ("00" + (date.getMonth() + 1)).slice(-2);
        const dd = ("00" + date.getDate()).slice(-2);
        const hh = ("00" + date.getHours()).slice(-2);
        const mi = ("00" + date.getMinutes()).slice(-2);
        const ss = ("00" + date.getSeconds()).slice(-2);

        let ret = `${yyyy}/${mm}/${dd} ${hh}:${mi}:${ss}`;
        if (format !== undefined) {
            let strFormat = format.toLowerCase();
            strFormat = strFormat.replace("yyyy", yyyy);
            strFormat = strFormat.replace("mm", mm);
            strFormat = strFormat.replace("dd", dd);
            strFormat = strFormat.replace("hh", hh);
            strFormat = strFormat.replace("mi", mi);
            strFormat = strFormat.replace("ss", ss);
            ret = strFormat;
        }

        return ret;
    };


    return _functions;
}

export default ({ app, store }, inject) => {
    inject("utils", VueUtils(app, store));
}
