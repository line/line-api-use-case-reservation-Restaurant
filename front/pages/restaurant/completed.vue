<template>
    <v-app class="reserve-font-size" v-bind:style="style">
        <p class="font-weight-bold text-center mt-4 ml-1 mr-1 message">
            {{ message ? $t("completed.msg001", { name: message.name }) : null }}
            {{ $t("completed.msg002") }}<br/>
            <span style="color:#ff6347;">{{ $t("completed.msg003") }}</span><br/>
            {{ $t("completed.msg004") }}
            {{ $t("completed.msg005") }}                    
        </p>
        <v-card class="text-center card-size">
            <v-card-text class="menu pa-3">
                <v-row class="text-left" dense>
                    <v-col cols="5"><v-icon>mdi-store</v-icon>&nbsp;{{ $t("completed.msg006") }}</v-col>
                    <v-col cols="7">{{ message.restaurant.name }}</v-col>
                </v-row>
            </v-card-text>
            <v-card-text class="menu pa-3">
                <v-row class="text-left" dense>
                    <v-col cols="5"><v-icon>mdi-calendar</v-icon>&nbsp;{{ $t("completed.msg007") }}</v-col>
                    <v-col cols="7">{{ date }}（{{ weekday }}）</v-col>
                </v-row>
            </v-card-text>
            <v-card-text class="menu pa-3">
                <v-row class="text-left" dense>
                    <v-col cols="5"><v-icon>mdi-clock</v-icon>&nbsp;{{ $t("completed.msg008") }}</v-col>
                    <v-col cols="7">{{ message.start }} ～ {{ message.end }}</v-col>
                </v-row>
            </v-card-text>
            <v-card-text class="menu pl-3 pr-3 pt-1 pb-3">
                <v-row class="text-left" dense>
                    <v-col cols="5" style="margin:auto;"><v-icon>fas fa-user</v-icon>&nbsp;{{ $t("completed.msg009") }}</v-col>
                    <v-col cols="7" style="margin:auto;">
                        {{ $t("completed.msg013", { people: message.people }) }}
                    </v-col>
                </v-row>
            </v-card-text>
            <v-card-text class="menu pa-3">
                <v-row class="text-left" dense>
                    <v-col cols="5"><v-icon>fas fa-utensils</v-icon>&nbsp;{{ $t("completed.msg010") }}</v-col>
                    <v-col cols="7">
                        {{ message.course.name }}&nbsp;<span v-if="message.course.id!=0">({{ $t("completed.msg011", { price: message.course.price.toLocaleString() }) }})</span>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
        <!-- ボタン -->
        <v-footer fixed style="opacity:0.9;" class="pa-0 footer-height">
            <v-btn class="font-weight-bold" color="#00ba00" v-on:click="top()" style="color:#fff; width:100%; height:100%; border-radius:0 0 4px 4px;">
                <span class="footer-font-size" style="color:#fff;">{{ $t("completed.msg012") }}</span>
            </v-btn>
        </v-footer>
    </v-app>    
</template>

<script>
/**
 * 予約完了画面
 * 
 */
export default {
    async asyncData({ app }) {

        return {
            message: app.$flash.get("message"),
        };
    },
    head() {
        return {
            title: this.$t("title")
        }
    },
    data() {
        return {
            message: null,
            style: {
                backgroundImage: "url(https://media.istockphoto.com/photos/reserved-sign-on-restaurant-table-with-bar-background-picture-id912129754)",
                backgroundRepeat: "no-repeat",
                backgroundSize: "cover",
                backgroundPosition: "center center"
            },
        }
    },
    computed: {
        date() {
            let yyyymmdd = this.message.day;
            yyyymmdd = yyyymmdd.split("-");
            for (let i=0; i<yyyymmdd.length; i++) {
                yyyymmdd[i] = parseInt(yyyymmdd[i], 10);
            }
            return `${yyyymmdd[0]}年${yyyymmdd[1]}月${yyyymmdd[2]}日`; 
        },
        weekday() {
            let yyymmdd = new Date(this.message.day.replace(/-/g, "/"));
            return this.$utils.weekdayName(yyymmdd.getDay());
        }
    },
    created() {
        if (!this.message) {
            this.$router.push("/");
        }
    },
    mounted() {

    },
    methods: {
        /**
         * トップ画面へ遷移
         * 
         */
        top() {
            this.$router.push("/");
        },
    }

}
</script>

<style scoped>
.top {
    color: #00ba00;
    font-size:16px;
}
.message {
    font-size:1.4em;
    color: #fffaf0;
    text-shadow: 2px 3px 3px #263238;
}
.menu {
    font-size: 1.0em;
    font-weight: bold;
}
.reserve-font-size {
    font-size: 16px;
}
@media screen and (max-width:540px) {
    .reserve-font-size {
        font-size: 12px;
    }
}
.card-size {
    width: 96%;
    min-width: 310px;
    max-width: 600px;
    margin: 0 auto 70px auto;
    opacity:0.8;    
}
.footer-height {
    height: 60px;
}
.footer-font-size {
    font-size: 1.4em;    
}
@media screen and (max-height:580px) {
    .card-size {
        margin: 0 auto 70px auto;
    }
    .footer-height {
        height: 60px;
    }
    .footer-font-size {
        font-size: 1.2em;    
    }
}
</style>
