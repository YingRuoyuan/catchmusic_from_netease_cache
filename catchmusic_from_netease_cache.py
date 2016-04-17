#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import platform
import getpass
import shutil
import random
import urllib2


# class Music_list(object):
#
#     def __init__(self,num):
#         self.num = num
#         self.keys = "music_name", "songid", "cache_name"
#         for i in self.keys:
#             setattr(self,i,i)
#
# music_list=Music_list(0)

class Catch_music(object):
    music_list=[]
    music_info={}
    PATTERN=re.compile(r'<title>(.*) - (.*) - 网易云音乐</title>')
    CATCHID_PATTERN=re.compile(r'(.*)"songId":"(.*)","md5":(.*)')
    userAgent=[
        "Mozilla/5.0 (Windows NT 5.1; rv:37.0) Gecko/20100101 Firefox/37.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
        "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"]
    headers = {
         "User-Agent":random.choice(userAgent)
        }

    def getCachePath(self, uname):
        if platform.system() == 'Darwin':
            return '/Users/' + uname + '/Library/Containers/com.netease.163music/Data/Caches/online_play_cache'
            # return '/Users/' + uname + '/Library/Containers/com.netease.163music/Data/Library/Caches/online_play_cache'
        elif platform.system() == 'Windows':
            return 'C:\\Users\\' + uname + '\\AppData\\Local\\Netease\\CloudMusic\\Cache\\Cache'
        else:
            print 'OS Not Supported'
            return ''

    def getSavePath(self, uname):
        if platform.system() == 'Darwin':
            return '/Users/' + uname + '/Desktop/Music'
        elif platform.system() == 'Windows':
            return 'C:\\Users\\' + uname + '\\Desktop\\Music'
        else:
            return ''

    def catch_file(self, num):
        username = getpass.getuser()
        cachePath = self.getCachePath(username)
        targetPath = self.getSavePath(username)
        targetname=self.music_list[num].get('music_name')
        fileName=self.music_list[num].get('cache_name')
        file1=fileName+'.uc!'
        file2=fileName+'.uc'
        if os.path.exists(file1):
            cachefile=file1
        elif os.path.exists(file2):
            cachefile=file2
        else:
            print "[Error]:Can not found the cachefile %s." % (fileName)
            sys.exit()
        shutil.copyfile(os.path.join(cachePath, cachefile), os.path.join(targetPath, cachefile))
        os.rename(os.path.join(targetPath, cachefile), os.path.join(targetPath, targetname))
        print cachefile + ' -> ' + targetname

    def catch_all_file(self):
        for i in range(0, len(self.music_list)):
            self.catch_file(i)

    def del_all_file(self):
        usrClear = raw_input('是否需要清理网易云音乐缓存？（y/n）')
        if usrClear == 'y':
            for anyFile in os.listdir(self.cachePath):
                os.remove(anyFile)
            print '清理完成'
        else:
            print '进程结束'

    def craw_name(self, songid):
        # url="http://music.163.com/#/m/song?id=%s" % (songid)  //Warning: Don not use this url because this content did not have the title name.
        url="http://music.163.com/song?id=%s" % (songid)
        music_name=""
        try:
            req = urllib2.Request(url, headers = self.headers)
            req.add_header("Referer","http://music.163.com/")
            res = urllib2.urlopen(req)
            content = res.read()
        except urllib2.HTTPError as http_error:
            print "[DEBUG]HTTPError: %s." % (http_error)
            print 'Open Url failed due to Error:' + str(http_error) + ' and ' + str(http_error.read())
        match = re.search(self.PATTERN, content)
        if match:
            print "Found music name: ", match.group(1)
            music_name=match.group(1) + ".mp3"
        else:
            print "[DEBUG]Found music name failed."
        return music_name

    def perform(self):
        print "Start:************************************************"
        print "正在扫描本地缓存:"
        username = getpass.getuser()
        cachePath = self.getCachePath(username)
        targetPath = self.getSavePath(username)
        if os.path.exists(targetPath) == False:
            os.mkdir(targetPath)
        os.chdir(cachePath)
        for fileName in os.listdir(cachePath):
            portion = os.path.splitext(fileName)
            if portion[1] == '.info':
                info_text = open(fileName).read()
                match=re.search(self.CATCHID_PATTERN, info_text)
                if match:
                    songid=match.group(2)
                    music_name=self.craw_name(songid)
                    cache_name=portion[0]
                    if not songid =="":
                        self.music_info={'music_name':music_name, 'songid':songid, 'cache_name':cache_name}
                        self.music_list.append(self.music_info)
                        # setattr(music_list, 'music_name', music_name)
                        # setattr(music_list, 'songid', songid)
                        # setattr(music_list, 'cache_name', cache_name)
                else:
                    pass
        print "本地缓存文件包含:"
        for i in range(0, len(self.music_list)):
            print i, "-" + self.music_list[i].get('music_name')
        result = raw_input("请选择需要提取歌曲前的数字(按q退出程序,按a提取全部,按d清除缓存):")
        if result=="q":
            sys.exit()
        elif result=="a":
            self.catch_all_file()
        elif result=="d":
            self.del_all_file()
        elif int(result) in range(0, len(self.music_list)):
            self.catch_file(int(result))
        else:
            print "Error input"
        print "End:**************************************************"

catch_music=Catch_music()

if __name__ == '__main__':
    catch_music.perform()