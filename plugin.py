###
# Copyright (c) 2012, James Scott
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import requests


class Imgur(callbacks.Plugin):
    """Add the help for "@plugin help Imgur" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _lookUpHash(self, imgur_hash):
        albumService = 'http://imgur.com/gallery/%s.json'
        try:
            if imgur_hash is None or imgur_hash == '':
                return None
            response = requests.get(albumService % imgur_hash)
            if response.status_code == 200:
                return response.json['data']['image']
            else:
                return None
        except:
            return None
    
    @classmethod
    def _parse_url(cls, full_url):
        """
        Takes a URL and returns the Imgur hash
        """
        parsed_url = requests.utils.urlparse(full_url)
        imgur_hash = parsed_url.path.split("/")[-1].split(".")[0]
        return imgur_hash

    @classmethod
    def _extract_url(cls, text):
        prefix_map = ["https://", "http://", "imgur.com"]
        for prefix in prefix_map:
            if prefix in text:
                url = text[text.find(prefix):].split(" ")[0]
                return url
        return None

    def _build_reply_string(self, json):
        title = ""
        reddit = ""
        views = 0
        try:
            title = ircutils.bold(json["title"])
        except:
            pass
        try:
            views = ircutils.bold(json["views"])
        except:
            views = ircutils.bold('0')
        try:
            reddit = ircutils.bold(json["reddit"])
        except:
            reddit = ircutils.bold("n/a")

        return ('Title: %s  Views: %s  Reddit: %s  ' % (title, views, reddit))

    def _lookUpImgur(self, irc, msg):
        """
        Main function of the Imgur plugin. Pass it and
        """
        (recipients, text) = msg.args
        url = self._extract_url(text)
        imgur_hash = self._parse_url(url)
        imgur_json = self._lookUpHash(imgur_hash)
        if imgur_json:
            reply_string = self._build_reply_string(imgur_json)

            irc.reply(reply_string, prefixNick=False)

    def doPrivmsg(self, irc, msg):
        (recipients, text) = msg.args
        if "imgur.com" in text:
            self._lookUpImgur(irc, msg)
        else:
            pass

    @classmethod
    def _uploadImage(cls, key, url):
        uploadService = "http://api.imgur.com/2/upload.json"
        headers = {
            'key': key,
            'image': url
        }
        try:
            response = requests.post(uploadService, params=headers)
            if response.status_code == 200:
                return response.json['upload']['links']['original']
            else:
                return None
        except:
            return None

    def imgur(self, irc, msg, args):
        """imgur <url> returns a imgur url for the image passed to it."""
        if args[0] is None or args[0] == '':
            irc.reply(__doc__)
        elif self.registryValue('developer_key') is None:
            irc.reply("Set developer_key")
        elif "http://" in args[0] or "https://" in args[0]:
            key = self.registryValue('developer_key')
            irc.reply(self._uploadImage(key, args[0]))
        else:
            irc.reply("Something Bad Happend.")
        
Class = Imgur


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
