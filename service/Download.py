import json
import re
import traceback

from util.Queue import DownloadQueue, PlayQueue

from downloader.NeteaseMusic import NeteaseMusic
from service.Service import Service
from util.Danmu import Danmu
from util.Log import Log
import requests
#滚动歌词生成
def lrc_to_ass(lrc):
    lrc=lrc.splitlines() #按行分割开来
    list1=['00','00']
    list2=['00','00']
    list3=['00','00']
    list4=[' ',' ']
    result='\r\n'
    for i in lrc:
        matchObj = re.match( r'.*\[(\d+):(\d+)\.(\d+)\]([^\[\]]*)', i)  #正则匹配获取每行的参数，看不懂的去自行学习正则表达式
        if matchObj:    #如果匹配到了东西
            list1.append(matchObj.group(1))
            list2.append(matchObj.group(2))
            list3.append(matchObj.group(3))
            list4.append(matchObj.group(4))
    list1.append('05')
    list1.append('05')
    list2.append('00')
    list2.append('00')
    list3.append('00')
    list3.append('00')
    list4.append(' ')
    list4.append(' ')
    for i in range(2, len(list1)-4):
        text='　'+list4[i+1]+'　\\N　'+list4[i+2]+'　'
        result+='Dialogue: 2,0:'+list1[i]+':'+list2[i]+'.'+list3[i][0:2]+',0:'+list1[i+1]+':'+list2[i+1]+'.'+list3[i+1][0:2]+',center_down,,0,0,0,,'+text+'\r\n'
        text='　'+list4[i]+'　'
        result+='Dialogue: 2,0:'+list1[i]+':'+list2[i]+'.'+list3[i][0:2]+',0:'+list1[i+1]+':'+list2[i+1]+'.'+list3[i+1][0:2]+',center_down_big,,0,0,0,,'+text+'\r\n'
        text='　'+list4[i-2]+'　\\N　'+list4[i-1]+'　'
        result+='Dialogue: 2,0:'+list1[i]+':'+list2[i]+'.'+list3[i][0:2]+',0:'+list1[i+1]+':'+list2[i+1]+'.'+list3[i+1][0:2]+',center_down,,0,0,0,,'+text+'\r\n'
    #修正倒数第二句句歌词消失的bug
    text='　'+list4[len(list1)-3]+'　\\N　'+list4[len(list1)-2]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-4]+':'+list2[len(list1)-4]+'.'+list3[len(list1)-4][0:2]+',0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',center_down,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-4]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-4]+':'+list2[len(list1)-4]+'.'+list3[len(list1)-4][0:2]+',0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',center_down_big,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-6]+'　\\N　'+list4[len(list1)-5]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-4]+':'+list2[len(list1)-4]+'.'+list3[len(list1)-4][0:2]+',0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',center_down,,0,0,0,,'+text+'\r\n'
    #修正最后一句歌词消失的bug
    text='　'+list4[len(list1)-2]+'　\\N　'+list4[len(list1)-1]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',0:10:00.00,center_down,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-3]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',0:10:00.00,center_down_big,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-5]+'　\\N　'+list4[len(list1)-4]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',0:10:00.00,center_down,,0,0,0,,'+text+'\r\n'
    return result

#滚动歌词生成
def tlrc_to_ass(lrc):
    lrc=lrc.splitlines() #按行分割开来
    list1=['00','00']
    list2=['00','00']
    list3=['00','00']
    list4=[' ',' ']
    result='\r\n'
    for i in lrc:
        matchObj = re.match( r'.*\[(\d+):(\d+)\.(\d+)\]([^\[\]]*)', i)  #正则匹配获取每行的参数，看不懂的去自行学习正则表达式
        if matchObj:    #如果匹配到了东西
            list1.append(matchObj.group(1))
            list2.append(matchObj.group(2))
            list3.append(matchObj.group(3))
            list4.append(matchObj.group(4))
    list1.append('05')
    list1.append('05')
    list2.append('00')
    list2.append('00')
    list3.append('00')
    list3.append('00')
    list4.append(' ')
    list4.append(' ')
    for i in range(2, len(list1)-4):
        text='　'+list4[i-2]+'　\\N　'+list4[i-1]+'　'
        result+='Dialogue: 2,0:'+list1[i]+':'+list2[i]+'.'+list3[i][0:2]+',0:'+list1[i+1]+':'+list2[i+1]+'.'+list3[i+1][0:2]+',center_up,,0,0,0,,'+text+'\r\n'
        text='　'+list4[i]+'　'
        result+='Dialogue: 2,0:'+list1[i]+':'+list2[i]+'.'+list3[i][0:2]+',0:'+list1[i+1]+':'+list2[i+1]+'.'+list3[i+1][0:2]+',center_up_big,,0,0,0,,'+text+'\r\n'
        text='　'+list4[i+1]+'　\\N　'+list4[i+2]+'　'
        result+='Dialogue: 2,0:'+list1[i]+':'+list2[i]+'.'+list3[i][0:2]+',0:'+list1[i+1]+':'+list2[i+1]+'.'+list3[i+1][0:2]+',center_up,,0,0,0,,'+text+'\r\n'
    #修正倒数第二句句歌词消失的bug
    text='　'+list4[len(list1)-6]+'　\\N　'+list4[len(list1)-5]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-4]+':'+list2[len(list1)-4]+'.'+list3[len(list1)-4][0:2]+',0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',center_up,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-4]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-4]+':'+list2[len(list1)-4]+'.'+list3[len(list1)-4][0:2]+',0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',center_up_big,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-3]+'　\\N　'+list4[len(list1)-2]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-4]+':'+list2[len(list1)-4]+'.'+list3[len(list1)-4][0:2]+',0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',center_up,,0,0,0,,'+text+'\r\n'
    #修正最后一句歌词消失的bug
    text='　'+list4[len(list1)-5]+'　\\N　'+list4[len(list1)-4]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',0:10:00.00,center_up,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-3]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',0:10:00.00,center_up_big,,0,0,0,,'+text+'\r\n'
    text='　'+list4[len(list1)-2]+'　\\N　'+list4[len(list1)-1]+'　'
    result+='Dialogue: 2,0:'+list1[len(list1)-3]+':'+list2[len(list1)-3]+'.'+list3[len(list1)-3][0:2]+',0:10:00.00,center_up,,0,0,0,,'+text+'\r\n'
    return result


class DownloadService(Service):
    
    def __init__(self):
        self.danmu = Danmu()
        self.log = Log('Download Service')
        self.musicDownloader = NeteaseMusic()

    # 获取下载队列 分发至下载函数
    def run(self):
        try:
            # 判断队列是否为空
            if DownloadQueue.empty():
                return
            
            # 获取新的下载任务
            task = DownloadQueue.get()
            if task and 'type' in task:
                if task['type'] == 'music':
                    self.musicDownload(task)
                elif task['type'] == 'vedio':
                    pass
        except Exception as e:
            self.log.error(e)
            traceback.print_exc()
            pass
    
    def musicDownload(self, song):

        # 搜索歌曲并下载
        #发送弹幕
        self.danmu.send('正在下载%s' % song['name'])
        filename = self.musicDownloader.download(song['id'])


        headers = {
            'authority': 'music.163.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://music.163.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://music.163.com/search/',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        url = 'http://music.163.com/api/song/lyric?'+ 'id=' + str(song['id'])+ '&lv=1&kv=1&tv=-1'
        resp = requests.get(url,headers=headers)
        resjson = json.loads(resp.text)

        #左下角info信息
        info = '当前网易云id：'+str(song['id'])+"\\N当前播放的歌曲："+song['name']+"\\N点播人："+song['username']
        #生成ass文件
        lrc = ""
        tlrc = ""
        #如果是纯音乐不传歌词
        if not "nolyric" in resjson:
            lrc=resjson["lrc"]["lyric"]
            tlrc=resjson["tlyric"]["lyric"]
        else:
            lrc='[00:00.000] 纯音乐，请您欣赏\n[10:00.000] '
        self.musicDownloader.make_ass(song['name'],info,lrc_to_ass(lrc),tlrc_to_ass(tlrc))

        if filename:
            self.log.info('歌曲下载完毕 %s - %s' % (song['name'], song['singer']))

            # 加入播放队列
            PlayQueue.put({
                'type': 'music',
                'filename': filename,
                'name': song['name'],
                'singer': song['singer'],
                'username': song['username'],
                'lrc': './resource/lrc/'+song['name']+'.ass'
            })
        else:
            pass

