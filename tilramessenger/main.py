# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 20:03:26 2015

Copyright (C) 2015  Tilra

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License

@author: Tilra
"""

from kwick import Kwick
import os
from concurrent.futures import ThreadPoolExecutor

from gi.repository import Gtk, GObject, Gdk, GLib
from .configuration import Configuration
from .user import User

config = Configuration()

kwick = Kwick()


def get_builder():
    curdir = os.path.dirname(os.path.abspath(__file__))
    builder = Gtk.Builder()
    builder.add_from_file(curdir + '/glade/main.glade')
    builder.connect_signals(handlers)
    return builder

class Messenger(GObject.GObject):
    users = []
    msgs = []
    msg = None
    userid = 0
    chatter = None
    channel = 0
    t = None
    old_msg = None
    sender_store = None

    is_loading_messages = GObject.property(type=bool, default=False)

    __gsignals__ = {
        'messages_loaded': (GObject.SIGNAL_RUN_FIRST, None, (bool,))
    }

    def __init__(self):
        super(Messenger, self).__init__()
        self.t = ThreadPoolExecutor(max_workers=1)

    def show_login(self, arg):
        d_user = builder.get_object('d_user')

        f_username = builder.get_object('f_username')
        f_password = builder.get_object('f_password')

        f_username.set_text(config['user/username'])
        f_password.set_text(config['user/password'])

        d_user.run()

    def close_login(self, *arg):
        d_user = builder.get_object('d_user')
        d_user.hide()

    def ok_login(self, *arg):
        f_username = builder.get_object('f_username')
        f_password = builder.get_object('f_password')

        config['user/username'] = f_username.get_text()
        config['user/password'] = f_password.get_text()
        self.close_login()

    def on_mainwindow_show(self, *arg):
        self.connect("messages_loaded", self.on_messages_loaded)
        self.sender_store = builder.get_object('sender_store')
        statusbar = builder.get_object('statusbar_mw')
        if len(config['user/username']) and len(config['user/password']):
            results = kwick.kwick_login(config['user/username'], config['user/password'])
            self.userid = results['userid']  # We need this for later use
            if results['loggedIn']:
                statusbar.push(0, 'Anmeldung erfolgreich als {username}'.format(username=config['user/username']))
                self.update_messages(True)

        GObject.timeout_add_seconds(5, self.update_messages)

    def update_messages(self, force_reload=False):
        self.job = self.t.submit(self.load_senders, force_reload=force_reload)
        self.job.add_done_callback(self.update_messages_finished)
        return True

    def update_messages_finished(self, job):
        results = job.result()
        if results:
            self.msgs = results
            self.emit('messages_loaded', True)
        return True

    def on_messages_loaded(self, widget, value):
        GLib.idle_add(widget.fill_treeview)

    def fill_treeview(self):
        self.sender_store.clear()
        for msg in self.msgs:
            self.sender_store.append(None, (msg['user']['username'], msg['channel'],))
            #self.sender_store.append(None, ('Dummy', 0,))
            #store.append(userrow, (str(msg['channel']),))
        return False

    def sendmessage(self, *args):
        text_buffer = builder.get_object('chatinputbuffer')
        start_iter = text_buffer.get_start_iter()
        end_iter = text_buffer.get_end_iter()
        msg = text_buffer.get_text(start_iter, end_iter, True)
        if self.msg:
            kwick.kwick_message_reply(self.chatter['username'], self.channel, msg)
            self.update_messages(force_reload=True)
        else:
            kwick.kwick_message_send(self.chatter['username'], msg)
            self.update_messages(force_reload=True)

    def inputfinished(self, textbuffer):
        pass

    def chatinput_key_pressed(self, widget, event):
        mods = Gtk.accelerator_get_default_mod_mask()
        if event.keyval == 65293 and event.get_state() & mods != Gdk.ModifierType.SHIFT_MASK:
            self.sendmessage()
            text_buffer = builder.get_object('chatinputbuffer')
            text_buffer.delete(text_buffer.get_start_iter(), text_buffer.get_end_iter())
            self.fill_chat_textbuffer()
            return True


    def hide_chatwindow(self, *args):
        chat = builder.get_object('chatwindow')
        chat.hide()
        return True

    def newmessage(self, *args):
        newsender = builder.get_object('newsender')
        username = newsender.get_text()

        user = kwick.kwick_user(username=username)
        if user:
            self.chatter = user['vcard']
        self.show_chatwindow()

    def show_chatwindow(self):
        chat = builder.get_object('chatwindow')
        chat.show_all()
        GObject.idle_add(self.fill_chat_textbuffer)

    def fill_chat_textbuffer(self):
        text = builder.get_object('sendertext')
        text_buffer = text.get_buffer()
        start_iter = text_buffer.get_start_iter()
        end_iter = text_buffer.get_end_iter()

        try:
            self.msg = [c for c in self.msgs if c['user']['username'] == self.chatter['username'] and c['channel'] == self.channel][0]
        except IndexError as e:
            """
            Empty Chat
            """
            text_buffer.delete(start_iter, end_iter)
            self.msg = None
            return True

        try:
            if self.msg['history'][0]['date'] == self.old_msg['date']:
                return True
        except TypeError as e:
            "Keine neuen Nachrichten"
            return True

        text_buffer.delete(start_iter, end_iter)
        for line in self.msg['history']:
            if int(line['sender']) != self.userid:
                sender = '[{sender}]: '.format(sender=self.msg['user']['username'])
            else:
                sender = '[{sender}]: '.format(sender=config['user/username'])

            text_buffer.insert(start_iter, sender + line['text'] + '\n\n')
        self.old_msg = self.msg['history'][0]
        return True

    def show_message(self):
        selection = builder.get_object('sender_selection')
        model, treeiter = selection.get_selected()
        if treeiter:
            username = model[treeiter][0]
            channel = model[treeiter][1]
            self.channel = channel
            self.msg = [c for c in self.msgs if c['user']['username'] == username and c['channel'] == channel][0]
            self.chatter = self.msg['user']
            self.show_chatwindow()

    def tree_sender_key_pressed(self, w, event):
        pressed, button = event.get_button()
        if button == 1 and pressed:
            self.show_message()

        if button == 3 and pressed:
            self.show_sender_contextmenu(w)

    def show_sender_contextmenu(self, widget):
        menu = builder.get_object('sender_menu')
        menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def delete_sender(self, selection):
        model, treeiter = selection.get_selected()
        username = model[treeiter][0]
        channel = model[treeiter][1]
        self.msg = [c for c in self.msgs if c['user']['username'] == username and c['channel'] == channel][0]
        userid = self.msg['msgid']
        kwick.kwick_message(folder='recv',
                                   sender=userid,
                                   channel=channel,
                                   delete=True)
        self.update_messages(force_reload=True)


    def load_senders(self, *args, force_reload=False):
        message_blob_recv = kwick.kwick_message(folder='recv')
        if not force_reload:
            try:
                newest_message = message_blob_recv['messages']['msgs'][0]
                if newest_message['conversation']['lastMessage'] == self.msgs[0]['conversation']['lastMessage']:
                    return False
            except IndexError as e:
                newest_message = None
            except KeyError as e:
                newest_message = None
        message_blob_sent = kwick.kwick_message(folder='sent')
        blobs = [message_blob_recv, message_blob_sent]
        msgs = []
        for blob in blobs:
            if 'maxPage' in blob:
                max_page = blob['maxPage']
            else:
                max_page = 1
            folder = blob['selected']
            for p in range(0, max_page):
                message_blob = kwick.kwick_message(page=p, folder=folder)
                if 'messages' in message_blob:
                    for msg in message_blob['messages']['msgs']:
                        msgs.append(msg)
        return msgs

messenger = Messenger()

handlers = {
    'on_mainwindow_destroy': Gtk.main_quit,
    'on_mainwindow_show': messenger.on_mainwindow_show,
    'on_show_login_activate': messenger.show_login,
    'on_d_user_delete_event':  messenger.close_login,
    'on_d_user_close': messenger.close_login,
    'on_b_cancel_clicked': messenger.close_login,
    'on_b_ok_clicked': messenger.ok_login,
    #'on_sender_selection_changed': messenger.show_message,
    'on_chatwindow_delete_event': messenger.hide_chatwindow,
    'on_sendchat_activate': messenger.sendmessage,
    'on_chatinputbuffer_end_user_action': messenger.inputfinished,
    'on_chatinput_key_press_event': messenger.chatinput_key_pressed,
    'on_tree_sender_button_release_event': messenger.tree_sender_key_pressed,
    'on_delete_activate': messenger.delete_sender,
    'on_b_sendmsg_activate': messenger.newmessage,
}

builder = get_builder()
window = builder.get_object('mainwindow')
window.show_all()

Gtk.main()
