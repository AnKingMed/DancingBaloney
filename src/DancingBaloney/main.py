# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/DancingBaloney
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import aqt
from aqt import mw
from anki.hooks import wrap, addHook

from .const import *
from .utils import *
from .style import *
from .config import Config

from .lib.com.lovac42.anki.version import CCBC

conf = Config(ADDON_NAME)


def bundledCSS(webview, fname, _old):
    theme = conf.get("theme")
    if theme:
        css = themeLoader(webview, fname, theme)
    else:
        css = manualLoader(webview, fname)
        theme = "user_files"

    # Custom style sheets
    custom_css = conf.get(f"custom_{fname[:-4]}_style")
    if custom_css:
        cc = f"{MOD_DIR}/{theme}/{custom_css}"
        try:
            import ccbc
            ret = ccbc.utils.readFile(cc)
        except ImportError:
            ret = _old(webview, cc).replace(r"/_anki/","/_addons/")
    else:
        ret = _old(webview, fname)

    if css:
        if CCBC:
            return f"{ret}\n{css}"
        return f"{ret}\n<style>{css}</style>"
    return ret





def themeLoader(webview, fname, theme):
    css = ""
    if fname in (
        "deckbrowser.css","overview.css","reviewer.css",
        "toolbar-bottom.css","reviewer-bottom.css"
    ):
        bg = f"{mw.state}_{fname[:-4]}.jpg"
        css = getBGImage(webview, MOD_DIR, bg, 100, theme)

        # if "toolbar" in fname:
        btn_bg = f"btn_{bg}"
        css += getButtonImage(webview, MOD_DIR, btn_bg, 80, theme)
    return css



def manualLoader(webview, fname):
    css = ""

    if mw.state == "review":
        # TODO: Fix for new version, it does not clear color on toolbar.
        # One or the other, targets different versions
        clearBGColor(webview)
        clearBGColor(mw.toolbar.web)

    elif fname == "toolbar.css" and mw.state == "deckBrowser":
        color = conf.get("top_toolbar_bg_color", "#F6FFE9")
        css = setBGColor(color, top=True)

    elif fname in ("deckbrowser.css","overview.css"):
        bg = conf.get("bg_img","sheep.gif")
        op = conf.get("bg_img_opacity",100)
        css = getBGImage(webview, MOD_DIR, bg, op)

    elif fname == "toolbar-bottom.css":
        tool_img = conf.get("bottom_toolbar_bg_img", "#1E2438")
        if tool_img:
            op = conf.get("bottom_toolbar_bg_img_opacity",100)
            css = getBGImage(webview, MOD_DIR, tool_img, op)
        else:
            color = conf.get("bottom_toolbar_bg_color")
            css = setBGColor(color, top=False)

    return css



def onAfterStateChange(newS, oldS, *args):
    "This is needed to get around an issue with setting images on the toolbar."
    theme = conf.get("theme", "")
    if theme:
        bg = f"{newS}_toolbar.jpg"
        setToolbarImage(mw.toolbar.web, MOD_DIR, bg, theme)


# ===== EXEC ===========

MOD_DIR = setWebExports(r".*\.(gif|png|jpe?g|bmp|css)$")

def onProfileLoaded():
    aqt.webview.AnkiWebView.bundledCSS = wrap(
        aqt.webview.AnkiWebView.bundledCSS,
        bundledCSS,
        "around"
    )
    mw.reset(True)
    addHook(f"{ADDON_NAME}.configUpdated", lambda:mw.reset(True))

#reloads with config.json data
addHook("profileLoaded", onProfileLoaded)
addHook('afterStateChange', onAfterStateChange)
