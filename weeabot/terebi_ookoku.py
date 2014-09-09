# vim: set ts=2 expandtab:
# -*- coding: utf-8 -*-
"""

Module: terebi_ookoku.py
Desc: scrape tv.so-net.ne.jp for data
Author: on_three
Email: on.three.email@gmail.com
DATE: Thursday, September 4th 2014
  
"""
from bs4 import BeautifulSoup
import string
import re
import romkan
from twisted.python import log

'''

Content we're scraping is of the form:

<h1 class="basicContTitle">番組情報</h1>
				<dl class="basicTxt">
					<dd> 石田とあさくら　<a href="/webSearch.action?query=%E7%9F%B3%E7%94%B0%E3%81%A8%E3%81%82%E3%81%95%E3%81%8F%E3%82%89" target="_blank" class="linkArrowA">ウェブ検索</a></dd>
					<dd>
					    9/7 (Sun) 12:40 ～ 13:00&nbsp;（20分）
					  <a class="linkArrowA" href="/chartFromSchedule.action?id=400670201409071240">この時間帯の番組表</a>
					</dd>
					<dd>アニマックス HD(Ch.670)</dd>
					<dd><a href="/schedulesBySearch.action?condition.genres[0].id=107000">アニメ／特撮</a> - <a href="/schedulesBySearch.action?condition.genres[0].id=107100">国内アニメ</a></dd>
				</dl>
</h1>

'''

def elipsize(string, max_length=128, elipsis='...'):
  '''
  cap string at max X characters.
  If they exceed X, truncate with elipsis '...'
  '''
  if len(string)>max_length:
    string = string[:max_length-len(elipsis)]+elipsis
  return string

def scrape_tv_schedule(html):
  '''
  Extract curretn program name and running time from html.
  '''
  result = u'何？Wakarimasen aniki.'
  try:
    soup = BeautifulSoup(html)
    content_block = soup('dl', {'class' : 'basicTxt'})[0]
    name = content_block.contents[1].text.strip()
    #remove un needed content and strip again
    name = re.sub(u'ウェブ検索', u'', name).strip()
    time = unicode(content_block.contents[3].text)
    time = re.sub(u'この時間帯の番組表', u'', time)
    #there appears to be a bug in string.strip() in unicode whereby numerals can be stripped
    #so we strip here via regex
    time = re.sub(u'^[\D]+',u' ', time)
    time = time.rstrip()

    #log.msg(u'title: {name}'.format(name=name).encode('utf-8'))
    #log.msg(u'time : {time}'.format(time=time).encode('utf-8'))

    result = u'{name} \x035|\u000f\x032{time}\u000f\x035|\u000f'.format(name=name, time=time)
  except:
    log.err()
  return result




