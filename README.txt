Table of Contents
_________________

1 Steps needed to get a working addon
.. 1.1 change addon.xml
.. 1.2 change the jen folder name
.. 1.3 fill out variables
.. 1.4 OPTIONAL if your xmls don't end in xml change resources/lib/util/xml.py
.. 1.5 OPTIONAL change the replace_url function in resources/lib/util/url.py
2 XML Formats for Jen
.. 2.1 Main Directories
.. 2.2 Movies
.. 2.3 TV Directories
.. 2.4 TV Seasons
.. 2.5 TV Episodes
.. 2.6 Youtube Channels


1 Steps needed to get a working addon
=====================================

1.1 change addon.xml
~~~~~~~~~~~~~~~~~~~~

  change the addon id and name and anything else you need to suit your
  addon


1.2 change the jen folder name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  change it to reflect the addon id you assigned in step 1. not really
  needed while developing, but important before doing the first release
  so you don't overwrite any other addons using Jen


1.3 fill out variables
~~~~~~~~~~~~~~~~~~~~~~

  fill out these lines in default.py
  ,----
  | root_xml_url = "http://"  # url of the root xml file
  | __builtin__.tvdb_api_key = ""  # tvdb api key
  | __builtin__.tmdb_api_key = ""  # tmdb api key
  | __builtin__.trakt_client_id = ""  # trakt client id
  | __builtin__.trakt_client_secret = ""  # trakt client secret
  `----


1.4 OPTIONAL if your xmls don't end in xml change resources/lib/util/xml.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  change the following code in __init__
  ,----
  | if url.endswith(".xml"):
  |     request = urllib2.Request(replace_url(url))
  |     response = urllib2.urlopen(request)
  |     xml = response.read()
  |     response.close()
  | else:
  |     xml = url
  `----
  to
  ,----
  | request = urllib2.Request(replace_url(url))
  | response = urllib2.urlopen(request)
  | xml = response.read()
  | response.close()
  `----


1.5 OPTIONAL change the replace_url function in resources/lib/util/url.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  add any url replacing functions here. this shouldn't usualy be
  necesary


2 XML Formats for Jen
=====================

2.1 Main Directories
~~~~~~~~~~~~~~~~~~~~

  ,----
  | <dir>
  |         <name></name>
  |         <link></link>
  |         <animated_thumbnail></animated_thumbnail>
  |         <thumbnail></thumbnail>
  |         <animated_fanart></animated_fanart>
  |         <fanart></fanart>
  | </dir>
  `----


2.2 Movies
~~~~~~~~~~

  ,----
  | <item>
  |         <title></title>
  |         <meta>
  |                 <content>movie</content>
  |                 <imdb></imdb>
  |                 <title></title>
  |                 <year></year>
  |         </meta>
  |         <link>
  |                 <sublink>search</sublink>
  |                 <sublink>searchsd</sublink>
  |         </link>
  |         <animated_thumbnail></animated_thumbnail>
  |         <thumbnail></thumbnail>
  |         <animated_fanart></animated_fanart>
  |         <fanart></fanart>
  | </item>
  `----


2.3 TV Directories
~~~~~~~~~~~~~~~~~~

  ,----
  | <dir>
  |         <title></title>
  |         <meta>
  |                 <content>tvshow</content>
  |                 <imdb></imdb>
  |                 <tvdb></tvdb>
  |                 <tvshowtitle></tvshowtitle>
  |                 <year></year>
  |         </meta>
  |         <link></link>
  |         <animated_thumbnail></animated_thumbnail>
  |         <thumbnail></thumbnail>
  |         <animated_fanart></animated_fanart>
  |         <fanart></fanart>
  | </dir>
  `----


2.4 TV Seasons
~~~~~~~~~~~~~~

  ,----
  | <dir>
  |         <name></name>
  |         <meta>
  |                 <content>season</content>
  |                 <imdb></imdb>
  |                 <tvdb></tvdb>
  |                 <tvshowtitle></tvshowtitle>
  |                 <year></year>
  |                 <season></season>
  |         </meta>
  |         <link></link>
  |         <animated_thumbnail></animated_thumbnail>
  |         <thumbnail></thumbnail>
  |         <animated_fanart></animated_fanart>
  |         <fanart></fanart>
  | </dir>
  `----


2.5 TV Episodes
~~~~~~~~~~~~~~~

  ,----
  | <item>
  |         <title></title>
  |         <meta>
  |                 <content>episode</content>
  |                 <imdb></imdb>
  |                 <tvdb></tvdb>
  |                 <tvshowtitle></tvshowtitle>
  |                 <year></year>
  |                 <title></title>
  |                 <premiered></premiered>
  |                 <season></season>
  |                 <episode></episode>
  |         </meta>
  |         <link>
  |                 <sublink>search</sublink>
  |                 <sublink>searchsd</sublink>
  |         </link>
  |         <animated_thumbnail></animated_thumbnail>
  |         <thumbnail></thumbnail>
  |         <animated_fanart></animated_fanart>
  |         <fanart></fanart>
  | </item>
  `----


2.6 Youtube Channels
~~~~~~~~~~~~~~~~~~~~

  ,----
  | <plugin>
  |   <title></title>
  |   <link>plugin://plugin.video.youtube/channel/***CHANNEL NUMBER HERE***/playlists/</link>
  |   <animated_thumbnail></animated_thumbnail>
  |   <thumbnail></thumbnail>
  |   <animated_fanart></animated_fanart>
  |   <fanart></fanart>
  | </plugin>
  `----
