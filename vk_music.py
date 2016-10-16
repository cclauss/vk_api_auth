#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
py3 = sys.version_info[0] == 3

if py3:
   from urllib.request import urlopen
   from urllib.parse import urlencode
else:
   from urllib2 import urlopen 
   from urllib import urlencode

import vk_auth
import json
import os
import getpass

def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    data = urlopen(url).read()
    if py3:
       data = data.decode()
    return json.loads(data)["response"]

def get_audio(user_id, token, cnt):
    return call_api("audio.get", [("owner_id", user_id), ("count", cnt)], token)

def login_and_save():
   email = raw_input("Email: ")
   password = getpass.getpass()
   client_id = "2951857" # Vk application ID
   token, user_id = vk_auth.auth(email, password, client_id, "audio")

   f = open('token', 'w')
   f.write(token)
   f.close()

   f = open('user_id', 'w')
   f.write(user_id)
   f.close()

if __name__ == '__main__':
   import getopt

   def usage():
      print('vk_music.py [-l[list] <number of media to show>] [-u[rl]] [-i[d] <media id>] [-a[uth]]')

   try:
      opts, args = getopt.getopt(sys.argv[1:], "hul:i:", ['help', 'url', 'list=', 'id=', '--auth'])
   except getopt.GetoptError:
      usage()
      sys.exit(1)

   num = -1
   media_id = -1
   url = False
   for opt, arg in opts:
      if opt in ('-h', '--help'):
         usage()
         sys.exit(0)
      if opt in ('-l', '--list'):
         num = int(arg)
      elif opt in ('-i', '--id'):
         media_id = int(arg)
      elif opt in ('-u', '--url'):
         url = True
      elif opt in ('-a', '--auth'):
         os.remove('token')
         os.remove('user_id')

   if not os.path.exists('token') or not os.path.exists('user_id'):
      login_and_save()

   f = open('token', 'r')
   token = f.read()
   f.close()

   f = open('user_id', 'r')
   user_id = f.read()
   f.close()

   if num > 0:
      musics = get_audio(user_id, token, num)
      n = 0
      for i in musics:
          n += 1
          if not isinstance(i, dict):
             continue
          print("%d: %s - %s" % (n, i['artist'].encode(sys.stdout.encoding, errors='replace'), i['title'].encode(sys.stdout.encoding, errors='replace')))
   elif media_id > 0 and not url:
      musics = get_audio(user_id, token, media_id)
      print(musics[-1]['artist'].encode(sys.stdout.encoding, errors='replace'), '-', musics[-1]['title'].encode(sys.stdout.encoding, errors='replace'))
   elif media_id > 0 and url:
      musics = get_audio(user_id, token, 2 * media_id)
      n = 0
      for i in musics:
         n += 1
         if n == media_id:
            print(i['url'])
            break
