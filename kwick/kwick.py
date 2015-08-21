# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:50:30 2015

@author: Tilra
"""

import requests

version = 1.0  # Kwicks mapi version

class KwickError(Exception):

    def __init__(self, msg):
        self.msg = msg['errorMsg']
    
    def __str__(self):
        return repr(self.msg)

class Kwick(object):

    session = None
    cookie = None
    
    host = 'http://mapi.kwick.de/{version}'.format(version=version)
    response = None
    
    def __init__(self, session=None):
        if not session:
            self.session = requests.Session()
    
    def post(self, url, data, json=True):
        response = self.session.post(self.host + url, data)
        self.response = response
        if json:
            return response.json()
        return response.content
    
    def get(self, url, params=dict(), json=True):
        response = self.session.get(self.host + url, params=params)
        self.response = response
        if json:
            return response.json()
        return response.content
    
    def kwick_login(self, kwick_username, kwick_password):
        """
        Wenn erfolgreich:
            {'loggedIn': True,
             'session_id': 'ein hash',
             'session_name': 'a2K3j8G1',
             'userid': XXXXXXX}
        Der name der Session ist immer gleich
        """
        url = '/login'
        data = dict(
            kwick_username=kwick_username,
            kwick_password=kwick_password
        )
        json = self.post(url, data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
    
    def kwick_logout(self):
        """
        Von kwick ausloggen
        """
        url = '/logout'
        return self.get(url)
    
    # User-Service
    def kwick_index(self, page):
        """
        docs: http://developer.kwick.com/index.php/User/index
        """
        url = '/index'
        params = dict(
            page=page
        )
        return self.get(url, params=params)
        
    def kwick_infobox(self):
        url = '/infobox'
        return self.get(url)
    
    def kwick_user(self, username, page=0):
        url = '/{username}'.format(
            username=username
        )
        return self.get(url)
    
    # Feed Service
    def kwick_feed(self, feedid, delete=False):
        """
        docs: http://developer.kwick.com/index.php/Feed/feed
        docs: http://developer.kwick.com/index.php/Feed/feed/feedid/delete
        warning: veraltet
        """
        if delete:
            url = '/feed/{feedid}/delete'.format(feedid=feedid)
        else:
            url = '/feed/{feedid}'.format(feedid=feedid)
        return self.get(url)
    
    # Message Service
    def kwick_message(self, page=0, folder=None, sender=None, channel=0, delete=False, show=False):
        """
        folder: recv, sent, parked, spam
        default: recv
        """
        if delete:
            url = '/message/delete/{folder}/{sender}/{channel}'.format(
                folder=folder,
                sender=sender,
                channel=channel
            )
        if show:
            url = '/message/show/{folder}/{page}/{sender}/{channel}'.format(
                folder=folder,
                page=page,
                sender=sender,
                channel=channel
            )
        else:
            url = '/message/{page}/'.format(page=page)
            if page and folder:
                url = '/message/{page}/{folder}'.format(page=page, folder=folder)
                
        json = self.get(url)
        
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
    
    def kwick_message_send(self, receiver, msgtext):
        url = '/message/send'
        data = dict(
            receiver=receiver,
            msgText=msgtext,
        )
        json = self.post(url, data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
    
    def kwick_message_reply(self, receiver, channel, msgtext):
        url = '/message/sendReply'
        data = dict(
            receiver=receiver,
            channel=channel,
            msgText=msgtext,
        )
        
        json = self.post(url, data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_email(self, folder=None, page=0, delete=False):
        url = '/email/{page}/{folder}'.format(
            folder=folder,
            page=page
        )
        json = self.get(url)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
    
    def kwick_email_delete(self, folder, mailid):
        url = '/email/delete/{folder}/{mailid}'.format(
            folder=folder,
            mailid=mailid
        )
        json = self.get(url)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_email_show(self, folder, mailid):
        url = '/email/show/{folder}/{mailid}'.format(
            folder=folder,
            mailid=mailid
        )
        json = self.get(url)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
            
    def kwick_email_send(self, receiver, subject, content, 
                         folder=None, replymessage=None, forwardmessage=None):
        url = '/email/send'
        data = dict(
            receiver=receiver,
            subject=subject,
            content=content,
            folder=folder,
            replyMsg=replymessage,
            forwardMsg=forwardmessage
        )
        
        json = self.post(url, data=data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
    
    def kwick_email_contactsel(self, group=None, page=0):
        url = '/email/write/contactsel/{group}/{page}'.format(
            group=group,
            page=page
        )
        
        return self.get(url)