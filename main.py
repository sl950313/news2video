#!/usr/bin/python
# -*- coding: utf-8 -*-
#coding=utf-8

'''
text news to video to earn money

step 1: get text from url news
step 2: get pic from the same url news
step 3: generate video by the text and pics
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import cv2
import os
from PIL import Image, ImageFont, ImageDraw
import re
import moviepy.editor as mpe
import subprocess
from aip import AipSpeech
import librosa
import numpy
import urllib2
import urllib
import json

class News2Video():
    def __init__(self, url):
        self.url = url
        self.name = ""
        if url != "":
            self.name = self.url.split('/')[-1].split('.')[0]
        else:
            print("Please input the right url")
            sys.exit(1)

        #print("name:", self.name, "url", url)
        #sys.exit(1)
        self.imgroot = r'E:\testimg\/' + self.name + "/"
        self.videoroot = r'E:\testavi\/' + self.name + "/"
        self.audioduration = 0
        if not os.path.exists(self.imgroot):
            os.makedirs(self.imgroot)
        if not os.path.exists(self.videoroot):
            os.makedirs(self.videoroot)
        print("url:%s name:%s imgroot:%s videoroot:%s" % (self.url, self.name, self.imgroot, self.videoroot))

    def getTextAndPicFromUrl(self):
        page = urllib2.urlopen(self.url)
        content = page.read()
        lines = content.split("\n")

        mapImgContent = []
        mapContentImg = {}
        maxLenNote = ""
        imgs = []
        title = ""
        firstnote = ""
        cnt = 0
        for line in lines:
            if line.find("<title>") != -1:
                titleBegin = line.find("<title>")
                titleEnd = line.find("</title>")
                title = line[titleBegin + len("<title>"):titleEnd]

            if line.find("orig") < 0 or line.find("jpeg") > 0:
                continue

            if cnt >= 9:
                break
            #cnt += 1
            begin = line.find("{")
            end = line.rfind("}")
            info = line[begin:(end + 1)].replace(' ', '')
            orig = info.find("orig:")
            big = info.find("big:")
            thumb = info.find("thumb:")
            note = info.find("note:")
            url = info.find("url:")

            origUrl = info[orig + len("orig:") + 1:(big - 2)]
            bigUrl = info[big + len("big:") + 1:(thumb - 2)]
            thumbUrl = info[thumb + len("thumb:") + 1:(note - 2)]
            note = info[note + len("note:") + 1:(url - 2)].decode("unicode_escape")
            #urlUrl = info[orig + len("url:") + 2:(big - 2)]

            if firstnote == "":
                firstnote = note

            bigUrlNameBegin = bigUrl.rfind("/")
            bigUrlNameEnd = bigUrl.find(".jpg")
            bigUrlName = bigUrl[bigUrlNameBegin + 1:bigUrlNameEnd]
            if os.path.exists(self.imgroot + "/" + bigUrlName + ".jpg"):
                print("pic:%s is already exsit" % (self.imgroot + "/" + bigUrlName + ".jpg"))
            else:
                print("pic:%s is not exsit, let's download it" % (self.imgroot + "/" + bigUrlName + ".jpg"))
                urllib.urlretrieve(bigUrl, self.imgroot + "/" + bigUrlName + ".jpg")
            imgcontent = (bigUrlName + ".jpg", note)
            imgs.append(bigUrlName + ".jpg")

            if len(maxLenNote) <= len(note):
                maxLenNote = note

            print(imgcontent)
            mapImgContent.append(imgcontent)
            if firstnote not in mapContentImg.keys():
                mapContentImg[firstnote] = [bigUrlName + ".jpg"]
            else:
                mapContentImg[firstnote].append(bigUrlName + ".jpg")

        mapContentImg = {}
        mapContentImg[maxLenNote] = imgs

        #print(mapImgContent)
        #sys.exit(1)

        #text = []
        #pics = []
        #title = u"纽约股市12日早盘暴跌再度触发熔断机制"
        #text.append(u"3月12日，在美国纽约证券交易所，电子屏显示交易因触发熔断机制暂停。 纽约股市三大股指在12日开盘出现暴跌，跌幅超过7%。暴跌行情导致美股再次触发熔断机制，暂停交易15分钟。 新华社发")
        '''
        files = os.listdir(self.imgroot)
        for file in files:
            pics.append(file)
        texts = text[0]
        for t in range(1, len(text)):
            texts += text[t]
            print(text[t])
        #print(texts[0:30])
        '''
        #print(mapImgContent)
        print(self.imgroot)
        print(title)
        print(mapContentImg)
        print(len(mapContentImg))
        #sys.exit(1)
        return mapContentImg, title

    def changePicSize(self, imgpath, width, height):
        print("imgPath:%s" % imgpath)
        im = Image.open(imgpath)
        w, h = im.size
        print("w:%d width:%d" % (w, width))
        if True or w > width:
            print("pic:%s size is bigger" % (imgpath))
            #hNew = width * h / w
            hNew = height
            wNew = width
            out = im.resize((wNew, hNew), Image.ANTIALIAS)
            newPic = re.sub(imgpath[:-4], imgpath[:-4] + '_new', imgpath)
            print("newPic", newPic)
            out.save(newPic)

    def changePathPicSize(self, imgpath):
        minWidth = 1000000
        minHeight = 0
        for im in os.listdir(imgpath):
            img = cv2.imread(imgpath + "/" + im)
            print(img.shape)
            if minWidth > img.shape[0]:
                minHeight = img.shape[0]
                minWidth = img.shape[1]

        if minHeight == 0:
            print("no pic in path:%s" % (imgpath))
            sys.exit(-1)

        print("minw:%d minh:%d" % (minWidth, minHeight))
        for im in os.listdir(imgpath):
            self.changePicSize(imgpath + "/" + im, minWidth, minHeight)
        return minWidth, minHeight

    def generateVideo(self, pics, duration, name):
        #videopath = r"E:\test-res\test.avi"
        videopath = self.videoroot + "/piconly-%s.avi" % name
        #imgpath = r'E:\testimg\/'
        imgpath = self.imgroot
        minWidth, minHeight = self.changePathPicSize(imgpath)
        imgnum = len(os.listdir(imgpath))
        perSecondImg = max(int(duration / imgnum), 1)
        fps = 1
        #size = (540, 720)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        videowriter = cv2.VideoWriter(videopath, fourcc, fps, (minWidth, minHeight))
        #for i in os.listdir(imgpath):
        for pic in pics:
            img = cv2.imread(imgpath + '/' + pic)
            print(img.shape[0], img.shape[1])
            #cv2.rectangle(img, (0, 0), (10, 10), (55,255,155), 5)
            #img = cv2.putText(img, 'frame_%s' % i, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (55, 255, 155), 2)
            for j in range(0, perSecondImg):
                videowriter.write(img)

        left = int(duration - perSecondImg * imgnum)
        print("pers img:%d duration:%d imgnum:%d left:%d" % (perSecondImg, duration, imgnum, left))
        if left > 0:
            for i in range(0, left):
                img = cv2.imread(imgpath + '/' + pics[-1])
                videowriter.write(img)

        videowriter.release()
        print(videopath[:-3] + "mp4")
        self.convertAvi2Mp4(videopath, videopath[:-3] + "mp4")
        return videopath[:-3] + "mp4"

    def addText2Video(self, videopath, texts, title):
        textVideo = videopath[:-4] + "-withtext.mp4"
        print("addText2Video", videopath, "textVideo", textVideo)
        video = cv2.VideoCapture(videopath)
        fps_video = video.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        videoWriter = cv2.VideoWriter(textVideo, fourcc, fps_video, (frame_width, frame_height))
        frame_id = 0
        perLineWord = 20
        lines = int(len(texts) / perLineWord)
        perLineSecond = int(self.audioduration / lines)
        print("lines:%d perlineword:%d textsLen:%d perlineSecond:%d" % (lines, perLineWord, len(texts), perLineSecond))
        cnt = 0

        while (video.isOpened()):
            ret, frame = video.read()
            if ret == True:
                if cnt % perLineSecond == 0:
                    textbegin = int(cnt / perLineSecond) * perLineWord
                    textend = min((int(cnt / perLineSecond) + 1) * perLineWord, len(texts))
                    showtext = texts.decode('utf8')[textbegin:textend].encode('utf8')
                    print("-----------------[%d:%d:%d]---------" % (textbegin, textend, cnt))
                    print(showtext)
                #cnt = (cnt + 1) % perLineSecond
                cnt += 1
                #print("cnt", cnt)
                frame_id += 1
                #word_x = frame_width + 40
                word_x = 100
                word_y = frame_height - 40
                #cv2.rectangle(frame, (word_x, word_y), (frame_width - 40, word_y + 40), (55,255,155), 1)
                frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(frame)
                #fontText = ImageFont.truetype("simsun.ttc", 20, encoding="utf-8")
                fontText = ImageFont.truetype("simsun.ttc", 35)
                titleText = ImageFont.truetype("msyh.ttc", 40)
                #draw.text((word_x, word_y), showtext, (255, 255, 255), font=fontText)
                draw.text((word_x, word_y), showtext.decode('utf8'), fill=(255, 255, 255, 1), font=fontText)
                draw.text((10, 40), title.decode('utf8'), fill=(255, 255, 255, 1), font=titleText)
                #(frame, title.decode('utf8')[0:-1].encode('utf8').decode('utf8'), (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (55,255,155), 1)
                frame = cv2.cvtColor(numpy.asarray(frame), cv2.COLOR_RGB2BGR)


                #cv2.putText(frame, 'Picture %s' % showtext, (word_x, word_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (55,255,155), 1)
                videoWriter.write(frame)
            else:
                videoWriter.release()
                break
        print("textVideo:%s", textVideo)
        return textVideo

    def addAudio2Video(self, videopath, audiopath):
        video = mpe.VideoFileClip(videopath)
        print("video duration:%d" % (video.duration))
        audio = mpe.AudioFileClip(audiopath)
        subaudio = audio.subclip(0, video.duration)
        print(video.audio)
        finalAudio = mpe.CompositeAudioClip([subaudio])
        #finalAudio = subaudio
        finalVideo = video.set_audio(finalAudio)
        audioVideo = videopath[:-4] + "-withaudio.mp4"
        finalVideo.write_videofile(audioVideo)
        return audioVideo

    def convertAvi2Mp4(self, avipath, mp4path):
        print("avipath:%s mp4path:%s" % (avipath, mp4path))
        cmd = "ffmpeg -i {input} -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 {output}".format(input = avipath, output = mp4path)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.communicate()
        print("cmd:%s" % cmd)
        return True

    def text2Audio(self, text, name):
        audiopath = r'E:\test-res\%s-%s.mp3' % (self.name, name)
        if os.path.exists(audiopath):
            duration = librosa.get_duration(filename=audiopath)
            self.audioduration = duration
            print("audiopath:%s with duration:%d is exist, do not need to generate agin." % (audiopath, duration))
            return audiopath, duration

        APP_ID = '18701222'
        API_KEY = 'I1x7GAHVTKeiAImiHlG3xzGY'
        SECRET_KEY = 'I1GaRrI5NRqPnLxAerXsiO7vpiVREEEr'
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

        #result = client.synthesis('欢迎使用百度语音只能服务', 'zh', 1, {'vol':5,})
        result = client.synthesis(text, 'zh', 1, {'vol':5,})

        if not isinstance(result, dict):
            with open(audiopath, 'wb') as f:
                f.write(result)

        duration = librosa.get_duration(filename=audiopath)
        self.audioduration = duration
        return audiopath, duration

def main():
    return

def test():
    return

if __name__ == "__main__":
    #news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200306/2403795.shtml")
    #news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200313/2404484.shtml")
    #news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200313/2404487.shtml")
    #news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200313/2404486.shtml")
    #news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200313/2404483.shtml")
    #news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200313/2404487.shtml")
    news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200313/2404488.shtml")
    mapContentImg, title = news2video.getTextAndPicFromUrl()
    print("Get Text and Pic over..")
    print(mapContentImg)
    print(title)
    #for key in mapContentImg:
    videos = []
    for i in range(len(mapContentImg.keys())):
        audiopath, duration = news2video.text2Audio(mapContentImg.keys()[i], "audio-%d" % i)
        videopath = news2video.generateVideo(mapContentImg.values()[i], duration, "%d" % i)
        videopath = news2video.addAudio2Video(videopath, audiopath)
        videos.append(mpe.VideoFileClip(videopath))
        #print(mapContentImg.keys()[i])
        #print(mapContentImg.values()[i])

    if len(videos) > 1:
        finalclip = mpe.concatenate_audioclips(videos)
        finalclip.to_videofile(news2video.imgroot + "final.mp4", fps=1, remove_temp=False)
    sys.exit(1)
    audiopath, duration = news2video.text2Audio(texts)
    print("Audio Generate over, name:%s duration:%d" % (audiopath, duration))
    videopath = news2video.generateVideo(pics, duration)
    print("Video Generate over, name:%s duration:%d" % (videopath, duration))
    #videopath = news2video.addText2Video(videopath, texts, title)
    print("Text Adding over, name:%s duration:%d" % (videopath, duration))
    videopath = news2video.addAudio2Video(videopath, audiopath)
    print("Audio Adding over, name:%s duration:%d" % (videopath, duration))
    #audiopath = news2video.text2Audio('欢迎使用百度语音只能服务')
    #news2video.changePicSize(r'E:\testimg\IMG_1615.JPG', 540, 720)
    #videopath = news2video.addAudio2Video(videopath, r'E:\test-res\test.mp3')
    #news2video.addAudio2Video(r'E:\test-res\test.mp4', r'E:\test-res\test.mp3')
    print("Final video name:%s" % (videopath))


    #test()
    #main()



