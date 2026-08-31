/**
 * 根据凤凰网直播 ID 获取真实视频播放地址
 * @param {string} videoId
 * @returns {Promise<string|null>}
 */
async function getVideoUrl(videoId) {
    if (!videoId) {
        return null;
    }

    const targetUrl = `https://flive.ifeng.com/live/${videoId}.html`;

    try {
        const response = await fetch(targetUrl, {
            method: "GET",
            headers: {
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                    "AppleWebKit/537.36 (KHTML, like Gecko) " +
                    "Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://jx.ifeng.com/zhibo"
            }
        });

        if (!response.ok) {
            console.log("请求失败:", response.status);
            return null;
        }

        const htmlContent = await response.text();

        let match;

        // 1. 优先匹配 url: "xxx.mp4"
        match = htmlContent.match(
            /["']url["']\s*:\s*["'](https?:\/\/[^"']+\.mp4)["']/
        );

        if (match) {
            return match[1];
        }

        // 2. 任意 mp4 地址
        match = htmlContent.match(
            /(https?:\/\/[^\s"'<>]+\.mp4)/
        );

        if (match) {
            return match[1];
        }

        // 3. 匹配 url: "xxx.m3u8"
        match = htmlContent.match(
            /["']url["']\s*:\s*["'](https?:\/\/[^"']+\.m3u8)["']/
        );

        if (match) {
            return match[1];
        }

        // 4. 任意 m3u8 地址
        match = htmlContent.match(
            /(https?:\/\/[^\s"'<>]+\.m3u8)/
        );

        if (match) {
            return match[1];
        }

        return null;

    } catch (e) {
        console.log("请求出错:", e);
        return null;
    }
}


/**
 * 酷9入口
 * 支持：
 * 1016529
 * https://xxx.com/xxx?id=1016529
 */
async function main(urlOrId) {
    let videoId = "";

    if (urlOrId.includes("id=")) {
        try {
            const url = new URL(urlOrId);
            videoId = url.searchParams.get("id") || "";
        } catch (e) {
            // URL() 无法解析时使用正则兜底
            const match = urlOrId.match(/[?&]id=([^&#]+)/);

            if (match) {
                videoId = decodeURIComponent(match[1]);
            }
        }
    } else {
        videoId = urlOrId;
    }

    const realUrl = await getVideoUrl(videoId);

    if (realUrl) {
        return realUrl;
    }

    return "Error: 未找到视频";
}


// 测试
(async () => {
    const result = await main("1016529");
    console.log("解析结果:", result);
})();
