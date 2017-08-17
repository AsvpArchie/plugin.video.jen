# -*- coding: utf-8 -*-
"""
    xml.py --- functions dealing with jen xml list format
    Copyright (C) 2017, Midraal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

from resources.lib.util.url import replace_url, get_addon_url
from resources.lib.util.info import get_info
from resources.lib.util.context import get_context_items

import datetime
import time
import koding
import os
import xbmcaddon
import xbmc
import xbmcgui
from threading import Thread
import __builtin__
import urllib2

ADDON = xbmcaddon.Addon()


class JenList(object):
    """
wrapper class for jen list functions
    """

    list_pattern = re.compile(
        '((?:<item>.+?</item>|<dir>.+?</dir>|<plugin>.+?</plugin>'
        '|<info>.+?</info>|'
        '<name>[^<]+</name><link>[^<]+</link><thumbnail>[^<]+</thumbnail>'
        '<mode>[^<]+</mode>|'
        '<name>[^<]+</name><link>[^<]+</link><thumbnail>[^<]+</thumbnail>'
        '<date>[^<]+</date>))', re.MULTILINE | re.DOTALL)

    def __init__(self, url):
        if url.endswith(".xml"):
            request = urllib2.Request(replace_url(url))
            response = urllib2.urlopen(request)
            xml = response.read()
            response.close()
        else:
            xml = url
        if xml:
            self.xml = xml
            self.content = ""
            self.list = JenList.list_pattern.findall(xml)
            info = JenItem(xml.split('<item>')[0].split('<dir>')[0])
            self.playlister = info.get('poster', '0')
            self.list_image = replace_url(
                info.get('thumbnail', ADDON.getAddonInfo('icon')))
            self.list_fanart = replace_url(info.get('fanart', "0"))
            if self.list_fanart == "0":
                    self.list_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
            self.metadata = {}
        else:
            self.list = []

    def get_raw_list(self):
        """returns the raw xml list of items"""
        return self.list

    def get_list(self, input_list=None, skip_meta=False, skip_dialog=False):
        """
        returns the list of items in a format suitable for kodiswift
        Returns:
        list of jen items
        """
        items = []
        meta = ADDON.getSetting("metadata") == "true"
        try:
            is_widget = __builtin__.JEN_WIDGET
        except:
            is_widget = False
        if is_widget:
            skip_dialog = True
        if input_list is None:
            input_list = self.list

        xbmc.log("input_list: " + repr(input_list))

        dialog = None
        dialog2 = None

        if not skip_dialog:
            if ADDON.getSetting("disable_metadata_dialog") == "false":
                dialog = xbmcgui.DialogProgress()
                addon_name = ADDON.getAddonInfo("name")
                dialog.create(addon_name, "Loading items")

        if meta and not skip_meta:
            info_thread = threadWithReturn(
                target=get_info, args=(input_list, dialog))
            info_thread.start()
        else:
            info_thread = None

        num_items = len(input_list)
        for index, item_xml in enumerate(input_list):
            if dialog2:
                percent = ((index + 1) * 100) / num_items
                dialog2.update(percent, "processing item",
                               "%s of %s" % (index + 1, num_items))
            result_item = self.process_item(item_xml)
            if result_item:
                items.append(result_item)
        if dialog2:
            dialog2.close()

        if info_thread:
            info = info_thread.join()  # wait till for thread to finish
            if info:
                skip = 0
                for index, item in enumerate(items):
                    if not item.get("imdb", None):
                        continue
                    if index <= len(info) - 1:
                        for info_item in info[index + skip:]:
                            if "imdb_id" in info_item:
                                if info_item["imdb_id"] == item["imdb"]:
                                    item["info"].update(info_item)
                                    break
                                else:
                                    skip = skip + 1
                            else:
                                break
                    else:
                        break
        if ADDON.getSetting("trailer_context") == "true":
            for item in items:
                if "trailer" in item["info"]:
                    item["context"].append(("Trailer", "PlayMedia({0})".format(
                        item["info"]["trailer"])))
        return items

    def process_item(self, item_xml):
        try:
            is_widget = __builtin__.JEN_WIDGET
        except:
            is_widget = False
        item = JenItem(item_xml)
        enable_gifs = xbmcaddon.Addon().getSetting('enable_gifs') == "true"
        if item.item_string.startswith("<item>"):
            title = item["title"]
            if title == "":
                title = item["name"]
            try:
                title = xbmcaddon.Addon().getLocalizedString(int(title))
            except ValueError:
                pass
            is_playable = True
            mode = "get_sources"
            link = item_xml
        elif item.item_string.startswith("<dir>"):
            title = item["name"]
            if title == "":
                title = item["title"]
            try:
                title = xbmcaddon.Addon().getLocalizedString(int(title))
            except ValueError:
                pass

            if item["link"].startswith("message"):
                is_playable = True
                mode = "message"
                link = item["link"].replace("message(", "")[:-1]
                if link.startswith("http"):
                    text = koding.Open_URL(replace_url(link))
                    link = text
            else:
                is_playable = False
                mode = "get_list"
                link = item["link"]
        elif item.item_string.startswith("<plugin>"):
            link = item["link"]
            title = item["name"]
            if title == "":
                title = item["title"]
            try:
                title = xbmcaddon.Addon().getLocalizedString(int(title))
            except ValueError:
                pass
            if link.endswith("openSettings"):
                is_playable = True
                link = ""
                mode = "Settings"
            elif link.endswith("developer"):
                is_playable = False
                link = '{"file_name":"testings.xml"}'
                mode = "Testings"
                path = xbmcaddon.Addon().getAddonInfo('profile')
                profile_path = xbmc.translatePath(path).decode('utf-8')
                test_file = os.path.join(profile_path, "testings.xml")
                if not os.path.exists(test_file):
                    return
            else:
                if "youtube" in link and ("user" in link or "playlist" in link):
                    is_playable = True
                    mode = 'get_sources'
                    link = item_xml
                else:
                    is_playable = True
                    mode = 'get_sources'
                    link = item_xml
        else:
            xbmc.log("other: " + repr(item), xbmc.LOGDEBUG)
            raise Exception()

        # filter out "unreleased"
        if title == "" or " /title" in title or "/ title" in title:
            return

        if is_widget:
            if mode == "message":
                return

        context = get_context_items(item)

        content = item["content"]
        if content == "boxset":
            content = "set"
        if content != '':
            self.content = content
        imdb = item["imdb"]
        season = item["season"] or '0'
        episode = item["episode"] or '0'
        year = item["year"] or '0'
        fanart = None
        if enable_gifs:
            fan_url = item.get("animated_fanart", "")
            if fan_url and fan_url != "0":
                fanart = replace_url(fan_url)
        if not fanart:
            fanart = replace_url(
                item.get("fanart", self.list_fanart), replace_gif=False)
        thumbnail = None
        if enable_gifs:
            thumb_url = item.get("animated_thumbnail", "")
            if thumb_url and thumb_url != "0":
                thumbnail = replace_url(thumb_url)
        if not thumbnail:
            thumbnail = replace_url(
                item.get("thumbnail", self.list_image), replace_gif=False)

        premiered = item.get("premiered", "")
        if premiered:
            try:
                today_tt = datetime.date.today().timetuple()
                premiered_tt = time.strptime(premiered, "%Y-%m-%d")
                if today_tt < premiered_tt:
                    title = "[COLORyellow]" + title + "[/COLOR]"
            except:
                xbmc.log("wrong premiered format")
                pass
        result_item = {
            'label': title,
            'icon': thumbnail,
            'fanart': fanart,
            'mode': mode,
            'url': link,
            'folder': not is_playable,
            'imdb': imdb,
            'content': content,
            'season': season,
            'episode': episode,
            'info': {},
            'year': year,
            'context': context
        }
        if fanart:
            result_item["properties"] = {'fanart_image': fanart}
            result_item['fanart_small'] = fanart

        if content in ['movie', 'episode']:
            # only add watched data for applicable items
            result_item['info']['watched'] = 0
        return result_item

    def get_content_type(self):
        """return content type of list"""
        if self.content in ["movie", "set"]:
            return "movies"
        elif self.content == "tvshow":
            return "tvshows"
        elif self.content == "season":
            return "seasons"
        elif self.content == 'episode':
            return "episodes"
        else:
            return "files"


class JenItem(object):
    """represents an item in a jen xml list"""

    def __init__(self, item_xml):
        self.item_string = item_xml

    def get_tag_content(self, tag):
        """
        parses xml string for the content of a tag
        Args:
            collection: xml to search through
            tag: tag to find the content in
            default: value to return if nothing found
        Returns:
            tag content or default value if content is not found
        """
        return re.findall('<%s>(.+?)</%s>' % (tag, tag), self.item_string,
                          re.MULTILINE | re.DOTALL)

    def keys(self):
        """returns all keys in item"""
        return re.findall("<([^/]+?)>", self.item_string)[1:]

    def get(self, tag, default):
        """proxy for get_tag_content"""
        try:
            return self.get_tag_content(tag)[0]
        except IndexError:
            return default

    def getAll(self, tag):
        "get all tags contents" ""
        return self.get_tag_content(tag)

    def __getitem__(self, item):
        return self.get(item, "")

    def __eq__(self, other):
        return bool(self.item_string == other.item_string)

    def __repr__(self):
        return self.item_string


def display_list(items, content_type):
    "display jen list in kodi"
    import xbmcplugin
    import sys
    if content_type == "seasons":
        import pickle
        context_items = []
        if ADDON.getSetting("settings_context") == "true":
            context_items.append(("Settings",
                                 "RunPlugin({0})".format(
                                     get_addon_url("Settings"))))
        url = []
        for item in items:
            url.append(item["url"])
        koding.Add_Dir(
            name="All Episodes",
            url=pickle.dumps(url),
            mode="all_episodes",
            folder=True,
            icon=ADDON.getAddonInfo("icon"),
            fanart=ADDON.getAddonInfo("fanart"),
            context_items=context_items,
            content_type="video")
    for item in items:
        context_items = []
        if ADDON.getSetting("settings_context") == "true":
            context_items.append(("Settings",
                                 "RunPlugin({0})".format(
                                     get_addon_url("Settings"))))
        context_items.extend(item["context"])
        koding.Add_Dir(
            name=item["label"],
            url=item["url"],
            mode=item["mode"],
            folder=item["folder"],
            icon=item["icon"],
            fanart=item["fanart"],
            context_items=context_items,
            content_type="video",
            info_labels=item["info"],
            set_property=item["properties"],
            set_art={"poster": item["icon"]})
        xbmcplugin.setContent(int(sys.argv[1]), content_type)


class threadWithReturn(Thread):
    def __init__(self, *args, **kwargs):
        super(threadWithReturn, self).__init__(*args, **kwargs)

        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self, *args, **kwargs):
        super(threadWithReturn, self).join(*args, **kwargs)

        return self._return

#  LocalWords:  nfl
