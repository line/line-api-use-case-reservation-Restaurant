<template>
    <v-app class="reserve-font-size">
        <!-- Header -->
        <v-app-bar app class="elevation-3" style="width:100%;">
            <v-toolbar-title>
                <v-select
                    solo
                    dense
                    prepend-icon="mdi-calendar"
                    v-bind:items="months"
                    v-model="selectedMonth"
                    class="mt-6"
                    style="max-width:185px;"
                    v-on:change="changeMonth"
                ></v-select>
            </v-toolbar-title>
            <v-spacer></v-spacer>
            <v-toolbar-title>
                <v-chip outlined class="float-right" style="font-size:0.8em;">
                    <span class="line-color">
                        <span class="hidden-xs-only">{{ area ? area.name : null }}&nbsp;</span>
                        {{ restaurant ? restaurant.name : null }}
                    </span>
                </v-chip>
            </v-toolbar-title>
        </v-app-bar>
        <!-- Weekdays Header　-->
        <v-container fluid style="margin-top:82px;">
            <v-row justify="center">
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold; color:red;">{{ $t("utils.sun")}}</span></v-col>
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold;">{{ $t("utils.mon")}}</span></v-col>
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold;">{{ $t("utils.tue")}}</span></v-col>
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold;">{{ $t("utils.wed")}}</span></v-col>
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold;">{{ $t("utils.thu")}}</span></v-col>
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold;">{{ $t("utils.fri")}}</span></v-col>
                <v-col class="ma-0 pa-0 text-center"><span style="font-weight:bold; color:blue;">{{ $t("utils.sat")}}</span></v-col>
            </v-row>
        </v-container>
        <!-- Calendar -->
        <v-sheet width="100%" height="calc(100% - 151px)">
            <v-calendar
                v-bind:locale="locale"
                v-bind:day-format="dayFormat"
                v-bind:month-format="monthFormat"
                v-bind:weekday-format="weekdayFormat"
                v-bind:interval-format="intervalFormat"
                v-model="calendar"
                class="mt-0 pt-2"
            >
                <template v-slot:day="context">
                    <div v-if="context.date.replace('-', '').substr(0,6) == selectedMonth" style="height:100%;">
                        <div v-if="isValid(context.date, minDate, maxDate)" v-bind:style="dayStyle(context.date, selectedMonth, minDate, maxDate)">
                            <v-hover v-slot:default="{ hover }" open-delay="150">
                                <v-card color="white" class="daily-card" v-ripple="{ class: 'white--text' }" v-bind:elevation="hover ? 16 : 2" style="height:100%;" v-on:click="showDayDetail(context.date)">
                                    <v-card-text class="ma-0 pa-0 pt-lg-3 pt-1" style="font-size:1.0em; white-space:nowrap; height:100%;">
                                        <div>{{ dateFormat(context.date, selectedMonth, $vuetify.breakpoint) }}</div>
                                        <div class="pa-1 hidden-xs-only">
                                            <div v-if="dayStatus(context.date)==3" class="daily-height">
                                                <div>{{ $t("calendar.vacancy") }}</div>
                                                <v-btn small rounded color="error" class="ma-0 pa-0 btn-opacity">{{ $t("calendar.full") }}</v-btn>
                                            </div>
                                            <div v-else-if="dayStatus(context.date)==2" class="daily-height">
                                                <div>{{ $t("calendar.vacancy") }}</div>
                                                <v-btn small rounded color="warning" class="ma-0 pa-0 btn-opacity">{{ $t("calendar.vacant_little") }}</v-btn>
                                            </div>
                                            <div v-else-if="dayStatus(context.date)==1" class="daily-height">
                                                <div>{{ $t("calendar.vacancy") }}</div>
                                                <v-btn small rounded color="success" class="ma-0 pa-0 btn-opacity">{{ $t("calendar.vacant") }}</v-btn>
                                            </div>
                                            <div v-else>
                                                <div class="ma-2" style="color:red;">{{ $t("calendar.closingday") }}</div>
                                            </div>
                                        </div>
                                        <div class="hidden-sm-and-up text-center">
                                            <div v-if="dayStatus(context.date)==3" class="daily-height-small">
                                                <v-btn small fab color="error" class="ma-0 pa-0 btn-opacity">{{ $t("calendar.short_full") }}</v-btn>
                                            </div>
                                            <div v-else-if="dayStatus(context.date)==2" class="daily-height-small">
                                                <v-btn small fab color="warning" class="ma-0 pa-0 btn-opacity">{{ $t("calendar.short_vacant_little") }}</v-btn>
                                            </div>
                                            <div v-else-if="dayStatus(context.date)==1" class="daily-height-small">
                                                <v-btn small fab color="success" class="ma-0 pa-0 btn-opacity">{{ $t("calendar.short_vacant") }}</v-btn>
                                            </div>
                                            <div v-else>
                                                <div class="ma-2" style="color:red;">{{ $t("calendar.short_closingday") }}</div>
                                            </div>
                                        </div>
                                    </v-card-text>
                                </v-card>
                            </v-hover>
                        </div>
                        <div v-else style="width:100%; height:100%; background-color:#f8f8ff;">
                            <div class="hidden-sm-and-up" style="min-height:70px;"></div>
                        </div>
                    </div>
                    <div v-else style="width:100%; height:100%; background-color:#dcdcdc;">
                    </div>
                </template>
            </v-calendar>
        </v-sheet>

        <!-- Detail Dialog -->
        <v-dialog v-model="dialog" fullscreen hide-overlay transition="dialog-bottom-transition">
            <v-card>
                <v-toolbar color="grey lighten-5">
                    <v-btn icon absolute style="left:2px; top:-8px;" v-on:click="closeDialog">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                    <v-toolbar-title style="width:100%; padding:0; text-align:center;">
                        <span class="daily-title">{{ reserveDate }} {{ restaurant.name }}&nbsp;&nbsp;{{ $t("calendar.msg001") }}</span>
                    </v-toolbar-title>
                </v-toolbar>
                <div class="text-center ma-2">
                    <v-chip outlined style="border-color:#00ba00;">
                        <span class="line-color">{{ area ? area.name : null }}&nbsp;&nbsp;{{ restaurant.name }}</span>
                    </v-chip>
                </div>
                <v-calendar 
                    v-bind:locale="locale"
                    type="day"
                    v-model="reserveDate"
                    v-bind:events="events"
                    v-bind:event-color="eventColor"
                    v-bind:event-name="eventNameFormat"
                    v-bind:first-interval="8"
                    v-on:click:event="clickEvent"
                >
                </v-calendar>
            </v-card>
            <v-btn 
                fixed
                rounded
                absolute bottom right
                color="success"
                class="mb-10"
                style="width:160px; color:white; opacity:0.9;"
                v-on:click="showDialog"
                v-bind:disabled="reserveButton"
            >
                {{ $t("calendar.msg002") }}
            </v-btn>
            <!-- Reserve Dialog -->
            <v-dialog persistent max-width="460px" v-model="reserveDialog">
                <div class="shake-text" v-show="fromtoErrored">
                    {{ $t("calendar.msg003") }}
                </div>
                <v-toolbar dense class="elevation-0">
                    <v-btn icon style="position:absolute;" v-on:click="reserveDialog=false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                    <div style="margin:auto; font-size:1.0em;">{{ $t("calendar.msg004") }}</div>
                </v-toolbar>
                <v-card class="elevation-0" style="border-radius:0;">
                    <v-card-text class="pb-0">
                        <v-form ref="form" v-model="valid" lazy-validation>
                            <v-container>
                                <v-row dense>
                                    <v-col cols="12">
                                        <v-select
                                            v-bind:label="$t('calendar.msg005')"
                                            v-bind:items="times"
                                            item-text="text"
                                            item-value="value"
                                            v-model="sendReserve.start"
                                            required
                                            v-bind:rules="[v=>!!v || $t('calendar.msg006')]"
                                            v-on:change="changeCourse(sendReserve.start, sendReserve.course);"
                                        ></v-select>
                                    </v-col>
                                </v-row>
                                <v-row dense>
                                    <v-col cols="12">
                                        <v-select
                                            v-bind:label="$t('calendar.msg007')"
                                            v-bind:items="times"
                                            item-text="text"
                                            item-value="value"
                                            v-model="sendReserve.end"
                                            required
                                            v-bind:readonly="endtimeDisabled"
                                            v-bind:rules="[v=>!!v || $t('calendar.msg008')]"
                                            v-on:change="changeEndtime"
                                        ></v-select>
                                    </v-col>
                                </v-row>
                                <v-row dense>
                                    <v-col cols="12">
                                        <v-text-field
                                            type="number"
                                            v-bind:label="$t('calendar.msg009')"
                                            min="0"
                                            v-bind:max="maxSeats"
                                            v-model="sendReserve.people"
                                            required
                                            v-bind:rules="[v=>!!v ||  $t('calendar.msg010'), v=>!(v&&parseInt(v,10)<=0) || $t('calendar.msg011')]"
                                            v-on:change="modifyPeopleNum()"
                                        ></v-text-field> 
                                    </v-col>
                                </v-row>
                                <v-row dense>
                                    <v-col cols="12">
                                        <v-select
                                            v-bind:label="$t('calendar.msg012')"
                                            v-bind:items="course"
                                            item-text="text"
                                            item-value="value"
                                            v-model="sendReserve.course"
                                            v-on:change="changeCourse(sendReserve.start, sendReserve.course)"
                                        ></v-select>
                                    </v-col>
                                </v-row>
                                <v-row dense>
                                    <v-col cols="12">
                                        {{ sendReserve.comment }}
                                    </v-col>
                                </v-row>
                            </v-container>
                        </v-form>
                    </v-card-text>
                </v-card>
                <footer style="text-align:center; width:100%;">
                    <v-btn 
                        class="ma-0 font-weight-bold"
                        style="width:100%; height:48px; background-color:#00ba00; border-radius:0 0 4px 4px;"
                        v-on:click="reserve(sendReserve)"
                    >
                        <span style="color:#fff;">{{ $t("calendar.msg013") }}</span>
                    </v-btn>
                </footer>
            </v-dialog>
            <!-- Footer -->
            <vue-footer icons="3" v-bind:shop="restaurant"></vue-footer>
        </v-dialog>

        <!-- Error Message Dialog -->
        <v-dialog v-model="errorDialog" max-width="300px">
            <v-card>
                <v-card-title class="line-background-color">
                    <v-btn absolute icon style="right:0; top:-5px;" v-on:click="errorDialog=false">
                        <v-icon small>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>
                <v-card-text class="text-center font-weight-bold pa-6 pb-3" style="color:red; line-height:1.4em; font-size:1.3em;">
                    <span v-html="errorDialogMessage.title"></span>
                </v-card-text>
                <v-card-text>
                    <span v-html="errorDialogMessage.text"></span>
                </v-card-text>
            </v-card>
        </v-dialog>
        <!-- Footer -->
        <vue-footer icons="2" v-bind:shop="restaurant.id"></vue-footer>
    </v-app>
</template>

<script>
/**
 * 予約カレンダー画面
 * 
 */
import VueFooter from "~/components/restaurant/Footer.vue"

export default {
    layout: "reserve/restaurant",
    components: {
        VueFooter,
    },
    async asyncData({ app, store, params }) {
        // 対象期間取得
        const months = app.$restaurant.utils.monthList(2);
        const minDate = app.$utils.now("yyyymmdd");
        const maxDate = app.$utils.now("yyyymmdd", 2);
        // 対象店舗取得
        let area = app.$flash.hold("area");
        let restaurant = app.$flash.hold("restaurant");
        // リロード対応
        if (area === undefined) {
            const data = await app.$restaurant.getAreaShops();
            area = data.areas.find((v) => v.code == params.code);
            restaurant = data.restaurants[params.code].find((v) => v.id == params.id);
        }

        // 予約時間帯リスト取得
        const times = app.$restaurant.utils.timeList(restaurant.start, restaurant.end);
        // 予約コースリスト取得
        const coursePromise = app.$restaurant.getCourses(restaurant.id);
        // 予約状況データ取得
        const statusesPromise = app.$restaurant.getMonthlyReservationStatus(restaurant.id, months[0].value, restaurant);

        let course = await coursePromise;
        let statuses = await statusesPromise;

        return {
            statuses: statuses,
            area: area,
            restaurant: restaurant,
            selectedMonth: months[0].value,
            minDate: minDate,
            maxDate: maxDate,
            months: months,
            times: times,
            course: course,
            maxSeats: restaurant.seats,
        }
    },
    head() {
        return {
            title: this.$t("title")
        }
    },
    data() {
        return {
            reserveDate: null,
            statuses: null,
            area: null,
            restaurant: null,
            selectedMonth: null,
            minDate: null,
            maxDate: null,
            months: null,
            dialog: false,
            reserveDialog: false,
            reserveButton: false,
            events: [],
            times: null,
            course: null,
            valid: true,
            sendReserve: {
                day: null,
                start: null,
                end: null,
                people: 1,
                course: null,
                comment: null,
            },
            fromtoErrored: false,
            endtimeDisabled: false,
            maxSeats: 0,
            errorDialog: false,
            errorDialogMessage: {
                title: null,
                text: null
            },
        }
    },
    computed: {
        calendar() {
            let month = this.selectedMonth;
            if (month != null) {
                month = `${month.substr(0,4)}-${month.substr(4,2)}-01`;
            }
            return month;
        },
        locale() {
            let ret = "ja-jp"

            switch (this.$store.state.locale) {
            case "ja":
                ret = "ja-jp";
                break;
            case "en":
                ret = "en";
                break;                
            }

            return ret;
        }
    },
    created() {
        this.$nuxt.$on("dialog", this.closeDialog);
    },
    mounted() {
        this.$nextTick(() => {
            window.addEventListener("resize", this.modifyWeeksHeight);
            this.modifyWeeksHeight();
        });
    },
    updated() {
        this.$nextTick(() => {
            this.modifyWeeksHeight();
        });
    },
    beforeDestroy() {
        window.removeEventListener("resize", this.modifyWeeksHeight);
    },
    methods: {
        /**
         * カレンダー年月フォーマット
         * 
         * @param {string} datetime 日付
         * @returns {string} 年月
         */
        monthFormat(datetime) {
            let date = new Date(datetime.date);
            let month = date.getMonth() + 1;
            return `${month} /`;
        },

        /**
         * カレンダー日フォーマット
         * 
         * @param {Object} datetime v-calendar日付オブジェクト
         * @returns {number} 日
         */
        dayFormat(datetime) {
            let day = datetime.day;
            switch (datetime.weekday) {
            case 0:
                day = `${day}`;
                break;
            case 6:
                day = `${day}`;
                break;
            }
            return day;
        },

        /**
         * カレンダー曜日フォーマット
         * 
         * @param {Object} datetime v-calendar日付オブジェクト
         * @returns {number} 曜日値
         */
        weekdayFormat(datetime) {
            return null;
        },

        /**
         * カレンダー間隔フォーマット
         * 
         * @returns {number} 間隔値
         */
        intervalFormat() {
            return null;
        },

        /**
         * カレンダー有効日判定
         * 
         * @param {string} date 日付
         * @param {number} min 最小日付
         * @param {number} max 最大日付
         * @returns {boolean} 真偽値
         */
        isValid(date, min, max) {
            let ret = false;

            const fmtdate = date.replace(/-/g, "");
            if (fmtdate >= min && fmtdate <= max) {
                ret = true;
            }

            return ret;
        },

        /**
         * カレンダー日ステータス
         * 
         * @param {string} date 日付
         * @returns {number} 予約状況ステータス
         */
        dayStatus(date) {
            let ret = 1;
            if (date in this.statuses) {
                ret = this.statuses[date].status;
            } else {
                ret = this.$restaurant.utils.isHoliday(date, this.restaurant.holiday) ? 0 : 1;
            }
            return ret;
        },

        /**
         * カレンダー日Style属性
         * 
         * @param {string} date 日付
         * @param {string} month 年月
         * @param {string} min 最小日付
         * @param {string} max 最大日付
         * @returns {Object} Style属性
         */
        dayStyle(date, month, min, max) {
            let style = {
                textAlign: "center",
                width: "99%",
                height: "99%",
                margin: "auto",
            };
            return style;
        },

        /**
         * カレンダー日付表示フォーマット
         * 
         * @param {string} date 日付
         * @param {string} month 年月
         * @param {Object} breakpoint Vuetifyブレークポイント
         * @returns {string} 月日
         */
        dateFormat(date, month, breakpoint) {
            let yyyymmdd = date.split("-");
            let mmdd = `${parseInt(yyyymmdd[1], 10)} / ${parseInt(yyyymmdd[2], 10)}`;
            if (breakpoint.xs) {
                mmdd = mmdd.replace(/\s/g, "");
            }
            return mmdd;
        },

        /**
         * カレンダー予約イベント表示文言フォーマット
         * 
         * @param {Object}} event 予約イベント
         * @param {boolean} timed 時間指定フラグ
         * @returns {string} HTML文字列
         */
        eventNameFormat(event, timed) {
            let name = event.input.name;
            return this.eventText(name, event);
        },

        /**
         * カレンダーイベント色
         * 
         * @param {Object} event 予約イベント
         * @returns {string} イベント色
         */
        eventColor(event) {
            return event.color;
        },

        /**
         * 予約イベント表示HTML
         * 
         * @param {string} text 表示テキスト
         * @param {Object} event 予約イベント
         * @returns {string} HTML文字列
         */
        eventText(text, event) {
            const fromto = event.input.start.split(" ")[1] + " - " + event.input.end.split(" ")[1];
            return `<div class='event-text' style='height:600px; padding:2px; font-size:1.1em;'>${text}　${fromto}</div>`;            
        },

        /**
         * 週表示高さ修正処理
         * 
         */
        modifyWeeksHeight() {
            const cards = document.getElementsByClassName("v-calendar-weekly__week");
            for (const card of cards) {
                if (card.clientHeight < 92) {
                    card.style.height = "92px";
                }
            }
        },

        /**
         * 年月変更時カレンダー表示処理
         * 
         * @param {string} month 年月
         */
        changeMonth(month) {
            const restaurantId = this.restaurant.id;
            const restaurant = this.restaurant;
            this.$restaurant.getMonthlyReservationStatus(restaurantId, month, restaurant)
            .then((data) => {
                this.statuses = data; 
            });
        },

        /**
         * 日時間帯カレンダー表示処理
         * 
         * @param {string} date 日付
         */
        async showDayDetail(date) {
            const status = this.dayStatus(date);
            if (status==0 || status==3) { return; } // 「定休日」と「無し」は詳細表示しない

            let statuses = (date in this.statuses) ? this.statuses[date] : this.$restaurant.utils.createStatusRecord(); 
            this.reserveDate = date;
            this.reserveButton = (statuses.status==3) ? true : false;

            this.events = await this.$restaurant.getDailyReservationStatus(this.restaurant.id, date, this.restaurant);
            if (!this.$store.state.axiosError) {
                this.sendReserve.day = date;
                this.dialog = true;
            }
        },

        /**
         * 予約内容入力ダイアログ表示処理
         * 
         * @param {string} start 予約開始時間
         * @param {string} end 予約終了時間
         * @param {number} reserved 予約済席数
         */
        showDialog(start, end, reserved) {
            this.sendReserve.start = (typeof(start)=="string") ? start : null;
            this.sendReserve.end = (typeof(end)=="string") ? end : null;
            this.endtimeDisabled = false;
            this.sendReserve.people = 1;
            this.sendReserve.course = 0;
            this.sendReserve.comment = null;
            this.maxSeats = (reserved && !isNaN(reserved)) ? (this.restaurant.seats - reserved) : this.restaurant.seats;
            // 予約内容入力ダイアログ表示
            this.reserveDialog = true;
            setTimeout(()=>{
                this.$refs.form.resetValidation();
            }, 0);
        },

        /**
         * ダイアログ非表示処理
         * 
         */
        closeDialog() {
            this.dialog = false;
            this.events = [];
        },

        /**
         * 予約時間帯イベントクリック時処理
         * 
         * @param {Object} e イベントオブジェクト
         */
        clickEvent(e) {
            const status = e.event.color;
            if (status == "error") { return false; }

            const start = e.event.start.split(" ")[1];
            const end = e.event.end.split(" ")[1];
            const reserved = e.event.reserved;
            this.showDialog(start, end, reserved);
        },

        /**
         * 予約コース変更時処理
         * 
         * @param {string} start 予約開始時間
         * @param {number} course 予約コースID
         */
        changeCourse(start, course) {
            this.fromtoErrored = false;
            this.endtimeDisabled = false;
            this.sendReserve.comment = null;
            if (!start || !course) { return; }
            if (course > 0) { this.endtimeDisabled = true; }

            // 終了時間算出
            const courseInfo = this.course[course];
            let datetime = `${this.reserveDate} ${start}`;
            let date = this.$utils.addMinutes(datetime, courseInfo.time);
            let endTime = this.$utils.dateFormat(date, "hh:mi");
            this.sendReserve.end = (this.times.find((v) => v.value == endTime) ? endTime : null);
            this.sendReserve.comment = courseInfo.comment;
        },

        /**
         * 予約終了時間変更時処理
         * 
         */
        changeEndtime() {
            this.fromtoErrored = false;
        },

        /**
         * 予約処理
         * 
         * @param {Object} input 予約入力内容
         * @returns {boolean} 正常・異常終了値
         */
        async reserve(input) {
            // バリデーション
            let ret = this.$refs.form.validate();
            if (input.start !=null && input.end != null) {
                if (!this.$restaurant.utils.checkFromToTime(input.start, input.end)) {
                    this.fromtoErrored = false;
                    setTimeout(() => {
                        this.fromtoErrored = true;
                    }, 0);
                    return false;
                }
            }

            if (ret) {
                const token = this.$store.state.lineUser.token;
                const shopId = this.restaurant.id;
                const day = input.day;
                const start = input.start;
                const end = input.end;
                const courseId = input.course===null ? 0 : input.course;
                const people = input.people;
                // デモ用
                const course = this.course.find((v) => v.id==courseId);
                const names = {
                    userName: this.$store.state.lineUser.name,
                    shopName: this.restaurant.name,
                    courseName: courseId==0 ? this.$t("calendar.msg014") : (course ? course.name : this.$t("calendar.msg014")),
                };

                try {
                    this.$processing.show(0, this.$t("calendar.msg015"));
                    // 予約申込送信
                    const data = await this.$restaurant.updateReserve(token, shopId, day, start, end, courseId, people, names);
                    if (data) {
                        const reservationId = data.reservationId;
                        if (isNaN(reservationId)) {
                            this.reserveDialog = false;
                        } else {
                            this.errorDialogMessage.title = this.$t("calendar.msg016");
                            this.errorDialogMessage.text = this.$t("calendar.msg017");
                            this.errorDialog = true;
                            return false;
                        }
                        // ページ遷移
                        let course = {
                            id: 0,
                            name: this.$t("calendar.msg014"),
                            time: 0,
                            price: 0,
                            comment: null,
                            text: this.$t("calendar.msg014"),
                            value: 0
                        };
                        if (input.course > 0) {
                            course = this.course[input.course];
                        }
                        const message = {
                            no: reservationId,
                            restaurant: this.restaurant,
                            name: this.$store.state.lineUser.name,
                            course: course,
                            day: input.day,
                            people: input.people,
                            start: input.start,
                            end: input.end,
                        };
                        this.$flash.set("message", message);
                        this.$router.push("/restaurant/completed");
                    }
                } finally {
                    this.$processing.hide();
                }

                return true;
            }
        },
        /**
         * 人数入力制限 (keypressイベント)
         */
        modifyPeopleNum() {
            if( Number(this.sendReserve.people) > Number(this.maxSeats)) {
                this.sendReserve.people = this.maxSeats;
            }
            
            if ( this.sendReserve.people < 1 || isNaN(this.sendReserve.people) ) {
                this.sendReserve.people = 1;
            }
            this.sendReserve.people = Math.floor(this.sendReserve.people)
         }
    }
}
</script>

<style scoped>
.v-chip:before {
    background-color: transparent;
}
.reserve-font-size {
    font-size: 16px;
}
.daily-title {
    font-size: 1.0em;
}
.daily-card {
    height: 100%;
}
.btn-opacity {
    opacity: 0.8;
}
@media screen and (max-width:540px) {
    .reserve-font-size {
        font-size: 12px;
    }
    .daily-title {
        font-size: 0.8em;
    }
}
@media screen and (orientation:landscape) {
    .daily-height {
        margin-bottom: 7px;
    }
    .daily-height-small {
        margin-bottom: 12px;
    }
}
.shake-text {
    animation: shake 0.82s cubic-bezier(.36,.07,.19,.97) both;
    transform: translate3d(0, 0, 0);
    backface-visibility: hidden;
    perspective: 1000px;
    position: relative;
    max-width: 400px;
    height: 0;
    left: 35px;
    top: 195px;
    font-size: 0.8em;
    font-weight: bold;
    color: #f00;
    z-index: 1;
}
@keyframes shake {
    10%, 90% {
        transform: translate3d(-1px, 0, 0);
    }

    20%, 80% {
        transform: translate3d(2px, 0, 0);
    }

    30%, 50%, 70% {
        transform: translate3d(-4px, 0, 0);
    }

    40%, 60% {
        transform: translate3d(4px, 0, 0);
    }
}
</style>
<style>
.v-calendar-weekly__day-label {
    display: none;
}
.v-event-timed.error.white--text {
    opacity: 0.8;
}
.v-event-timed.success.white--text {
    opacity: 0.8;
}
.v-event-timed.warning.white--text {
    opacity: 0.8;
}
</style>
