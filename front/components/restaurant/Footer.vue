<template>
    <v-footer fixed class="elevation-3" style="width:100%;">
        <v-col class="pa-0" color="grey lighten-5">
            <v-btn outlined class="footer-back btn-xs-only" style="text-transform:none;" v-on:click="back(1)" v-show="icons>0">
                <span class="footer-font-size">Top</span>
            </v-btn>
            <v-btn outlined class="footer-back btn-xs-only" v-on:click="back(2)" v-show="icons>1">
                <v-icon>mdi-store</v-icon>
                <span class="footer-font-size" style="text-transform:none;">{{ $t("footer.shop") }}<span class="hidden-xs-only">{{ $t("footer.selection") }}</span></span>
            </v-btn>
            <v-btn outlined class="footer-back btn-xs-only" v-on:click="back(3)" v-show="icons>2">
                <v-icon>mdi-calendar</v-icon>
                <span class="footer-font-size" style="text-transform:none;">&nbsp;{{ $t("footer.day") }}<span class="hidden-xs-only">{{ $t("footer.selection") }}</span></span>
            </v-btn>
        </v-col>           
    </v-footer>
</template>

<script>
/**
 * レストランフッター
 * 
 */
export default {
    props: {
        icons: {
            type: [String, Number],
            required: true,
            default: 0,
        },
    },
    data() {
        return {

        }
    },
    methods: {
        /**
         * 画面遷移処理
         * 
         * @param {number} icon アイコンボタン番号
         */
        back(icon) {
            switch (icon) {
            case 1:
                this.$router.push("/");
                break;
            case 2:
                this.$router.push("/restaurant/areas");
                break;
            case 3:
                this.$nuxt.$emit("dialog", false);
                break;
            }
        }
    }
}
</script>

<style scoped>
.footer-back {
    cursor: pointer;
    color: #4C4C4C;
    font-weight: normal;
}
.footer-font-size {
    font-size: 1.0em;
}
@media screen and (max-width:540px) {
    .footer-font-size {
        font-size: 0.7em;
    }
    .btn-xs-only {
        max-width: 60px;
    }
    .btn-xs-only-staff {
        max-width: 80px;
    }
}

</style>
