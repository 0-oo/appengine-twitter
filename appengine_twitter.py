#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
AppEngine-Twitter

Twitter API wrapper for applications on Google App Engine

See: http://0-oo.net/sbox/python-box/appengine-twitter
License: http://0-oo.net/pryn/MIT_license.txt (The MIT license)

See also:
  https://dev.twitter.com/docs/api
  https://developers.google.com/appengine/docs/python/urlfetch/?hl=ja
'''

__author__ = 'dgbadmin@gmail.com'
__version__ = '0.4.0'


import json
import urllib
from appengine_oauth import AppEngineOAuth
from google.appengine.api import urlfetch


class AppEngineTwitter(object):

  def __init__(self):
    self._api_url = 'https://api.twitter.com/1.1/'
    self._oauth_url = 'https://api.twitter.com/oauth/'
    self._oauth = None
    self._tw_name = ''


  def update(self, message):
    '''
    Post a tweet
    Sucess => Retrun 200 / Fialed => Return other HTTP status
    '''
    return self._post('statuses/update.json', {'status': message})


  def retweet(self, tweet_id):
    '''
    ReTweet a tweet
    Sucess => Retrun 200 / Fialed => Return other HTTP status
    '''
    return self._post('statuses/retweet/' + tweet_id + '.json', {})


  def follow(self, target_name):
    '''
    Sucess => Return 200 / Already following => Return 403 /
    Fialed => Return other HTTP status
    '''
    return self._post('friendships/create.json', {'screen_name': target_name})


  def is_following(self, target_name):
    '''
    Yes => Return True / No => Return False /
    Fialed => Return HTTP status except 200
    '''
    if self._tw_name == '':
      self.verify()
      user_info = json.loads(self.last_response.content)
      self._tw_name = user_info['screen_name']

    status = self._get('friendships/exists.json',
                       {'user_a': self._tw_name, 'user_b': target_name})
    if status == 200:
      return (self.last_response.content == 'true')
    else:
      return status


  def verify(self):
    '''
    Verify user_name and password, and get user info
    Sucess => Return 200 / Fialed => Return other HTTP status
    '''
    return self._get('account/verify_credentials.json', {})


  def search(self, keyword, params={}):
    '''
    Sucess => Return Array of dict / Fialed => raise an Exception
    '''
    params['q'] = keyword
    status = self._get('search/tweets.json', params)

    if status == 200:
      return json.loads(self.last_response.content)['statuses']
    else:
      raise Exception('Error: HTTP Status is ' + str(status))


  # OAuth methods
  # (See http://0-oo.net/sbox/python-box/appengine-oauth )

  def set_oauth(self, key, secret, acs_token='', acs_token_secret=''):
    '''
    Set OAuth parameters
    '''
    self._oauth = AppEngineOAuth(key, secret, acs_token, acs_token_secret)


  def prepare_oauth_login(self):
    '''
    Get request token, request token secret and login URL
    '''
    dic = self._oauth.prepare_login(self._oauth_url + 'request_token')
    dic['url'] = self._oauth_url + 'authorize?' + dic['params']
    return dic


  def exchange_oauth_tokens(self, req_token, req_token_secret):
    '''
    Exchange request token for access token
    '''
    return self._oauth.exchange_tokens(self._oauth_url + 'access_token',
                                       req_token,
                                       req_token_secret)


  # Private methods

  def _post(self, path, params):
    url = self._api_url + path
    params = self._oauth.get_oauth_params(url, params, 'POST')
    res = urlfetch.fetch(url=url, payload=urllib.urlencode(params), method='POST')
    self.last_response = res
    return res.status_code


  def _get(self, path, params):
    url = self._api_url + path
    if self._oauth != None:
      params = self._oauth.get_oauth_params(url, params, 'GET')
    url += '?' + urllib.urlencode(params)
    res = urlfetch.fetch(url=url, method='GET')
    self.last_response = res
    return res.status_code
