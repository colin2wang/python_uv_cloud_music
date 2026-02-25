# Get Album

## API Call Bash Command use curl
```bash
# Get Album By ID
curl 'https://musicapi.lxchen.cn/Album?id=361790100' \
  -H 'accept: application/json, text/javascript, */*; q=0.01' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'priority: u=1, i' \
  -H 'referer: https://musicapi.lxchen.cn/' \
  -H 'sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' \
  -H 'x-requested-with: XMLHttpRequest'
```
## API Response
```json
{
    "data": {
        "album": {
            "artist": "\u8c2d\u7ef4\u7ef4",
            "coverImgUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300",
            "description": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u7531\u4e2d\u592e\u5e7f\u64ad\u7535\u89c6\u603b\u53f0\u3001\u6b63\u5348\u9633\u5149\u3001\u7231\u5947\u827a\u3001\u4e2d\u56fd\u7535\u89c6\u5267\u5236\u4f5c\u4e2d\u5fc3\u51fa\u54c1\u3001\u9ad8\u6ee1\u5802\u4efb\u603b\u7b56\u5212\uff0c\u738b\u4e09\u6bdb\u3001\u78ca\u5b50\u521d\u7a3f\u7f16\u5267\uff0c\u8096\u610f\u51e1\u3001\u9ec4\u51ef\u6587\u3001\u674e\u96ea\u3001\u8d75\u70c1\u3001\u5218\u5c0f\u6eaa\u7f16\u5267\uff0c\u674e\u96ea\u6267\u5bfc\uff0c\u8d75\u70c1\u62c5\u4efb\u5206\u7ec4\u5bfc\u6f14\uff0c\u4faf\u9e3f\u4eae\u4efb\u603b\u5236\u7247\u4eba\uff0c\u8d75\u5b50\u715c\u4efb\u5236\u7247\u4eba\u7684\u73b0\u5b9e\u4e3b\u4e49\u9898\u6750\u7684\u5267\u96c6\u3002\n\u8be5\u5267\u7531\u6768\u7d2b\u9886\u8854\u4e3b\u6f14\uff0c\u80e1\u6b4c\u7279\u522b\u51fa\u6f14\uff0c\u674e\u5149\u6d01\u3001\u5f20\u54f2\u534e\u9886\u8854\u4e3b\u6f14\uff0c\u6885\u5a77\u3001\u8881\u5f18\u3001\u6768\u70c1\u3001\u5468\u6e38\u53cb\u60c5\u51fa\u6f14\uff0c\u91d1\u5df4\u3001\u51af\u5175\u3001\u66f4\u65e6\u3001\u82cf\u946b\u3001\u5b8b\u695a\u708e\u3001\u5468\u653e\u3001\u5468\u601d\u7fbd\u3001\u7d22\u6717\u65fa\u59c6\u5171\u540c\u4e3b\u6f14\uff0c\u8bb2\u8ff0\u4e86\u6ee1\u8154\u70ed\u8840\u7684\u5de1\u5c71\u961f\u65b0\u4eba\u767d\u83ca\uff08\u6768\u7d2b \u9970\uff09\uff0c\u5728\u4fe1\u5ff5\u575a\u5b9a\u7684\u961f\u957f\u591a\u6770\uff08\u80e1\u6b4c \u9970\uff09\u7684\u5e26\u9886\u4e0b\u4e0e\u961f\u5458\u4eec\u4e0d\u60e7\u8270\u9669\u6253\u51fb\u72af\u7f6a\u7684\u6545\u4e8b\uff0c\u5176\u80cc\u540e\u4e5f\u6298\u5c04\u51fa\u66fe\u7ecf\u4e00\u4ee3\u4ee3\u5de1\u5c71\u4eba\u4ece\u672a\u5c06\u73af\u5883\u4fdd\u62a4\u8ba9\u6b65\u4e8e\u7ecf\u6d4e\u53d1\u5c55\u7684\u4fe1\u4ef0\u63a5\u529b\u3002\n\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u540c\u540d\u4e3b\u9898\u66f2\u7531\u674e\u66a8\u9752\u4f5c\u8bcd\uff0c\u6bb5\u70bc\u4f5c\u66f2\uff0c\u6b4c\u624b\u8c2d\u7ef4\u7ef4\u6f14\u5531\u3002\u6b4c\u66f2\u4ee5\u60a0\u8fdc\u6292\u60c5\u7684\u65cb\u5f8b\u52fe\u52d2\u51fa\u535a\u62c9\u6728\u62c9\u8fd9\u7247\u571f\u5730\u4e0a\u7684\u751f\u547d\u53f2\u8bd7\uff0c\u501f\u98ce\u3001\u96ea\u3001\u9633\u5149\u4e0e\u6811\u6728\u7b49\u610f\u8c61\uff0c\u541f\u5531\u751f\u547d\u575a\u97e7\u4e0e\u6545\u571f\u6df1\u60c5\uff0c\u55bb\u793a\u751f\u547d\u5982\u6811\u6839\u6df1\u624e\u8352\u91ce\uff0c\u987d\u5f3a\u751f\u957f\uff0c\u8be0\u91ca\u4e86\u751f\u547d\u4e0e\u571f\u5730\u4e4b\u95f4\u751f\u751f\u4e0d\u606f\u7684\u7cbe\u795e\u8054\u7ed3\u3002\n\u300a\u751f\u547d\u6811\u300b\u5f71\u89c6\u539f\u58f0\u4e13\u8f91\u914d\u4e50\u7531\u97f3\u4e50\u4eba\u6bb5\u70bc\u5320\u5fc3\u6253\u9020\uff0c\u539f\u58f0\u65cb\u5f8b\u5728\u82cd\u51c9\u4e0e\u70bd\u70ed\u95f4\u5f80\u590d\uff0c\u5199\u5c3d\u5b88\u62a4\u8005\u7684\u70ed\u8840\u4e0e\u6e29\u67d4\uff0c\u9053\u7834\u81ea\u7136\u4e0e\u751f\u547d\u7684\u5171\u751f\u8f6e\u56de\u3002\u6bcf\u4e00\u6bb5\u65cb\u5f8b\u90fd\u662f\u4e00\u68f5\u6811\u7684\u751f\u957f\uff0c\u6bcf\u4e00\u6b21\u541f\u5531\u90fd\u662f\u4e00\u7247\u571f\u5730\u7684\u56de\u54cd\u3002\u5f53\u97f3\u4e50\u968f\u5f71\u7247\u800c\u8d77\uff0c\u4f60\u542c\u89c1\u7684\u4e0d\u53ea\u662f\u5267\u60c5\uff0c\u662f\u98ce\u8fc7\u8352\u539f\u3001\u662f\u751f\u7075\u547c\u5438\uff0c\u662f\u751f\u751f\u4e0d\u606f\u7684\u751f\u547d\u4e4b\u6811\u3002\u6bcf\u4e00\u5904\u60c5\u7eea\u8d77\u4f0f\uff0c\u90fd\u5bf9\u5e94\u7740\u89d2\u8272\u7684\u6323\u624e\u4e0e\u575a\u5b88\uff1b\u4f5c\u8005\u7528\u97f3\u4e50\u52fe\u52d2\u51fa\u5927\u5730\u7684\u547c\u5438\uff0c\u8ba9\u4eba\u7269\u7684\u60c5\u611f\u624e\u6839\u4e8e\u5c71\u5ddd\u4e4b\u95f4\uff0c\u8ba9\u81ea\u7136\u7684\u7075\u97f5\u6ce8\u5165\u6bcf\u4e00\u6bb5\u547d\u8fd0\u4e4b\u4e2d\uff0c\u8ba9\u97f3\u4e50\u65e2\u8868\u73b0\u51fa\u4e86\u76f8\u5bf9\u5e94\u7684\u4e16\u754c\u89c2\uff0c\u4e5f\u80fd\u542c\u5f97\u5230\u4eba\u5fc3\u7684\u611f\u52a8\u3002\n\n\n",
            "id": 361790100,
            "name": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
            "publishTime": 1770825600000,
            "songs": [
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u8c2d\u7ef4\u7ef4",
                    "id": 3346362708,
                    "name": "\u751f\u547d\u6811",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348978482,
                    "name": "\u8352\u539f\u60b2\u6b4c",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976126,
                    "name": "\u5b64\u9014",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976114,
                    "name": "\u8352\u539f\u56de\u54cd",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976108,
                    "name": "\u6765\u65f6\u7684\u8def",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976107,
                    "name": "\u5988\u5988\u6765\u4e86",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976106,
                    "name": "\u5c71\u795e\u4f4e\u8bed",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976110,
                    "name": "\u5c71\u795e\u4e4b\u6012",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976112,
                    "name": "\u751f\u547d\u4e4b\u9633",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976115,
                    "name": "\u751f\u751f\u4e0d\u606f",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348975984,
                    "name": "\u5353\u739b\u5f80\u4e8b",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976124,
                    "name": "\u201c\u79cb\u5929\u201d",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976127,
                    "name": "\u201c\u8fd9\u68f5\u6811\u957f\u5728\u4eba\u5fc3\u91cc\u201d",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976125,
                    "name": "\u5927\u5730\u4e4b\u8109",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976133,
                    "name": "\u6de1\u84dd\u8272\u7684\u98ce",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976123,
                    "name": "\u6076",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976131,
                    "name": "\u98ce\u8bb0\u5f97\u4f60\u7684\u6a21\u6837",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976128,
                    "name": "\u544a\u522b",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976113,
                    "name": "\u5f52\u9014\u6709\u706f",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976109,
                    "name": "\u91d1\u77ff\u4e00\u6218",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976111,
                    "name": "\u5988\u5988\u7684\u6127\u759a",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974365,
                    "name": "\u4e00\u7f15\u6696\u9633",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974358,
                    "name": "\u751f\u4e4b\u60b2\u9e23",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974368,
                    "name": "\u5b88\u671b",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974359,
                    "name": "\u4e07\u7075\u540c\u60b2",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974362,
                    "name": "\u5fae\u5149\u5165\u6000",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974366,
                    "name": "\u5fc3\u5411\u8352\u539f",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974360,
                    "name": "\u5fc3\u6709\u70ed\u671b\uff0c\u4fbf\u4e0d\u60e7\u8352\u51c9",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974361,
                    "name": "\u661f\u661f\u5728\u95ea\u8000",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974364,
                    "name": "\u4e00\u58f0\u7275\u6302\uff0c\u4e00\u751f\u6e29\u6696",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348975985,
                    "name": "\u6709\u5bb6\uff0c\u5c31\u6709\u5f52\u5904",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974367,
                    "name": "\u4e07\u7269\u751f\u957f",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348974363,
                    "name": "\u5de1\u5c71\u961f",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976130,
                    "name": "\u628a\u6e29\u67d4\u7559\u7ed9\u8eab\u8fb9\u4eba",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976132,
                    "name": "\u591a\u6770\u4e0e\u8fdc\u65b9",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                },
                {
                    "album": "\u7535\u89c6\u5267\u300a\u751f\u547d\u6811\u300b\u539f\u58f0\u5e26",
                    "artists": "\u6bb5\u70bc",
                    "id": 3348976129,
                    "name": "\u98ce\u4f1a\u8bb0\u5f97\u6bcf\u4e00\u6735\u82b1",
                    "picUrl": "https://p3.music.126.net/xxmzLjUaMNmW38vSHVKyIQ==/109951172731543933.jpg?param=300y300"
                }
            ]
        },
        "status": 200
    },
    "message": "\u83b7\u53d6\u4e13\u8f91\u8be6\u60c5\u6210\u529f",
    "status": 200,
    "success": true
}
```