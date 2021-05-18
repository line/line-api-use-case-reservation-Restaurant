<template>
    <v-app dark class="reserve-font-size">
        <v-expansion-panels class="mb-14">
            <v-container>
                <v-row>
                    <v-expansion-panel v-for="area in areas" v-bind:key="area.code">
                        <v-expansion-panel-header color="" style="opacity:0.8;">
                            <div class="font-weight-bold" style="font-size:1.0rem;">
                                <span class="line-color">{{ area.name }}</span>
                            </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content color="grey lighten-5">
                            <v-container>
                                <v-row>
                                    <v-col cols="12" sm="6" md="4" v-for="restaurant in restaurants[area.code]" v-bind:key="restaurant.id">
                                        <v-hover v-slot:default="{ hover }" open-delay="150">
                                            <v-card outlined class="restaurant" v-bind:elevation="hover ? 16 : 2" v-bind:ripple="rippled" v-on:mousedown.capture="mousedownCard(1)" v-on:click="reserve(area, restaurant)">
                                                <v-list-item-title class="mt-1 ml-1">
                                                    <span style="font-size:1.2em;">{{ restaurant.name }}</span>
                                                </v-list-item-title>
                                                <v-list-item class="ma-0 pa-0">
                                                    <v-img class="ma-1" style="width:50%;" v-bind:src="restaurant.img" alt="LINE Shop" />
                                                    <v-sheet class="ma-1 pa-2" style="width:50%; font-size:0.7em; background-color:transparent;">
                                                        <ul class="ma-0 pa-1">
                                                            <li class="pb-1">{{ $t("areas.msg001") }}: {{ restaurant.start }}～{{ restaurant.end }}</li>
                                                            <li class="pb-1">{{ $t("areas.msg002") }}: {{ weekdayNames(restaurant.holiday) }}</li>
                                                            <li class="pb-1">{{ $t("areas.msg003") }}: ¥{{ restaurant.budget ? restaurant.budget.toLocaleString() : null }}</li>
                                                            <li class="pb-1">{{ $t("areas.msg004") }}: {{ restaurant.seats }}{{ $t("areas.msg005") }}</li>
                                                            <li class="pb-1">{{ $t("areas.msg006") }}: {{ restaurant.smoking }}</li>
                                                            <li class="pb-1">
                                                                <a href="javascript:void(0);"
                                                                    v-bind:style="lineIcon"
                                                                    v-on:mousedown="mousedownCard(2)"
                                                                    v-on:click.stop="openLineOA(restaurant.line)"
                                                                >
                                                                    {{ $t("areas.msg007") }}
                                                                </a>
                                                            </li>
                                                            <li class="pb-1">Tel: {{ restaurant.tel }}</li>
                                                        </ul>
                                                    </v-sheet>
                                                </v-list-item>
                                                <v-list-item-action-text>
                                                    <p class="ma-0" style="font-size:1.0em; color:gray;">
                                                        <v-icon>mdi-map-marker</v-icon>
                                                        <a href="javascript:void(0);"
                                                           v-bind:style="mapIcon"
                                                           v-on:mousedown="mousedownCard(2)"
                                                           v-on:click.stop="openMap(restaurant.name, restaurant.map)"
                                                        >
                                                            {{ restaurant.address }}
                                                        </a>
                                                    </p>
                                                </v-list-item-action-text>
                                            </v-card>
                                        </v-hover>
                                    </v-col>
                                </v-row>
                            </v-container>
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-row>
            </v-container>
        </v-expansion-panels>
        <!-- Footer -->
        <vue-footer icons="1"></vue-footer>
    </v-app>
</template>

<script>
/**
 * エリア・店舗選択画面 
 * 
 */
import VueFooter from "~/components/restaurant/Footer.vue"

export default {
    layout: "reserve/restaurant",
    components: {
        VueFooter,
    },
    async asyncData({ app }) {
        // エリアデータ＆店舗データ取得 (Call Backend Lambda)
        const data = await app.$restaurant.getAreaShops();
        const areas = data.areas;
        const restaurants = data.restaurants;

        return {
            areas: areas,
            restaurants: restaurants,
        };
    },
    head() {
        return {
            title: this.$t("title")
        }
    },
    data() {
        return {
            areas: null,
            restaurants: null,
            rippled: false,
            icon: {
                line: require('~/assets/img/icon/line.png'),
                map: require('~/assets/img/icon/map.png')
            }
        }
    },
    computed: {
        lineIcon() {
            return `cursor:url(${this.icon.line}) 12 12, auto`;
        },
        mapIcon() {
            return `cursor:url(${this.icon.map}) 12 12, auto`;
        }
    },
    created() {

    },
    methods: {
        /**
         * 曜日名文字列
         * 
         * @param {Array<number>|string} weekdays 曜日情報
         * @returns {string} カンマ区切り曜日名
         */
        weekdayNames(weekdays) {
            let names = "";
            if (typeof(weekdays) == "object") {
                for (const weekday of weekdays) {
                    if (names.length > 0) { names += ", "; }
                    names += this.$utils.weekdayName(weekday);
                }
            } else {
                names = weekdays;
            }

            return (names.length == 0) ? "なし" : names;
        },

        /**
         * 予約カレンダー画面へ遷移
         * 
         * @param {Array<Object>} area エリア情報
         * @param {Array<Object>} restaurant レストラン店舗情報
         */
        reserve(area, restaurant) {
            this.$flash.set("area", area);
            this.$flash.set("restaurant", restaurant);
            this.$router.push(`/restaurant/${area.code}/${restaurant.id}`);
        },

        /**
         * 店舗カードマウスダウン処理
         * 
         * @param {number} num インデックス番号
         */
        mousedownCard(num) {
            const tagName = event.srcElement.tagName;
            if (num == 2) {
                event.stopPropagation();
            } else {
                if (tagName != "A") {
                    this.rippled = true;
                }
            }
        },

        /**
         * 地図を開く
         * 
         * @param {string} name 店舗名称
         * @param {Object} coordinate 緯度・経度
         */
        openMap(name, coordinate) {
            let latitude = coordinate.latitude;
            let longitude = coordinate.longitude;
            this.$utils.openMapApp(latitude, longitude, 18);
        },

        /**
         * LINE公式アカウントを開く
         * 
         * @param {string} LINE公式アカウント
         */
        openLineOA(line) {
            this.$utils.openLineOA(line);
        }
    }
}
</script>

<style scoped>
.text-area {
    color: #00ba00;
}
.map-title {
    color: #fff;
}
.restaurant {
    cursor: pointer;
    padding: 4px;
}
.reserve-font-size {
    font-size: 16px;
    letter-spacing: 0.06em;
}
.restaurant-header {
    font-size: 1.1em;
}
@media screen and (max-width:540px) {
    .reserve-font-size {
        font-size: 12px;
        letter-spacing: 0.06em;
    }
    .hairsalon-header {
        font-size: 1.0em;
    }
}
</style>
