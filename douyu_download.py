import os
import requests
from tqdm import tqdm
from multiprocessing import Pool
import re
from datetime import datetime

def get_m3u8(url):
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
               'X-Requested-With':'ShockwaveFlash/31.0.0.122'
               }
    res = requests.get(url,headers=headers).text
    with open('m3u8.txt','w') as file:
        file.write(res)
        file.close()

def get_url(url):
    with open('m3u8.txt','r') as file:
        line = file.readlines()
        file.close()
    a = len(line)
    url_1 = url.split('playlist.m3u8')[0]
    real_len = int((a - 6) / 2 - 1)
    k = 0
    dict = {}
    while k <= real_len:
        url_2 = line[6+2*k][:-2]
        real = url_1 + url_2
        dict[k] = real
        k = k+1
    url_list = list(dict.values())
    return(url_list)

def download_video(dict):
    filename = re.search('(\d{3})\.ts',dict).group(0)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'X-Requested-With': 'ShockwaveFlash/31.0.0.122'
        }
    req = requests.get(dict, headers=headers, stream=True)
    file_size = int(req.headers['content-length'])
    if os.path.exists(filename):
        first_byte = os.path.getsize(filename)
    else:
        first_byte = 0
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=filename)
    with(open(filename, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            f.write(chunk)
            #pbar.update(1024)
    pbar.update(file_size)
    pbar.close()
    f.close()

def ffmpeg(mp4_name):
    file = os.listdir('V:\\ts')
    with open("V:\\ts\\test.txt", "a") as txt:
        for i in file:
            if ".ts" in i:
                k = "file " + '\'' + i + '\'' + '\n'
                txt.write(k)
        txt.close()
    cmd = os.popen('ffmpeg -f concat -i test.txt -c copy %s.mp4' % mp4_name)
    info = cmd.readlines()
    for line in info:
        print(line)

def choice_1():
    mp4_name = input('输入文件名\n')
    if os.path.exists('./%s.mp4' % mp4_name):
        print('文件名已存在，请重新命名\n')
        mp4_name = input('输入文件名\n')
    url = input('请输入m3u8链接地址\n')
    get_m3u8(url)
    url_list = get_url(url)
    time_start = datetime.now()
    pool = Pool(5)
    pool.map(download_video, url_list)
    pool.close()
    time_finish = datetime.now()
    time_all = (time_finish - time_start).seconds
    print('总耗时  ' + str(time_all) + '\n')
    ffmpeg(mp4_name)
    cmd_finish = os.popen('del *.ts && del *.txt')
    #finish = input('输入任意键退出')


def choice_2():
    mp4_name = input('输入文件名\n')
    if os.path.exists('./%s.mp4' % mp4_name):
        print('文件名已存在，请重新命名\n')
        mp4_name = input('输入文件名\n')
    ffmpeg(mp4_name)
    cmd_finish = os.popen('del *.ts && del *.txt')
    #finish = input('输入任意键退出')


def choice_3():
    mp4_name = input('输入文件名\n')
    if os.path.exists('./%s.mp4' % mp4_name):
        print('文件名已存在，请重新命名\n')
        mp4_name = input('输入文件名\n')
    url = input('请输入m3u8链接地址\n')
    ts_len = input('请输入起始和结束时间，以/分割\n')
    ts_len = ts_len.split('/')
    ts_start = ts_len[0].split('.')
    ts_finish = ts_len[1].split('.')
    ts_start_location = int((int(ts_start[0])*3600 + int(ts_start[1])*60 + int(ts_start[2]))/10)
    ts_finish_location = int((int(ts_finish[0])*3600 + int(ts_finish[1])*60 + int(ts_finish[2]))/10)
    get_m3u8(url)
    url_list = get_url(url)[ts_start_location:ts_finish_location]
    time_start = datetime.now()
    pool = Pool(5)
    pool.map(download_video, url_list)
    pool.close()
    time_finish = datetime.now()
    time_all = (time_finish - time_start).seconds
    print('总耗时  ' + str(time_all) + '\n')
    ffmpeg(mp4_name)
    cmd_finish = os.popen('del *.ts && del *.txt')



if __name__ == "__main__" :
    print('1.下载加合成')
    print('2.只进行合成')
    print('3.进行切片下载')
    choice = int(input('请输入 1 或2 或3\n'))
    go_continue = 1
    while go_continue < 10:
        if choice == 1:
            choice_1()
        elif choice == 2:
            choice_2()
        elif choice == 3:
            choice_3()
        ifcontinue = int(input('继续请输入1，否则回车退出'))
        if ifcontinue == 1:
            go_continue = 1
        else:
            go_continue = 20
    finish = input('输入任意键退出')




