# Copyright: Ankitects Pty Ltd and contributors
# -*- coding: utf-8 -*-
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from __future__ import annotations

from typing import Any, Optional

import aqt
from anki.lang import _
from aqt.qt import *
from aqt.webview import AnkiWebView


# wrapper class for set_bridge_command()
class TopToolbar:
    def __init__(self, toolbar: Toolbar):
        self.toolbar = toolbar


# wrapper class for set_bridge_command()
class BottomToolbar:
    def __init__(self, toolbar: Toolbar):
        self.toolbar = toolbar


class Toolbar:
    def __init__(self, mw: aqt.AnkiQt, web: AnkiWebView) -> None:
        self.mw = mw
        self.web = web
        self.link_handlers = {
            "decks": self._deckLinkHandler,
            "study": self._studyLinkHandler,
            "add": self._addLinkHandler,
            "browse": self._browseLinkHandler,
            "stats": self._statsLinkHandler,
            "sync": self._syncLinkHandler,
        }
        self.web.setFixedHeight(30)
        self.web.requiresCol = False

    def draw(
        self,
        buf: str = "",
        web_context: Optional[Any] = None,
        link_handler: Optional[Callable[[str], Any]] = None,
    ):
        web_context = web_context or TopToolbar(self)
        link_handler = link_handler or self._linkHandler
        self.web.set_bridge_command(link_handler, web_context)
        self.web.stdHtml(
            self._body % self._centerLinks(), css=["toolbar.css"], context=web_context,
        )
        self.web.adjustHeightToFit()
        if self.mw.media_syncer.is_syncing():
            self.set_sync_active(True)

    # Available links
    ######################################################################

    def _centerLinks(self):
        links = [
            ["decks", _("Decks"), _("Shortcut key: %s") % "D"],
            ["add", _("Add"), _("Shortcut key: %s") % "A"],
            ["browse", _("Browse"), _("Shortcut key: %s") % "B"],
            ["stats", _("Stats"), _("Shortcut key: %s") % "T"],
        ]

        return self._linkHTML(links) + self._sync_link()

    def _linkHTML(self, links):
        buf = ""
        for ln, name, title in links:
            buf += """
            <a class=hitem tabindex="-1" aria-label="%s" title="%s" href=# onclick="return pycmd('%s')">%s</a>""" % (
                name,
                title,
                ln,
                name,
            )
        return buf

    def _sync_link(self) -> str:
        name = _("Sync")
        title = _("Shortcut key: %s") % "Y"
        label = "sync"
        return f"""
<a class=hitem tabindex="-1" aria-label="{name}" title="{title}" href=# onclick="return pycmd('{label}')">{name}
<img id=sync-spinner src='/_anki/imgs/refresh.svg'>        
</a>"""

    def set_sync_active(self, active: bool) -> None:
        if active:
            meth = "addClass"
        else:
            meth = "removeClass"
        self.web.eval(f"$('#sync-spinner').{meth}('spin')")

    # Link handling
    ######################################################################

    def _linkHandler(self, link):
        if link in self.link_handlers:
            self.link_handlers[link]()
        return False

    def _deckLinkHandler(self):
        self.mw.moveToState("deckBrowser")

    def _studyLinkHandler(self):
        # if overview already shown, switch to review
        if self.mw.state == "overview":
            self.mw.col.startTimebox()
            self.mw.moveToState("review")
        else:
            self.mw.onOverview()

    def _addLinkHandler(self):
        self.mw.onAddCard()

    def _browseLinkHandler(self):
        self.mw.onBrowse()

    def _statsLinkHandler(self):
        self.mw.onStats()

    def _syncLinkHandler(self):
        self.mw.onSync()

    # HTML & CSS
    ######################################################################

    _body = """
<center id=outer>
<table id=header width=100%%>
<tr>
<td class=tdcenter align=center>%s</td>
</tr></table>
</center>
"""


# Bottom bar
######################################################################


class BottomBar(Toolbar):

    _centerBody = """
<center id=outer><table width=100%% id=header><tr><td align=center>
%s</td></tr></table></center>
"""

    def draw(
        self,
        buf: str = "",
        web_context: Optional[Any] = None,
        link_handler: Optional[Callable[[str], Any]] = None,
    ):
        # note: some screens may override this
        web_context = web_context or BottomToolbar(self)
        link_handler = link_handler or self._linkHandler
        self.web.set_bridge_command(link_handler, web_context)
        self.web.stdHtml(
            self._centerBody % buf,
            css=["toolbar.css", "toolbar-bottom.css"],
            context=web_context,
        )
        self.web.adjustHeightToFit()
