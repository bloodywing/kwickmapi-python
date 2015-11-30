# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:50:30 2015

Copyright (C) 2015  Bloodywing

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License

@author: bloodywing
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
    mobile_session = None
    cookie = None

    host = 'http://mapi.kwick.de/{version}'.format(version=version)
    mobile_host = 'http://m.kwick.de'
    response = None

    def __init__(self, session=None, mobile_session=None):
        if not session:
            self.session = requests.Session()
        if not mobile_session:
            self.mobile_session = requests.Session()

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

    def mobile_post(self, url, data, params=dict(), json=True):
        if json:
            params['__env'] = 'json'
        if data:
            data['jsInfo'] = 'true'
            data['browserInfo'] = 'requests # Version'
        response = self.mobile_session.post(self.mobile_host + url, data, params=params)
        self.response = response
        if json:
            return response.json()
        return response.content

    def mobile_get(self, url, params=dict(), json=True):
        if json:
            params['__env'] = 'json'
        response = self.mobile_session.get(self.mobile_host + url, params=params)
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
        self.kwick_mobilelogin(kwick_username, kwick_password)
        json = self.post(url, data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_mobilelogin(self, kwick_username, kwick_password):

        url = '/login'
        data = dict(
            kwick_username=kwick_username,
            kwick_password=kwick_password
        )
        json = self.mobile_post(url, data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_logout(self):
        """
        Von kwick ausloggen
        """
        url = '/logout'
        json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    # User-Service
    def kwick_index(self, page, community=False, json=True):
        """
        docs: http://developer.kwick.com/index.php/User/index
        """
        url = '/index'
        if community:
            url = '/index/community/'
        params = dict(
            page=page
        )
        return self.mobile_get(url, params=params, json=json)

    def kwick_setstatus(self, statustext=None):
        url = '/index/setStatus'

        data = dict(
            statusText=statustext,
        )

        json = self.post(url, data=data)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_socialobject_delete(self, type, id):
        """
        This is not in the docs
        """
        url = '/socialobject/{type}/{id}/delete'.format(
            type=type,
            id=id
        )
        return self.mobile_get(url)

    def kwick_infobox(self):
        url = '/infobox'
        return self.get(url)

    def kwick_user(self, username, page=0, json=True):
        url = '/{username}'.format(
            username=username
        )
        return self.mobile_get(url, json=json)

    # Feed Service
    def kwick_feed(self, feedid, delete=False):
        """
        docs: http://developer.kwick.com/index.php/Feed/feed
        docs: http://developer.kwick.com/index.php/Feed/feed/feedid/delete
        warning: doesn't work at all
        Kwick has replaced this with socialobjects
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
        elif show:
            url = '/message/show/{folder}/{page}/{sender}/{channel}'.format(
                folder=folder,
                page=page,
                sender=sender,
                channel=channel
            )
        else:
            url = '/message/{page}/'.format(page=page)
            if folder:
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

        json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_friends(self, page=0, group=None, showoffline=0):
        url = '/friends'
        params = dict(
            page=page,
            group=group,
            showOffline=showoffline
        )
        json = self.get(url, params=params)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_friendrequests(self, page=0):
        url = '/friends/requests/{page}'.format(
            page=page
        )
        json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_friendrequest(self, username, action, reason=None):
        """
        :parameter action accept|reject|create|withdraw
        """
        url = '/{username}/friendrequest/{action}'.format(
            username=username,
            action=action
        )

        if action == 'create':
            data = dict(reason=reason)
            json = self.mobile_post(url, data=data)
        else:
            json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_comment_create(self, type, id, text):
        """
        :parameter type Microblog|Profile_Photos_Photo|Profile_Blog_Entry|Profile_Change_Registration
        :parameter id userid___objectid Use the kwick_index() function for examples
        """

        url = '/socialobject/{type}/{id}/comment/create'.format(
            type=type,
            id=id,
        )
        data = dict(
            text=text
        )
        json = self.post(url, data=data)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_comments(self, type, id, limit=100, offset=0):
        url = '/socialobject/{type}/{id}/comment/find/{limit}/{offset}'.format(
            type=type,
            id=id,
            limit=limit,
            offset=offset,
        )

        json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_comment_delete(self, type, id, commentid):
        url = '/socialobject/{type}/{id}/comment/{commentid}/delete'.format(
            type=type,
            id=id,
            commentid=commentid
        )

        json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_like(self, type, id, dolike=1):
        """
        :parameter dolike 1|0 Removes like if 0
        """
        url = '/socialobject/{type}/{id}/like/{dolike}'.format(
            type=type,
            id=id,
            dolike=dolike
        )
        json = self.get(url)

        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json

    def kwick_search_members(self, online=None, age_from=1, age_to=99, distance=0,
                            single=None, haspic=None, gender=3, limit=100, offset=0):
        """
        :parameter gender 0|1|2
        :parameter limit Anything between 0 and 20
        Kwick Docs are wrong
        """
        url = '/search/members'
        params = locals()
        params.pop('self')
        params.pop('url')

        json = self.get(url, params=params)
        if 'errorMsg' in json:
            raise KwickError(json)
        else:
            return json
