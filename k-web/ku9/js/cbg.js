/*
 * 重庆广电 / 视界网 Ku9 JS
 * NativeWasmTv
 *
 * 用法：
 * cbg.js?id=https://sj.cbg.cn/wap/list/4918/1.html
 */

function findM3u8(text) {
    if (!text) {
        return "";
    }

    text = String(text)
        .replace(/\\u002f/gi, "/")
        .replace(/\\u003a/gi, ":")
        .replace(/\\u003f/gi, "?")
        .replace(/\\u003d/gi, "=")
        .replace(/\\u0026/gi, "&")
        .replace(/\\\//g, "/")
        .replace(/&amp;/g, "&");

    var m = text.match(
        /https?:\/\/[^"'<> \r\n]+?\.m3u8(?:\?[^"'<> \r\n]*)?/i
    );

    return m ? m[0] : "";
}


function main(item) {

    var scriptUrl = item && item.url ? String(item.url) : "";

    var pageUrl = ku9.getQuery(scriptUrl, "id");

    if (!pageUrl) {
        pageUrl =
            "https://sj.cbg.cn/wap/list/4918/1.html";
    }


    /*
     * 先尝试直接扫描网页。
     * 如果以后 CBG 又把 m3u8 放回页面，这里可以直接命中。
     */
    try {

        var html = ku9.get(pageUrl, {
            "Referer": "https://sj.cbg.cn/",
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                "AppleWebKit/537.36 (KHTML, like Gecko) " +
                "Chrome/120.0.0.0 Safari/537.36"
        });

        var direct = findM3u8(html);

        if (direct) {
            ku9.log("CBG page m3u8: " + direct);

            return {
                url: direct
            };
        }

    } catch (e) {
        ku9.log("CBG page scan failed: " + e);
    }


    /*
     * 重庆卫视官方基础直播地址。
     *
     * CBG 的 getLiveUrl 接口会给基础 URL
     * 增加类似：
     *
     * /202608xxxxxx/
     *
     * 的路径。
     */
    var base =
        "https://sjlivecdn9.cbg.cn/" +
        "app_2/_definst_/ls_2.stream/chunklist.m3u8";

    var api =
        "https://web.cbg.cn/live/getLiveUrl?url=" +
        encodeURIComponent(base);


    /*
     * 使用 request 而不是单纯 get，
     * 这样同时可以获取最终 URL / HTTP Body。
     */
    try {

        var r = ku9.request(
            api,
            "GET",
            {
                "Referer": "https://web.cbg.cn/",
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                    "AppleWebKit/537.36 (KHTML, like Gecko) " +
                    "Chrome/120.0.0.0 Safari/537.36"
            },
            "",
            true
        );


        /*
         * 有些接口可能直接 302 到真正地址。
         */
        var url = findM3u8(r.url);

        if (url) {
            ku9.log("CBG redirect m3u8: " + url);

            return {
                url: url
            };
        }


        /*
         * 也可能 JSON / 文本返回地址。
         */
        url = findM3u8(r.body);

        if (url) {
            ku9.log("CBG api m3u8: " + url);

            return {
                url: url
            };
        }

    } catch (e) {
        ku9.log("CBG getLiveUrl failed: " + e);
    }


    /*
     * 最后兜底。
     *
     * 当前公开源中仍在使用这个 CBG 官方 CDN 地址。
     */
    return {
        url:
            "https://sjlivecdn9.cbg.cn/" +
            "204912315959/" +
            "app_2/_definst_/ls_2.stream/chunklist.m3u8"
    };
}
