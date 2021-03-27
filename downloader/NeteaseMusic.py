import os

from util.Log import Log
from util.Request import Request
from util.AES import AESCipher
import json
import time

class NeteaseMusic(object):

    def __init__(self):
        #有个坑，这里实例化两次，会打印两次Log
        self.log = Log('NeteaseMusic Service')
        self.config = {
            'nonce': '0CoJUm6Qyw8W8jud',
            'secretKey': 'TA3YiYCfY2dDJQgg',
            'encSecKey': '84ca47bca10bad09a6b04c5c927ef077d9b9f1e37098aa3eac6ea70eb59df0aa28b691b7e75e4f1f9831754919ea784c8f74fbfadf2898b0be17849fd656060162857830e241aba44991601f137624094c114ea8d17bce815b0cd4e5b8e2fbaba978c6d1d14dc3d1faf852bdd28818031ccdaaa13a6018e1024e2aae98844210',
            'IV': '0102030405060708'
        }

    # aes-128-cbc
    def aesEncode(self, data, key):
        return AESCipher(key=key).encrypt(data, self.config['IV'])
    
    # 预处理Post数据
    def prepare(self, data):
        result = { 'params': self.aesEncode(json.dumps(data), self.config['nonce']) }
        result['params'] = self.aesEncode(result['params'], self.config['secretKey'])
        result['encSecKey'] = self.config['encSecKey']
        return result

    # 搜索歌曲
    def search(self, keyword, singer=None):
        response = Request.jsonGet(url='http://s.music.163.com/search/get/', params={
            'type': 1,
            's': keyword
        })
        if 'code' in response and response['code'] == 200:
            result = []
            # 遍历歌曲
            for song in response['result']['songs']:
                # 遍历歌手
                song['singer'] = ''
                isSelect = True
                for artist in song['artists']:
                    if singer and artist['name'] == singer:
                        song['singer'] = singer
                        isSelect = True
                    elif singer:
                        isSelect = False
                    else:
                        isSelect = True
                        song['singer'] += artist['name'] + ' '
                if isSelect:
                    song['singer'] = song['singer'].strip()
                    result.append(song)

            return result
        else:
            return []
    
    # 搜索歌曲 取第一首
    def searchSingle(self, keyword, singer=None):
        result = self.search(keyword, singer)
        if result:
            return result[0]
        else:
            return None

    # 批量获取歌曲链接
    def getUrl(self, songIds):
        response = Request.jsonPost(url='http://music.163.com/weapi/song/enhance/player/url?csrf_token=', params=self.prepare({
            'ids': songIds,
            'br': 999000,
            'csrf_token': ''
        }))

        # 解析response
        if 'code' in response and response['code'] == 200:
            if 'data' in response:
                return response['data']
            else:
                return []
        else:
            return None
    
    # 获取单一歌曲链接
    def getSingleUrl(self, songId):
        result = self.getUrl([songId])
        if result == None:
            return result
        elif len(result) == 0:
            return {}
        else:
            return result[0]

    # 通过歌曲id下载歌曲
    def download(self, songId, filename=None, callback=None):
        # 名称处理
        if not filename:
            # filename = str(int(time.time()))
            filename = str(songId)

        # 获取歌曲并下载
        musicResult = self.getSingleUrl(songId)
        if musicResult and 'url' in musicResult:
            musicUrl = musicResult['url']
            filename = './downloader/download/%s.mp3' % filename
            if not os.path.exists(filename):
                self.log.info("开始下载音乐%s" % filename)
                print(type(filename))
                print(filename)
                print("开始下载音乐%s" % filename)
                print("开始下载音乐%s" % filename)
                print("musicUrl "+musicUrl)
                # print("callback "+callback)
                Request.download(musicUrl, filename, callback)
            else:
                self.log.info("使用缓存的音乐%s" % filename)
                print("使用缓存的音乐%s" % filename)
            self.log.info("下载完成")

            return filename
        else:
            return False

    # 通过ID获取歌曲信息
    def getInfo(self, id):
        response = Request.jsonPost(url='http://music.163.com/weapi/v3/song/detail?csrf_token=', params=self.prepare({
            'c': json.dumps([{ 'id': id }]),
            'csrf_token': ''
        }))
        if 'code' in response and response['code'] == 200:
            if 'songs' in response and response['songs']:
                song = response['songs'][0]
                return {
                    'id': song['id'],
                    'name': song['name'],
                    'singer': song['ar'][0]['name']
                }
                pass
            else:
                return False
        else:
            return False

    # 获取歌词
    def getLyric(self, songId):
        response = Request.jsonPost(url='http://music.163.com/weapi/song/lyric?csrf_token=', params=self.prepare({
            'id': songId,
            'os': 'pc',
            'lv': -1,
            'kv': -1,
            'tv': -1,
            'csrf_token': ''
        }))

        if 'code' in response and response['code'] == 200:
            result = {
                'lyric': '',
                'tlyric': ''
            }
            # 获取歌词
            if 'lrc' in response and 'lyric' in response['lrc']:
                result['lyric'] = response['lrc']['lyric']
            else:
                return False

            # 获取翻译歌词
            if 'tlyric' in response and 'lyric' in response['tlyric']:
                result['tlyric'] = response['tlyric']['lyric']

            return result
        else:
            return False

    #生成字幕文件，传入参数：
    #filename：文件名
    #info：文件信息，用于左下角显示用的
    #path：文件路径
    #ass：最原始的歌词数据
    def make_ass(self,filename, info, ass = '', asst = ''):
        # ass = lrc_to_ass(ass)
        # asst = tlrc_to_ass(asst)
        # timer_get = timer_create(filename,path)
        timer_get = ''
        file_content = '''[Script Info]
Title: Default ASS file
ScriptType: v4.00+
WrapStyle: 2
Collisions: Normal
PlayResX: 960
PlayResY: 720
ScaledBorderAndShadow: yes
Video Zoom Percent: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,2,10,10,5,1
Style: left_down,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,1,10,10,5,1
Style: right_down,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,3,10,10,5,1
Style: left_up,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,7,10,10,5,1
Style: right_up,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,9,10,10,5,1
Style: center_up,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,8,10,10,5,1
Style: center_up_big,微软雅黑,28,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,8,10,10,5,1
Style: center_down,微软雅黑,20,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,2,10,10,5,1
Style: center_down_big,微软雅黑,28,&H00FFFFFF,&H00FFFFFF,&H28533B3B,&H500E0A00,0,0,0,0,100.0,100.0,0.0,0.0,1,3.5546875,3.0,2,10,10,5,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 2,0:00:00.00,9:00:00.00,left_down,,0,0,0,,'''+info+'''
Dialogue: 2,0:00:00.00,9:00:00.00,right_down,,0,0,0,,基于树莓派4B\\N'''+'点播日期：'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'''
Dialogue: 2,0:00:00.00,9:00:00.00,left_up,,0,0,0,,super5xy的树莓派点播台~\\N已开源，源码见https://biu.ee/pi-live\\N使用时请保留源码链接
Dialogue: 2,0:00:00.00,9:00:00.00,right_up,,0,0,0,,弹幕点播方法请看直播间简介哦~\\N手机请点击直播间标题查看
        '''+ass+asst+timer_get
        filename = './resource/lrc/%s.ass' % filename
        print(filename)
        # file = open(path+'/downloads/'+str(filename)+'.ass','w')    #保存ass字幕文件
        file = open(filename,'w',encoding='utf-8')    #保存ass字幕文件
        file.write(file_content)
        file.close()