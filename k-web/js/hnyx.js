function main(item) {
    const url = item.url;
    const id = ku9.getQuery(url, "id");
    const dur = parseFloat(ku9.getQuery(url, "dur"));
    const offset = parseInt(ku9.getQuery(url, "offset"));
    if (!id) {
        console.log("Error id");
        return { url: "" };
    }
    if (!dur || isNaN(dur) || dur <= 0) {
        console.log("Error");
        return { url: "" };
    }
    if (offset === undefined || isNaN(offset)) {
        console.log("Error");
        return { url: "" };
    }
    const now = Math.floor(Date.now() / 1000);
    const start = Math.floor(now / dur - offset) - 4;
    let m3u8 = "#EXTM3U\n";
    m3u8 += "#EXT-X-VERSION:3\n";
    m3u8 += "#EXT-X-TARGETDURATION:" + (Math.floor(dur) + 1) + "\n";
    m3u8 += "#EXT-X-MEDIA-SEQUENCE:" + start + "\n";
    for (let i = 0; i < 3; i++) {
        const seq = start + i;
        m3u8 += "#EXTINF:" + dur + ",\n";
        m3u8 += "http://[2409:8c6a:b021:3901::28]/c1.cdn.hunancatv.com/live/" + id + "-" + seq + "-1-hls.ts\n";
    }
    if (id === "CCTV_4K") {
        return { m3u8: m3u8, player: 1 };
    }
    return { m3u8: m3u8 };
}
