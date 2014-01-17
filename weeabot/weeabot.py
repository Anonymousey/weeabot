#!/usr/bin/python
# vim: set ts=2 expandtab:
"""

Module: weeabot.py
Desc: japanese dictionary IRC bot
Author: on_three
Email: on_three@outlook.com
DATE: Tuesday, Jan 14th 2013

Monitor IRC chat for posts starting with 'jisho'
and scrape following terms from jisho.org

Will implement simple japanese to english lookup and 
english to japanese lookup.
  
""" 

import os.path
import uuid
import sys
import time
from collections import defaultdict
import argparse
import string

from twisted.internet import task
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import ssl
from twisted.python import log
from twisted.words.protocols import irc as twisted_irc
import irc
import re

from twisted.web.client import getPage
from denshi_jisho import DenshiJisho
from jikan import Jikan

DEFAULT_PORT = 6660

#after http://stackoverflow.com/questions/938870/python-irc-bot-and-encoding-issue
def irc_decode(bytes):
  '''
  IRC character encoding can be arbitrary. python doesn't like this
  '''
  try:
    text = bytes.decode('utf-8')
  except UnicodeDecodeError:
    try:
      text = bytes.decode('iso-8859-1')
    except UnicodeDecodeError:
      text = bytes.decode('cp1252')
  return text


def irc_encode(bytes):
  '''
  IRC character encoding can be arbitrary. python doesn't like this
  '''
  try:
    text = bytes.encode('utf-8')
  except UnicodeEncodeError:
    try:
      text = bytes.encode('iso-8859-1')
    except UnicodeEncodeError:
      text = bytes.encode('cp1252')
  return text


class WeeaBot(twisted_irc.IRCClient):
  plugins = []

  def connectionMade(self):
    twisted_irc.IRCClient.connectionMade(self)
    WeeaBot.plugins.append(DenshiJisho(self))
    WeeaBot.plugins.append(Jikan(self))

  def connectionLost(self, reason):
    twisted_irc.IRCClient.connectionLost(self, reason)

  def signedOn(self):
    '''
    Called when we've connected to the IRC server.
    We can use this opportunity to communicate with nickserv
    if necessary
    '''
    network = self.factory.network

    if network['identity']['nickserv_password']:
      self.msg('NickServ', 
            'IDENTIFY %s' % network['identity']['nickserv_password'])

    for channel in network['autojoin']:
      print('join channel %s' % channel)
      self.join(channel)

  def joined(self, channel):
    '''
    Called when we've joined a channel. This is here used to
    Initialize a chat dialog on the screen that will later
    be updated with posts as the chat progresses.
    '''
    print 'WeeaBot::joined'

  def privmsg(self, user, channel, msg):
    '''
    Invoked upon receipt of a message in channel X.
    Give plugins a chance to handle it until one does
    '''
    msg = re.sub(' +',' ',msg)
    #msg = irc_decode(msg)
    for plugin in WeeaBot.plugins:
      if plugin.is_msg_of_interest(msg, channel):
        plugin.handle_msg(msg, channel)
        break

  def left(self, channel):
    pass

  def noticed(self, user, channel, message):
    pass

  def modeChanged(self, user, channel, set, modes, args):
    pass
    
  def kickedFrom(self, channel, kicker, message):
    pass

  def NickChanged(self, nick):
    pass

  def userJoined(self, user, channel):
    pass

  def userLeft(self, user, channel):
    pass

  def userQuit(self, user, quit_message):
    pass

  def userKicked(self, kickee, channel, kicker, message):
    pass

  def action(self, user, channel, data):
    pass

  def topicUpdated(self, user, channel, new_topic):
    pass

  def userRenamed(self, oldname, newname):
    pass

  def alterCollidedNick(self, nickname):
    return nickname+'_'

class WeeaBotFactory(protocol.ClientFactory):
  protocol = WeeaBot

  def __init__(self, network_name, network):
    self.network_name = network_name
    self.network = network

  def clientConnectionLost(self, connector, reason):
    connector.connect()

  def clientConnectionFailed(self, connector, reason):
    reactor.stop()


def split_server_port(hostname):
  port = DEFAULT_PORT
  if not ':' in hostname:
    return (hostname, DEFAULT_PORT)
  hostname, port = string.split(hostname, ':', maxsplit=1)
  try:
    port = int(port)
  except ValueError:
    port = DEFAULT_PORT
  return (hostname, port)


def main():
  parser = argparse.ArgumentParser(description='Scrape jisho.org for japanese word (romaji) lookup.')
  parser.add_argument('hostname', help='IRC server URL as domain:port (e.g. www.freenode.net:6660).', type=str)
  parser.add_argument('nickname', help='Nick to use at signon. Multiple nicks not yet supported.', type=str)
  parser.add_argument('channel', help='Channel to join on server. Only supporting one channel presently.', type=str)
  #parser.add_argument('-p','--server_port', help='Port this server will service html client requests on. NOT the IRC server port this server connects to.', type=int, default=8888)
  parser.add_argument('-u', '--username', help='Username this server uses at IRC server signon.', type=str, default='')
  parser.add_argument('-r', '--realname', help='Realname this server uses at IRC server signon.', type=str, default='')
  parser.add_argument('--password', help='Optional password this server uses at signon', type=str, default=None)
  parser.add_argument('--nickserv_pw', help='Optional password to use with nickserv after IRC server connect.', type=str, default=None)
  parser.add_argument('-v', '--verbose', help='Run server in verbose mode.', action="store_true")
  parser.add_argument('-s', '--ssl', help='Connect to server via SSL.', action="store_true")
  args = parser.parse_args()

  hostname, port = split_server_port(args.hostname)
  if args.verbose:
    print 'Connecting to ' + hostname + ' on port ' + str(port) +'.'
    
  credentials = {
    'nickname': args.nickname,
    'realname': args.realname if len(args.realname)>0 else args.nickname,
    'username': args.username if len(args.username)>0 else args.nickname,
    'password': args.password,
    'nickserv_password': args.nickserv_pw
  }
  #we've got to add thise to the client, which is odd as fuq
  WeeaBot.nickname = credentials['nickname']
  WeeaBot.realname = credentials['realname']
  WeeaBot.username = credentials['username']
  WeeaBot.password = credentials['password']
    
  channels = (args.channel,)

  network = {
    'host': hostname,
    'port': port,
    'ssl': args.ssl,
    'identity': credentials,
    'autojoin': channels
  }


  factory = WeeaBotFactory(hostname, network)
  if args.ssl:
    reactor.connectSSL(hostname, port, factory, ssl.ClientContextFactory())
  else:
    reactor.connectTCP(hostname, port, factory)

  reactor.run()


if __name__ == "__main__":
  log.startLogging(sys.stdout)
  main()
