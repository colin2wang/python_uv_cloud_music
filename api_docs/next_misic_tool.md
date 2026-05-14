
## Call#1 获取 Key
```bash
curl 'https://nextmusic.toubiec.cn/api/key' \
  -X 'POST' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'content-length: 0' \
  -H 'origin: https://wyapi.toubiec.cn' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
  
# 响应
{
    "code": 200,
    "data": {
        "keyId": "343d6fa3-7238-4a7e-9e00-78b47228144c",
        "keyToken": "f3377da5-e8f1-42b5-9803-5c83fba59406",
        "key": "K1y+dWroyYOKjb885yHoHZN0USTG/hwrztc57nzDd5o="
    }
}
```

## Call#2 OPTION getSongUrl
```bash
curl 'https://nextmusic.toubiec.cn/api/getSongUrl' \
  -X 'OPTIONS' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'access-control-request-headers: content-type' \
  -H 'access-control-request-method: POST' \
  -H 'origin: https://wyapi.toubiec.cn' \
  -H 'priority: u=1, i' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
```

## Call#3 POST getSongUrl
```bash
curl 'https://nextmusic.toubiec.cn/api/getSongUrl' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'content-type: application/json' \
  -H 'origin: https://wyapi.toubiec.cn' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"keyId":"343d6fa3-7238-4a7e-9e00-78b47228144c","keyToken":"f3377da5-e8f1-42b5-9803-5c83fba59406","data":"IbrEVoGs6x74aGDe.hfZm4LjTdRIG+yyQ2iCmbg==.pp5PYs8cogvf1GSqgN3fXiBl7d6LotZjkjMBKNBbyKwXRR203RdPAyBiYwrBmPEuhENkZjuYy/y3GGfGdBi2gg=="}'
```

## Call#4 POST getSongLyric
```bash
curl 'https://nextmusic.toubiec.cn/api/getSongLyric' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'content-type: application/json' \
  -H 'origin: https://wyapi.toubiec.cn' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
  --data-raw '{"keyId":"89c4fb39-c3ea-449b-b750-95e947bde389","keyToken":"6291b52c-3b39-42a2-91ee-4c3757441288","data":"bQwk2qFKipdoh6b8.rbqW46swu/NnBduG5ZmOoQ==.bqZGrPkXUwD3C8Jo7aDvLH1Txki/NQkRBh7/w2J5J62VeyRVp2x1MQSiratn"}'

# 响应示例（解密后）
{
    "code": 200,
    "data": {
        "lrc": "[00:00.000] 作词 : ...\n[00:01.000] 作曲 : ...",
        "tlyric": "",
        "romalrc": "",
        "klyric": ""
    }
}
```

## 方法 单曲逻辑
```javascript
else if (o === `single`) {
                c.requestUrl = `https://nextmusic.toubiec.cn/api/getSongInfo`,
                c.requestBody = {
                    id: s
                };
                let {response: e, data: t} = await he(c.requestUrl, c.requestBody);
                if (c.responseStatus = e.status,
                c.responseData = t,
                t && t.code === 429)
                    throw Error(t.message || `当前IP请求频率过快，请稍后再试`);
                if (!t || t.code !== 200 || !t.data)
                    throw Error(t.message || `未找到该歌曲信息`);
                if (t.data.copyright === 0 && t.data.copyrightId === 0)
                    throw Error(`该歌曲可能存在版权问题，无法提供下载和播放链接`);
                let n = t.data
                  , {data: r} = await he(`https://nextmusic.toubiec.cn/api/getSongUrl`, {
                    id: s,
                    level: f
                });
                if (r && r.code === 429)
                    throw Error(r.message || `当前IP请求频率过快，请稍后再试`);
                if (!r || r.code !== 200 || !r.data || !r.data.url)
                    throw Error(r.message || `无法获取该歌曲的播放链接！`);
                let a = r.data
                  , o = ``;
                try {
                    let {data: e} = await he(`https://nextmusic.toubiec.cn/api/getSongLyric`, {
                        id: s
                    });
                    if (e && e.code === 429)
                        throw Error(e.message || `当前IP请求频率过快，请稍后再试`);
                    e && e.code === 200 && e.data && (o = xe(e.data.lrc || ``, e.data.tlyric || ``))
                } catch (e) {
                    console.warn(`获取歌词失败，忽略歌词展示`, e)
                }
                let u = n.picimg ? n.picimg.replace(/`/g, ``).trim() : ``;
                u && u.includes(`music.126.net`) && (u = u.split(`?`)[0] + `?param=200y200`);
                let d = a.url ? a.url.replace(/`/g, ``).trim() : ``
                  , p = a.size ? (a.size / (1024 * 1024)).toFixed(2) + ` MB` : `未知大小`
                  , m = {
                    type: `single`,
                    id: s,
                    name: n.name || `未知歌曲`,
                    artist: n.singer || `未知歌手`,
                    album: n.album || `未知专辑`,
                    duration: n.duration || a.duration || `未知时长`,
                    size: p,
                    cover: u,
                    audioUrl: d,
                    lrc: o,
                    quality: me.find(e => e.value === (a.level || f))?.label || a.level || `未知音质`
                };
                i ? (E(m),
                setTimeout( () => {
                    let e = document.getElementById(`nested-single-result`);
                    e && e.scrollIntoView({
                        behavior: `smooth`,
                        block: `center`
                    })
                }
                , 100)) : l(m),
                ZA.success(`解析成功`),
                R(e => {
                    let t = n.name || `未知歌曲`
                      , r = {
                        id: s,
                        name: t
                    }
                      , i = (e.single || []).filter(e => e.name !== t);
                    return {
                        ...e,
                        single: [r, ...i].slice(0, 10)
                    }
                }
                )
            }
```

## 方法 he

```javascript
let he = async (e, t) => {
        try {
            let {key: n, keyId: r, keyToken: i} = await _B()
              , a = await hB({
                ...t,
                timestamp: Date.now()
            }, n)
              , o = await fetch(e, {
                method: `POST`,
                headers: {
                    "Content-Type": `application/json`
                },
                body: JSON.stringify({
                    keyId: r,
                    keyToken: i,
                    data: a
                })
            })
              , s = await o.json();
            if (s.ciphertext) {
                let e = await gB(s.ciphertext, n);
                if (!e)
                    throw Error(`响应数据解密失败`);
                return {
                    response: o,
                    data: e
                }
            }
            return {
                response: o,
                data: s
            }
        } catch (e) {
            throw Error(`请求接口失败: ${e.message}`)
        }
    }
```

## 可能是加密解密方法
```javascript
var Hb = v.forwardRef( (e, t) => v.createElement(bo, Vb({}, e, {
    ref: t,
    icon: Bb
})))
  , Ub = {
    icon: {
        tag: `svg`,
        attrs: {
            viewBox: `64 64 896 896`,
            focusable: `false`
        },
        children: [{
            tag: `path`,
            attrs: {
                d: `M884 256h-75c-5.1 0-9.9 2.5-12.9 6.6L512 654.2 227.9 262.6c-3-4.1-7.8-6.6-12.9-6.6h-75c-6.5 0-10.3 7.4-6.5 12.7l352.6 486.1c12.8 17.6 39 17.6 51.7 0l352.6-486.1c3.9-5.3.1-12.7-6.4-12.7z`
            }
        }]
    },
    name: `down`,
    theme: `outlined`
};

 fB = e => {
    let t = ``
      , n = new Uint8Array(e)
      , r = n.byteLength;
    for (let e = 0; e < r; e++)
        t += String.fromCharCode(n[e]);
    return window.btoa(t)
}
  , pB = e => {
    let t = window.atob(e)
      , n = t.length
      , r = new Uint8Array(n);
    for (let e = 0; e < n; e++)
        r[e] = t.charCodeAt(e);
    return r.buffer
}
  , mB = async e => {
    let t = pB(e);
    return await window.crypto.subtle.importKey(`raw`, t, {
        name: `AES-GCM`
    }, !1, [`encrypt`, `decrypt`])
}
  , hB = async (e, t) => {
    let n = await mB(t)
      , r = window.crypto.getRandomValues(new Uint8Array(12))
      , i = new TextEncoder().encode(JSON.stringify(e))
      , a = await window.crypto.subtle.encrypt({
        name: `AES-GCM`,
        iv: r
    }, n, i)
      , o = new Uint8Array(a)
      , s = o.slice(0, o.length - 16)
      , c = o.slice(o.length - 16);
    return `${fB(r)}.${fB(c)}.${fB(s)}`
}
  , gB = async (e, t) => {
    try {
        let n = await mB(t)
          , [r,i,a] = e.split(`.`)
          , o = pB(r)
          , s = new Uint8Array(pB(i))
          , c = new Uint8Array(pB(a))
          , l = new Uint8Array(c.length + s.length);
        l.set(c, 0),
        l.set(s, c.length);
        let u = await window.crypto.subtle.decrypt({
            name: `AES-GCM`,
            iv: new Uint8Array(o)
        }, n, l);
        return JSON.parse(new TextDecoder().decode(u))
    } catch (e) {
        return console.error(`Failed to decrypt response:`, e.message),
        null
    }
}
  , _B = async () => {
    let e = await fetch(`https://nextmusic.toubiec.cn/api/key`, {
        method: `POST`
    })
      , t = await e.json();
    if (!e.ok || t.code !== 200 || !t.data)
        throw Error(`获取加密会话失败`);
    return t.data
}
  , vB = () => {
    let[e,t] = (0,
    v.useState)(!1)
      , [n,r] = (0,
    v.useState)(!1)
      , [i,a] = (0,
    v.useState)(0)
      , [o,s] = (0,
    v.useState)(``)
      , [c,l] = (0,
    v.useState)(null)
      , [u,d] = (0,
    v.useState)(``)
      , [f,p] = (0,
    v.useState)(`standard`)
      , [m,h] = (0,
    v.useState)(!1)
      , [g,_] = (0,
    v.useState)(`changelog`)
      , [y,b] = (0,
    v.useState)(!1)
      , [x,S] = (0,
    v.useState)(`single`)
      , [C,w] = (0,
    v.useState)(`alipay`)
      , [T,E] = (0,
    v.useState)(null)
      , [D,O] = (0,
    v.useState)(!1)
      , [k,A] = (0,
    v.useState)( () => localStorage.getItem(`wyy_agreement_agreed`) !== `true`)
      , [j,M] = (0,
    v.useState)(!1)
      , [N,P] = (0,
    v.useState)(!0)
      , [F,I] = (0,
    v.useState)([])
      , [L,R] = (0,
    v.useState)( () => {
        try {
            let e = localStorage.getItem(`wyy_historyList`);
            if (e) {
                let t = JSON.parse(e);
                return Array.isArray(t) ? {
                    single: t,
                    album: [],
                    playlist: [],
                    search: []
                } : {
                    single: t.single || [],
                    album: t.album || [],
                    playlist: t.playlist || [],
                    search: t.search || []
                }
            }
            return {
                single: [],
                album: [],
                playlist: [],
                search: []
            }
        } catch {
            return {
                single: [],
                album: [],
                playlist: [],
                search: []
            }
        }
    }
```