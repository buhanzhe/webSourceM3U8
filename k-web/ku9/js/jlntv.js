function main(item) {
    var id = item.id || 'jlws';

    var channelMap = {
        jlws: '吉林卫视',
        ds:   '都市频道',
        sh:   '生活频道',
        ys:   '影视频道',
        xc:   '乡村频道',
        zy:   '综艺·文化频道',
        cc:   '长春综合'
    };

    // 也允许直接传中文频道名称
    var channelName = channelMap[id] || id;

    var pageUrl = 'https://www.jlntv.cn/tv?id=104';

    var headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) ' +
            'Chrome/116.0.0.0 Safari/537.36'
    };

    // 防止频道名中出现引号导致 JS 出错
    var target = JSON.stringify(channelName);

    var jscode =
        "(function(){" +
        "var TARGET=" + target + ";" +
        "var startTime=Date.now();" +

        "function trimText(s){" +
            "return String(s||'').replace(/\\s+/g,'').trim();" +
        "}" +

        "function findChannel(){" +
            "var nodes=document.querySelectorAll('a,button,li,span,div');" +
            "var target=trimText(TARGET);" +

            "for(var i=0;i<nodes.length;i++){" +
                "var el=nodes[i];" +
                "var text=trimText(el.textContent||el.innerText||'');" +

                "if(text===target){" +
                    "if(el.tagName==='A'||el.tagName==='BUTTON'){" +
                        "return el;" +
                    "}" +

                    "var a=el.querySelector?el.querySelector('a'):null;" +
                    "if(a && trimText(a.textContent||a.innerText||'')===target){" +
                        "return a;" +
                    "}" +

                    "if(el.onclick){" +
                        "return el;" +
                    "}" +
                "}" +
            "}" +

            "return null;" +
        "}" +

        "function doClick(el){" +
            "try{" +
                "el.click();" +
                "return;" +
            "}catch(e){}" +

            "try{" +
                "var evt=document.createEvent('MouseEvents');" +
                "evt.initMouseEvent(" +
                    "'click',true,true,window,1," +
                    "0,0,0,0,false,false,false,false,0,null" +
                ");" +
                "el.dispatchEvent(evt);" +
            "}catch(e){}" +
        "}" +

        "function setupVideo(){" +
            "var video=document.querySelector('video');" +
            "if(!video)return false;" +

            "document.documentElement.style.background='#000';" +
            "document.body.style.background='#000';" +
            "document.body.style.margin='0';" +
            "document.body.style.padding='0';" +
            "document.body.style.overflow='hidden';" +

            "video.style.position='fixed';" +
            "video.style.left='0';" +
            "video.style.top='0';" +
            "video.style.width='100vw';" +
            "video.style.height='100vh';" +
            "video.style.objectFit='contain';" +
            "video.style.background='#000';" +
            "video.style.zIndex='2147483647';" +

            "video.muted=false;" +
            "video.volume=1;" +
            "video.autoplay=true;" +
            "video.controls=false;" +

            "try{video.play();}catch(e){}" +

            "return true;" +
        "}" +

        "var clicked=(TARGET==='吉林卫视');" +

        "var timer=setInterval(function(){" +

            "if(!clicked){" +
                "var channel=findChannel();" +

                "if(channel){" +
                    "clicked=true;" +
                    "doClick(channel);" +
                "}" +
            "}else{" +
                "setupVideo();" +
            "}" +

            "if(Date.now()-startTime>20000){" +
                "clearInterval(timer);" +
            "}" +

        "},300);" +

        "})();";

    return {
        webview: pageUrl,
        headers: headers,
        jscode: jscode
    };
}
