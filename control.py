#! /usr/bin/env python
import os
import sys
import shutil
import time
import smtplib
from   email.mime.text import MIMEText
configrlogs = []
mailparams  = ['kun.luo@intel.com', 'smtp.intel.com', 'kun.luo', 'intel.com']
mailtowho   = [['kun.luo@intel.com'],
               ['kun.luo@intel.com', 'jocelyn.li@intel.com', 'guangxin.xu@intel.com', 'jiankang.yu@intel.com']]
libyamiaddr = [['git://anongit.freedesktop.org/vaapi/libva',        'staging'],
               ['git://anongit.freedesktop.org/vaapi/intel-driver', 'staging'], 
               ['git://source.ffmpeg.org/ffmpeg.git', ' '],
               ['git://github.com/01org/libyami.git', ' ']]
libyamipara = [['./autogen.sh', 'VAAPI_PREFIX',   ' '],
               ['./autogen.sh', 'VAAPI_PREFIX',   ' '],
               ['./configure',  'VAAPI_PREFIX',   ' '],
               ['./autogen.sh', 'LIBYAMI_PREFIX', '--enable-tests --enable-tests-gles --enable-avformat']]
openmaxaddr = [['https://github.com/01org/omxil_core.git', ' '],
               ['https://github.com/01org/omx_comp.git',   ' '],
               ['https://github.com/01org/gst-omx.git',    ' ']]
openmaxpara = [['sh autogen.sh && ./configure','OMXCOMPONENT_PREFIX','--enable-libyami --enable-native-buffer=no --enable-vp8-role-name'],
               ['sh autogen.sh && ./configure','OMXCOMPONENT_PREFIX','--enable-libyami --enable-native-buffer=no --enable-vp8-role-name'],
               ['tsocks ./autogen.sh','GSTOMX_PREFIX','--with-omx-target=bellagio --with-omx-header-path=/opt/omx/omx/include/omx']]
gstreamaddr = [['git://anongit.freedesktop.org/gstreamer/gstreamer', '1.0'],
               ['git://anongit.freedesktop.org/gstreamer/gst-plugins-base', '1.0'],
               ['git://anongit.freedesktop.org/gstreamer/gst-plugins-bad',  '1.0']]
gstreampara = [['./autogen.sh', 'VAAPI_PREFIX', ''], 
               ['./autogen.sh', 'VAAPI_PREFIX', ''],
               ['./autogen.sh', 'VAAPI_PREFIX', '']]
v4l2configs = [['./autogen.sh', 'LIBYAMI_PREFIX', '--enable-tests --enable-v4l2 --enable-v4l2-glx --enable-avformat'],
               ['./autogen.sh', 'LIBYAMI_PREFIX', '--enable-tests --enable-capi  --enable-tests-gles --enable-dmabuf'],
               ['./autogen.sh', 'LIBYAMI_PREFIX', '--enable-tests --enable-tests-gles --enable-dmabuf --enable-avformat']]
def clone(addr, branch,cloneCmd):
    if branch == ' ':
        cloneCmd[0] = 'git clone ' + addr
    else:  
        cloneCmd[0] = 'git clone -b ' + branch + ' ' + addr
    return os.system(cloneCmd[0])
def build(dirname, param, buildCmd):
    currentpath = os.getcwd()
    os.chdir(dirname)
    buildCmd[0] = param[0] + ' --prefix=' + os.getenv(param[1]) + ' ' +  param[2] + ' && make -j8 && make install'
    state = os.system(buildCmd[0])
    os.chdir(currentpath)
    return state
def clone_build_addr(addrlist, paramlist):
    i = 0
    for addr in addrlist:
        cloneCmd = ['']
        buildCmd = ['']
        dirname = addr[0][(addr[0].rfind('/')+1):]
        if dirname.find('.') != -1:
            dirname = dirname[0:dirname.find('.')]
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        if clone(addr[0], addr[1], cloneCmd) != 0:
            configrlogs.append(cloneCmd[0])
            return False
        print(paramlist[i])
        print(buildCmd[0])
        if build(dirname, paramlist[i], buildCmd) != 0:
            configrlogs.append(buildCmd[0])
            return False
        i = i + 1
    return True
def send_mail(to_list, sub, content):
    me = 'luo kun'+'<'+mailparams[2]+'@'+mailparams[3]+'>'
    msg = MIMEText(content, _subtype='plain', _charset='gb2312')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ';'.join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mailparams[1])
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        print('send email success')
    except Exception, e:
        print str(e)
        print('send email fail')
def checkexists(testfiles):
    if os.path.exists(testfiles):
        return True
    return False
def yamitest(testfiles, formats, outputdir, savemode, *sendmode):
    if not checkexists(testfiles):
        return
    if formats == 'v4l2':
        for i in range(len(v4l2configs)):
            buildCmd = ['']
            if build('libyami', v4l2configs[i], buildCmd) != 0:
                configrlogs.append(buildCmd)
                sendconfigrlogs('v4l2 build failed')
                return
    rootpath = os.getcwd()
    testfiles = os.path.abspath(testfiles)    
    os.chdir('libyami/testscripts')
    currentpath = os.getcwd()
    os.system('./autotest.py '+testfiles+' '+formats+' '+outputdir+' '+str(savemode))
    if len(sendmode) != 0:
        sendtestlogs('log', currentpath, formats+' test', mailtowho[sendmode[0]])
    os.chdir(rootpath)
def sendtestlogs(logpath, currentpath, sub, emaillist):
    os.chdir(logpath)
    LastLogfileName = os.popen("ls -lrt | awk 'END{print $NF}'").read().rstrip()
    LastLogfileContent = open(LastLogfileName).read() 
    content = LastLogfileContent + '\n\nThanks,\nLuo Kun'
    send_mail(emaillist, sub, content)
    os.chdir(currentpath)
def sendconfigrlogs(sub, sendmode):
    content = ''
    for i in range(0, len(configrlogs)):
        content += configrlogs[i]
    send_mail(mailtowho[sendmode], sub, content)

if __name__=='__main__':
    if not clone_build_addr(libyamiaddr, libyamipara):
        sendconfigrlogs('yami dowload', 0)
        sys.exit(-1)
    if not os.path.exists('bat_video_content'):
        configrlogs.append('has no media files')
        sendconfigrlogs('yami test', 0)
        sys.exit(-1) 
    batvideocontent = os.path.abspath('bat_video_content')
    decodetestfiles = os.path.join(batvideocontent, 'mediafiles')
    decodeh264files = os.path.join(decodetestfiles, 'h264')
    encodetestfiles = os.path.join('libyami', 'testscripts/decodeh264yuv')
    v4l2testfiles   = os.path.join(batvideocontent,  'v4l2files')
    yamitest(decodetestfiles, 'decode', 'decodetestyuv', 0, 0)
    yamitest(decodeh264files, 'decode', 'decodeh264yuv', 1)
    yamitest(encodetestfiles, 'encode', 'encodetestyuv', 0, 0)
    yamitest(v4l2testfiles,   'v4l2',   'v4l2testyuv'  , 0, 0)
