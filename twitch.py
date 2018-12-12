import os
import requests
from tqdm import tqdm
from multiprocessing import Pool
import re
from datetime import datetime

def get_cookie():
   cookies = 'your cookies'
   cookies = cookies.split(';')
   cookie_dict = {}
   for i in cookies:
      k = i.split('=')
      cookie_dict[k[0]] = k[1]
   return(cookie_dict)

def get_auth(cookie,url_n):
   number = re.search('videos/(.*)',url_n).group(1)
   url = 'https://api.twitch.tv/api/vods/{}/access_token?need_https=true&oauth_token=1g2v92syz7xcxadplbw2vx7zmowoe4&platform=web&player_backend=mediaplayer'.format(number)
   headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
      'Origin': 'https://www.twitch.tv',
      'client-id':'client-id: jzkbprff40iqj646a697cyrvl0zt2m6'
   }
   res = requests.get(url,headers=headers,cookies=cookie).text
   sig = re.search("sig\":\"(.*?)\"",res).group(1) #sign码
   expires = re.search('expires\S{3}(\d{10}),',res).group(1) #10时间戳
   return([sig,expires,number])


def get_m3u8_url(auth):
   url_0 = 'https://usher.ttvnw.net/vod/{}.m3u8?allow_source=true&baking_bread=true&baking_brownies=true&baking_brownies_timeout=1050&nauth=%7B%22authorization%22%3A%7B%22forbidden%22%3Afalse%2C%22reason%22%3A%22%22%7D%2C%22chansub%22%3A%7B%22restricted_bitrates%22%3A%5B%5D%7D%2C%22device_id%22%3A%22mspJeBtPxmA0QflOSWZeAUrbT1oRUfNH%22%2C%22expires%22%3A{}%2C%22https_required%22%3Atrue%2C%22privileged%22%3Afalse%2C%22user_id%22%3A141459420%2C%22version%22%3A2%2C%22vod_id%22%3A{}%7D&nauthsig={}'.format(auth[2],auth[1],auth[2],auth[0])
   url_1 = '&player_backend=mediaplayer&playlist_include_framerate=true&reassignments_supported=true&rtqos=control&cdm=wv'
   url = url_0 + url_1
   headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
      'Origin': 'https://www.twitch.tv'
   }
   res = requests.get(url,headers=headers).text
   video_quality = re.findall(r'VIDEO=\"(.*?)\"', res)
   video_m3u8 = re.findall('https(.*?)m3u8', res)
   for i in range(len(video_m3u8)):
       video_m3u8[i] = 'https' + video_m3u8[i] + 'm3u8'
   for i in range(len(video_quality)):
      print(str(i+1) + '  %s'%(video_quality[i]))
   sequence_num = int(input('请输入下载视频质量的序号\n'))
   m3u8_url = video_m3u8[sequence_num-1]
   print(m3u8_url)
   return(m3u8_url)

def get_ts(url):
    headers = {
        'Accept': 'application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain',
        'Origin': 'https://www.twitch.tv',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
    }
    res = requests.get(url,headers=headers).text
    with open('m3u8.txt','w') as file:
        file.write(res)
        file.close()

def get_download_url(url):
    with open('m3u8.txt','r') as file:
        line = file.readlines()
        file.close()
    a = len(line)
    url_1 = url.split('index-dvr.m3u8')[0]
    real_len = int((a - 8) / 2 - 1)
    k = 0
    dict = {}
    while k <= real_len:
        url_2 = line[9+2*k][:-1]
        real = url_1 + url_2
        dict[k] = real
        k = k+1
    url_list = list(dict.values())
    return(url_list)

def download_video(dict):
    filename = re.search('(\d{1,5})\.ts',dict).group(0)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Origin':'https://www.twitch.tv'
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
    file = os.listdir('./')
    with open("./test.txt", "a") as txt:
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
    url = input('请输入视频链接地址\n')
    auth = get_auth(cookie, url)
    m3u8 = get_m3u8_url(auth)
    get_ts(m3u8)
    url_list = get_download_url(m3u8)
    time_start = datetime.now()
    pool = Pool(8)
    pool.map(download_video, url_list)
    pool.close()
    time_finish = datetime.now()
    time_all = (time_finish - time_start).seconds
    print('总耗时  ' + str(time_all) + '\n')
    ffmpeg(mp4_name)
    cmd_finish = os.popen('del *.ts && del *.txt')
    finish = input('输入任意键退出')


def choice_2():
    mp4_name = input('输入文件名\n')
    if os.path.exists('./%s.mp4' % mp4_name):
        print('文件名已存在，请重新命名\n')
        mp4_name = input('输入文件名\n')
    ffmpeg(mp4_name)
    cmd_finish = os.popen('del *.ts && del *.txt')
    finish = input('输入任意键退出')



if __name__ == "__main__" :
    print('1.下载加合成')
    print('2.只进行合成')
    choice = int(input('请输入 1或2 \n'))
    cookie = get_cookie()
    if choice == 1:
        choice_1()
    elif choice == 2:
        choice_2()






