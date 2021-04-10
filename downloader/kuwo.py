# 酷我音乐解析
import requests
import json

from util.Log import Log


class KuwoDownloader:
    def __init__(self):
        self.log = Log('KuwoDownloader Service')

    # 取第一个
    def search(self,key):
        #搜索歌曲爬虫
        search_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord'
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36 Edg/84.0.522.63",
            "Cookie":"_ga=GA1.2.1083049585.1590317697; _gid=GA1.2.2053211683.1598526974; _gat=1; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1597491567,1598094297,1598096480,1598526974; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1598526974; kw_token=HYZQI4KPK3P",
            "Referer": "http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6",
            "csrf": "HYZQI4KPK3P",
        }
        params = {
            "key": key,
            # 页数
            "pn": "1",
            # 音乐数
            "rn": "10",
            "httpsStatus": "1",
            "reqId": "cc337fa0-e856-11ea-8e2d-ab61b365fb50",
        }

        resp = requests.get(search_url,params=params,headers=headers)
        print(resp.text)
        json_string = json.loads(resp.text)
        song_list=json_string["data"]["list"]
        for song in song_list:
            print(song)

        songid = song_list[0]["musicrid"]
        return songid


    #拼接下载链接
    def get_song(self,musicrid):
        return 'http://antiserver.kuwo.cn/anti.s?useless=/resource/&format=mp3&rid=%s&response=res&type=convert_url&' % musicrid

    # 解析下载链接
    def get_download_url(self,musicrid):
        headers2 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'Connection': 'keep-alive',
        'Host': 'antiserver.kuwo.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
        }
        resp = requests.get(self.get_song(musicrid), headers=headers2, allow_redirects=False)
        download_url = resp.headers['Location']
        self.log.info('解析链接 %s' % download_url)
        return download_url

    def download(self,musicname=None,musicrid=None):
        if musicrid:
            if 'MUSIC' not in musicrid:
                musicrid = 'MUSIC_'+ musicrid
            self.__download__(musicrid)
        else:
            musicrid = self.search(musicname)
            self.__download__(musicrid)



    #下载歌曲到本地
    def __download__(self,musicrid):
        filename = './downloader/download/%s.mp3' % musicrid
        resp = requests.get(self.get_download_url(musicrid))
        with open(filename, "wb") as file:
            file.write(resp.content)



