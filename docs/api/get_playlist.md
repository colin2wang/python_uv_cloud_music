# Get Album

## API Call Bash Command use curl
```bash
# Get Playlist By ID
curl 'https://musicapi.lxchen.cn/Playlist?id=331841455' \
  -H 'authority: musicapi.lxchen.cn' \
  -H 'accept: application/json, text/javascript, */*; q=0.01' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'referer: https://musicapi.lxchen.cn/' \
  -H 'sec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36' \
  -H 'x-requested-with: XMLHttpRequest'
```
## API Response
```json
{
    "data": {
        "playlist": {
            "coverImgUrl": "https://p1.music.126.net/g2_Gv0dtAicJ3ChTYu28_g==/1393081239628722.jpg",
            "creator": "\u97f3\u65e7-",
            "description": "\u597d\u5e0c\u671b\u8fd9\u91cc\u53ef\u4ee5\u6210\u4e3a\u5927\u5bb6\u7684\u4e00\u4e2a\u5e87\u62a4\u6240\n\u5728\u6df1\u591c\u5b89\u5b89\u9759\u9759\u4e0d\u5435\u4e0d\u95f9\n\u8def\u8fc7\u7684\u670b\u53cb\u7559\u4e0b\u4e00\u4e2a\u6545\u4e8b\u6216\u6c89\u9ed8\n\u5927\u5bb6\u90fd\u5f7c\u6b64\u9ed8\u5951\n\u7b49\u5f85\u5929\u660e\u3002\n\n\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\n\n\u5355\u4e3b\u4f1a\u5c06\u5e73\u65f6\u542c\u5230\u7684\u4e00\u4e9b\u5c0f\u4f17\u7684\u3001\u8282\u594f\u975e\u5e38\u8212\u7f13\u7684\u3001\u9002\u5408\u7761\u7720\u3001\u51a5\u60f3\u3001\u5199\u4f5c\u3001\u601d\u8003\u7684\u97f3\u4e50\u6536\u5f55\u8fdb\u6765\uff0c\u5982\u8fd9\u4e2a\u6b4c\u5355\u91cc\u7684\u300c\u677e\u7530\u5149\u7531\u3001\u5c0f\u6fd1\u6751\u6676\u3001\u03b1\u00b7Pav\u3001Endless Melancholy\u3001hideyuki hashimoto\u2026\u2026 \u300d\u4ed6\u4eec\u7684\u66f2\u5b50\u3002\n\n\u6bcf\u4e00\u9996\u66f2\u5b50\u90fd\u662f\u7531\u5355\u4e3b\u7cbe\u5fc3\u6311\u9009\u5e76\u4eb2\u81ea\u201c\u8bd5\u7761\u201d\u7684\u52a9\u7720\u6b4c\u66f2\uff0c\u7761\u4e0d\u7740\u7684\u65f6\u5019\u53ef\u4ee5\u7528\u6765\u5e73\u590d\u5fc3\u7eea\uff1b\u5982\u679c\u5931\u7720\u5f88\u4e25\u91cd\u7684\u8bdd\uff0c\u4e0d\u8981\u6025\u8e81\uff0c\u95ed\u4e0a\u773c\u775b\u6df1\u547c\u5438\uff0c\u653e\u677e\u8eab\u4f53\uff0c\u544a\u8bc9\u81ea\u5df1\u201c\u5373\u4f7f\u6ca1\u6709\u7761\u7740\u4e5f\u6ca1\u6709\u5173\u7cfb\u7684\u201d\uff0c\u56e0\u4e3a\u95ed\u4e0a\u773c\u775b\u653e\u677e\u4e5f\u662f\u4e00\u79cd\u4f11\u606f\u3002\n\n\u672c\u6b4c\u5355\u6301\u7eed\u66f4\u65b0\uff0c\u4f46\u662f\u7f13\u6162\uff0c\u56e0\u4e3a\u5355\u4e3b\u60f3\u4fdd\u8bc1\u6b4c\u5355\u8d28\u91cf\uff0c\u5e76\u628a\u771f\u6b63\u9002\u5408\u7684\u6b4c\u66f2\u6536\u5f55\u8fdb\u6765\uff0c\u5e0c\u671b\u4e0d\u7ba1\u662f\u5931\u7720\u8fd8\u662f\u7761\u7720\uff0c\u8fd9\u4e2a\u6b4c\u5355\u90fd\u53ef\u4ee5\u4e00\u76f4\u966a\u4f34\u7740\u4f60\uff0c\u8c22\u8c22\u559c\u6b22\u8fd9\u4e2a\u6b4c\u5355\u7684\u4f60\u4eec\u3002\n\n\u665a\u5b89\u5440\uff5e",
            "id": 331841455,
            "name": "\u6df1\u5ea6\u7761\u7720 |\u91cd\u5ea6\u5931\u7720\u8005\u4e13\u7528\u6b4c\u5355",
            "trackCount": 32,
            "tracks": [
                {
                    "album": "small sketch",
                    "artists": "\u677e\u7530\u5149\u7531",
                    "id": 475541,
                    "name": "breeze",
                    "picUrl": "https://p3.music.126.net/q2MThVM6v1sDJeH0xfUk7A==/109951169477358077.jpg"
                },
                {
                    "album": "small sketch",
                    "artists": "\u677e\u7530\u5149\u7531",
                    "id": 475563,
                    "name": "shizukana umi",
                    "picUrl": "https://p4.music.126.net/q2MThVM6v1sDJeH0xfUk7A==/109951169477358077.jpg"
                },
                {
                    "album": "Before, After",
                    "artists": "Endless Melancholy",
                    "id": 4064247,
                    "name": "A Minute for the Beginning",
                    "picUrl": "https://p4.music.126.net/wPOa5Vy_LveGYQZtyBqemA==/109951168882691005.jpg"
                },
                {
                    "album": "Before, After",
                    "artists": "Endless Melancholy",
                    "id": 4064255,
                    "name": "A Minute for the End",
                    "picUrl": "https://p3.music.126.net/wPOa5Vy_LveGYQZtyBqemA==/109951168882691005.jpg"
                },
                {
                    "album": "Hooray! for Happiness",
                    "artists": "The Last Dinosaur",
                    "id": 19498811,
                    "name": "Gusts of Wind Blowing in Different Directions",
                    "picUrl": "https://p4.music.126.net/f3exPjEKfsnrQbsUqUlb2w==/109951169557730207.jpg"
                },
                {
                    "album": "Buddhists",
                    "artists": "\u5c0f\u702c\u6751\u6676",
                    "id": 408140418,
                    "name": "Buddhists",
                    "picUrl": "https://p3.music.126.net/sWKJq9g9b07jrXlEu0DjZA==/1398578794113206.jpg"
                },
                {
                    "album": "Music for Quiet Mornings",
                    "artists": "Endless Melancholy",
                    "id": 4064273,
                    "name": "Light",
                    "picUrl": "https://p4.music.126.net/h0P7l2e8BKunyiB3RhAlXA==/109951164546524803.jpg"
                },
                {
                    "album": "Buddhists",
                    "artists": "\u5c0f\u702c\u6751\u6676",
                    "id": 408140415,
                    "name": "Quiet",
                    "picUrl": "https://p3.music.126.net/sWKJq9g9b07jrXlEu0DjZA==/1398578794113206.jpg"
                },
                {
                    "album": "Music for Quiet Mornings",
                    "artists": "Endless Melancholy",
                    "id": 4064279,
                    "name": "M\u00e9lancolie",
                    "picUrl": "https://p4.music.126.net/h0P7l2e8BKunyiB3RhAlXA==/109951164546524803.jpg"
                },
                {
                    "album": "nunu",
                    "artists": "nunu",
                    "id": 3204370,
                    "name": "wa1c oo",
                    "picUrl": "https://p4.music.126.net/COLKgKg4aKndBtbuUyNl5A==/1798801023047443.jpg"
                },
                {
                    "album": "Piano Solos, Vol. 2",
                    "artists": "Dustin O'Halloran",
                    "id": 17241428,
                    "name": "Opus 37",
                    "picUrl": "https://p4.music.126.net/grpa773EN0oFJWM5BhTqOg==/109951168541949717.jpg"
                },
                {
                    "album": "Catarse",
                    "artists": "Andrei Machado",
                    "id": 28273863,
                    "name": "Sopro seu",
                    "picUrl": "https://p3.music.126.net/FyOt30OsWpaTLu-3_mqbsg==/109951170632639724.jpg"
                },
                {
                    "album": "\u6620\u753b\u300c\u30da\u30bf\u30eb \u30c0\u30f3\u30b9\u300d\u30aa\u30ea\u30b8\u30ca\u30eb\u30fb\u30b5\u30a6\u30f3\u30c9\u30c8\u30e9\u30c3\u30af",
                    "artists": "\u83c5\u91ce\u3088\u3046\u5b50",
                    "id": 26402040,
                    "name": "norway",
                    "picUrl": "https://p3.music.126.net/NXjMDN7CenW5TTlFm243hg==/2322168557919525.jpg"
                },
                {
                    "album": "Music for Quiet Mornings",
                    "artists": "Endless Melancholy",
                    "id": 4064275,
                    "name": "A Song For The Morning Star",
                    "picUrl": "https://p4.music.126.net/h0P7l2e8BKunyiB3RhAlXA==/109951164546524803.jpg"
                },
                {
                    "album": "Music for Quiet Mornings",
                    "artists": "Endless Melancholy",
                    "id": 4064268,
                    "name": "Quiet",
                    "picUrl": "https://p3.music.126.net/h0P7l2e8BKunyiB3RhAlXA==/109951164546524803.jpg"
                },
                {
                    "album": "Pavonis ~ Piano Collection II ~",
                    "artists": "\u03b1\u00b7Pav",
                    "id": 29137872,
                    "name": "\u03b6",
                    "picUrl": "https://p4.music.126.net/U5O4aGdTvcnHSA5HhxLapg==/7937374441937799.jpg"
                },
                {
                    "album": "The Malady Of Elegance",
                    "artists": "Goldmund",
                    "id": 18057492,
                    "name": "Gifts",
                    "picUrl": "https://p4.music.126.net/vwTBDbUbHmDRrAYg6gxxfQ==/109951163439384227.jpg"
                },
                {
                    "album": "Pavonis ~ Piano Collection II ~",
                    "artists": "\u03b1\u00b7Pav",
                    "id": 29137869,
                    "name": "\u03b2",
                    "picUrl": "https://p4.music.126.net/U5O4aGdTvcnHSA5HhxLapg==/7937374441937799.jpg"
                },
                {
                    "album": "Music for Quiet Mornings",
                    "artists": "Endless Melancholy",
                    "id": 4064267,
                    "name": "Silent Dawn, Grey Twilight",
                    "picUrl": "https://p3.music.126.net/h0P7l2e8BKunyiB3RhAlXA==/109951164546524803.jpg"
                },
                {
                    "album": "ironomi",
                    "artists": "\u3044\u308d\u306e\u307f",
                    "id": 721061,
                    "name": "\u65e5\u3060\u307e\u308a",
                    "picUrl": "https://p4.music.126.net/QCpgjEScYQ-6jWjAWzGMHw==/857619069665576.jpg"
                },
                {
                    "album": "room",
                    "artists": "hideyuki hashimoto",
                    "id": 507585635,
                    "name": "matsu",
                    "picUrl": "https://p4.music.126.net/hQ6ysVFhIEEByVuHZ1CSJQ==/109951168734703694.jpg"
                },
                {
                    "album": "RECODE",
                    "artists": "\u3044\u308d\u306e\u307f",
                    "id": 22663118,
                    "name": "\u5915\u51ea",
                    "picUrl": "https://p4.music.126.net/3PVb167Qijgde3VSR5lwsA==/109951165907473270.jpg"
                },
                {
                    "album": "room",
                    "artists": "hideyuki hashimoto",
                    "id": 507585627,
                    "name": "futari",
                    "picUrl": "https://p3.music.126.net/hQ6ysVFhIEEByVuHZ1CSJQ==/109951168734703694.jpg"
                },
                {
                    "album": "Pavonis ~ Piano Collection II ~",
                    "artists": "\u03b1\u00b7Pav",
                    "id": 29137871,
                    "name": "\u03b7",
                    "picUrl": "https://p3.music.126.net/U5O4aGdTvcnHSA5HhxLapg==/7937374441937799.jpg"
                },
                {
                    "album": "room",
                    "artists": "hideyuki hashimoto",
                    "id": 507585626,
                    "name": "hitori",
                    "picUrl": "https://p4.music.126.net/hQ6ysVFhIEEByVuHZ1CSJQ==/109951168734703694.jpg"
                },
                {
                    "album": "RECODE",
                    "artists": "\u3044\u308d\u306e\u307f",
                    "id": 22663110,
                    "name": "\u6728\u9670",
                    "picUrl": "https://p3.music.126.net/3PVb167Qijgde3VSR5lwsA==/109951165907473270.jpg"
                },
                {
                    "album": "Catarse",
                    "artists": "Andrei Machado",
                    "id": 28273864,
                    "name": "Tempo",
                    "picUrl": "https://p3.music.126.net/FyOt30OsWpaTLu-3_mqbsg==/109951170632639724.jpg"
                },
                {
                    "album": "home",
                    "artists": "hideyuki hashimoto",
                    "id": 28679469,
                    "name": "koe",
                    "picUrl": "https://p4.music.126.net/EkQVJPKHc9AdZMAAXp2MUQ==/109951168047742764.jpg"
                },
                {
                    "album": "Sometimes",
                    "artists": "Goldmund",
                    "id": 37132783,
                    "name": "Too Much Still",
                    "picUrl": "https://p4.music.126.net/WsXwopZZBokoUd7NG0G36w==/109951163470970521.jpg"
                },
                {
                    "album": "Collaborative Works",
                    "artists": "\u00d3lafur Arnalds",
                    "id": 36199955,
                    "name": "20:17",
                    "picUrl": "https://p3.music.126.net/Ehr4gUc-jHvSEm0C0ZY_uQ==/3410685070697609.jpg"
                },
                {
                    "album": "Pavonis ~ Piano Collection \u2160~",
                    "artists": "\u03b1\u00b7Pav",
                    "id": 139221,
                    "name": "\u03bc\u00b9",
                    "picUrl": "https://p3.music.126.net/ycOIJZz5kBB-ZkqvKWdKrg==/126443837210020.jpg"
                },
                {
                    "album": "Outliers, Vol. I: Iceland",
                    "artists": "Goldmund",
                    "id": 5064939,
                    "name": "The Wind Sings",
                    "picUrl": "https://p3.music.126.net/PtsN5km34z-34rcSZFWpNw==/1820791255607150.jpg"
                }
            ]
        },
        "status": "success"
    },
    "message": "\u83b7\u53d6\u6b4c\u5355\u8be6\u60c5\u6210\u529f",
    "status": 200,
    "success": true
}
```