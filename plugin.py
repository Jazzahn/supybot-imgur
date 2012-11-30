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
        parsed_url = requests.utils.urlparse(full_url)
        imgur_hash = parsed_url.path.split("/")[-1].split(".")[0]
        return imgur_hash

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

    @classmethod
    def imgur(cls, irc, msg, args):
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
