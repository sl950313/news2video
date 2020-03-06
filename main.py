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
        if not os.path.exists(self.imgroot):
            os.makedirs(self.imgroot)
        if not os.path.exists(self.videoroot):
            os.makedirs(self.videoroot)
        print("url:%s name:%s imgroot:%s videoroot:%s" % (self.url, self.name, self.imgroot, self.videoroot))

    def getTextAndPicFromUrl(self):
        text = []
        pics = []
        text.append("3月5日，在韩国大邱世界杯体育场，新冠肺炎轻症患者走下救护车，之后将被送往分散在庆尚北道各地的治疗中心。 当日，在韩国大邱，一批新冠肺炎轻症患者被集中到世界杯体育场，随后分批从这里出发，被分散送往庆尚北道各地的治疗中心。在治疗中心有专职医疗人员常驻，随时检查设施内确诊人员的身体状况，医疗人员认为需要住院的患者将被迅速移送到医院。 新华社发（李相浩 摄）")
        text.append("3月5日，在韩国大邱世界杯体育场，医疗队工作人员坐在地上休息。 当日，在韩国大邱，一批新冠肺炎轻症患者被集中到世界杯体育场，随后分批从这里出发，被分散送往庆尚北道各地的治疗中心。在治疗中心有专职医疗人员常驻，随时检查设施内确诊人员的身体状况，医疗人员认为需要住院的患者将被迅速移送到医院。 新华社发（李相浩 摄）")
        text.append("这是3月5日在韩国庆尚北道漆谷郡拍摄的一处专门供大邱的新冠肺炎轻症患者居住的治疗中心。 当日，在韩国大邱，一批新冠肺炎轻症患者被集中到世界杯体育场，随后分批从这里出发，被分散送往庆尚北道各地的治疗中心。在治疗中心有专职医疗人员常驻，随时检查设施内确诊人员的身体状况，医疗人员认为需要住院的患者将被迅速移送到医院。 新华社发（李相浩 摄）")
        text.append("3月5日，在韩国庆尚北道漆谷郡，工作人员在一处专门供大邱新冠肺炎轻症患者居住的治疗中心进行消毒防疫。 当日，在韩国大邱，一批新冠肺炎轻症患者被集中到世界杯体育场，随后分批从这里出发，被分散送往庆尚北道各地的治疗中心。在治疗中心有专职医疗人员常驻，随时检查设施内确诊人员的身体状况，医疗人员认为需要住院的患者将被迅速移送到医院。 新华社发（李相浩 摄）")
        pics.append(self.imgroot + "1.jpg")
        pics.append(self.imgroot + "2.jpg")
        pics.append(self.imgroot + "3.jpg")
        pics.append(self.imgroot + "4.jpg")
        pics.append(self.imgroot + "5.jpg")
        pics.append(self.imgroot + "6.jpg")
        pics.append(self.imgroot + "7.jpg")
        pics.append(self.imgroot + "8.jpg")
        pics.append(self.imgroot + "9.jpg")
        pics.append(self.imgroot + "10.jpg")
        texts = text[0]
        for t in range(1, len(text)):
            texts += text[t]
            print(text[t])
        print(texts[0:30])
        return texts, self.imgroot

    def changePicSize(self, imgpath, width, height):
        print("imgPath:%s" % imgpath)
        im = Image.open(imgpath)
        w, h = im.size
        print("w:%d width:%d" % (w, width))
        if w > width:
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

    def generateVideo(self, imgpath, duration):
        #videopath = r"E:\test-res\test.avi"
        videopath = self.videoroot + "/piconly.avi"
        #imgpath = r'E:\testimg\/'
        minWidth, minHeight = self.changePathPicSize(imgpath)
        imgnum = len(os.listdir(imgpath))
        perSecondImg = max(int(duration / imgnum), 1)
        fps = 1
        #size = (540, 720)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        videowriter = cv2.VideoWriter(videopath, fourcc, fps, (minWidth, minHeight))
        for i in os.listdir(imgpath):
            img = cv2.imread(imgpath + '/' + i)
            print(img.shape[0], img.shape[1])
            #cv2.rectangle(img, (0, 0), (10, 10), (55,255,155), 5)
            #img = cv2.putText(img, 'frame_%s' % i, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (55, 255, 155), 2)
            for j in range(0, perSecondImg):
                videowriter.write(img)

        left = duration - perSecondImg * imgnum
        print("pers img:%d duration:%d imgnum:%d left:%d" % (perSecondImg, duration, imgnum, left))
        if left > 0:
            for i in range(0, left):
                img = cv2.imread(imgpath + '/' + os.listdir(imgpath)[-1])
                videowriter.write()

        videowriter.release()
        print(videopath[:-3] + "mp4")
        self.convertAvi2Mp4(videopath, videopath[:-3] + "mp4")
        return videopath[:-3] + "mp4"

    def addText2Video(self, videopath, texts):
        textVideo = videopath[:-4] + "-withtext.mp4"
        print("addText2Video", videopath, "textVideo", textVideo)
        video = cv2.VideoCapture(videopath)
        fps_video = video.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        videoWriter = cv2.VideoWriter(textVideo, fourcc, fps_video, (frame_width, frame_height))
        frame_id = 0
        perLineWord = 10
        lines = int(len(texts) / perLineWord)

        while (video.isOpened()):
            ret, frame = video.read()
            if ret == True:
                textbegin = frame_id * perLineWord
                textend = min((frame_id + 1) * perLineWord, len(texts))
                showtext = texts[textbegin:textend].decode('utf-8')
                print("-----------------[%d:%d]---------" % (textbegin, textend))
                print(showtext)
                frame_id += 1
                word_x = frame_width / 3
                word_y = frame_height - 20
                #cv2.rectangle(frame, (left_x_up, left_y_up), (right_x_down, right_y_down), (55,255,155), 5)
                #cv2.putText(frame, '第%s张照片' % frame_id, (word_x, word_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (55,255,155), 1)
                frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(frame)
                #fontText = ImageFont.truetype("simsun.ttc", 20, encoding="utf-8")
                fontText = ImageFont.truetype("simsun.ttc", 20)
                #draw.text((word_x, word_y), showtext, (255, 255, 255), font=fontText)
                draw.text((word_x, word_y), showtext, fill=(0, 0, 0, 0), font=fontText)
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

    def text2Audio(self, text):
        audiopath = r'E:\test-res\%s-audio.mp3' % (self.name)
        if os.path.exists(audiopath):
            duration = librosa.get_duration(filename=audiopath)
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
        return audiopath, duration

def main():
    return

def test():
    return

if __name__ == "__main__":
    news2video = News2Video("http://www.cankaoxiaoxi.com/photo/20200306/2403795.shtml")
    #news2video.getTextAndPicFromUrl()
    texts, pics = news2video.getTextAndPicFromUrl()
    audiopath, duration = news2video.text2Audio(texts)
    print("Audio Generate over, name:%s duration:%d" % (audiopath, duration))
    videopath = news2video.generateVideo(pics, duration)
    print("Video Generate over, name:%s duration:%d" % (videopath, duration))
    videopath = news2video.addText2Video(videopath, texts)
    print("Text Adding over, name:%s duration:%d" % (videopath, duration))
    #videopath = news2video.addAudio2Video(videopath, audiopath)
    print("Audio Adding over, name:%s duration:%d" % (videopath, duration))
    #audiopath = news2video.text2Audio('欢迎使用百度语音只能服务')
    #news2video.changePicSize(r'E:\testimg\IMG_1615.JPG', 540, 720)
    #videopath = news2video.addAudio2Video(videopath, r'E:\test-res\test.mp3')
    #news2video.addAudio2Video(r'E:\test-res\test.mp4', r'E:\test-res\test.mp3')
    print("Final video name:%s" % (videopath))


    #test()
    #main()



