#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Notification message with information, based on D-Bus, with Fallbacks."""


import logging as log
from shutil import which
from subprocess import run

try:
    import dbus
except ImportError:
    dbus = None

try:
    import pynotify
except ImportError:
    pynotify = None


def make_notification(title: str, message: str="", name: str="",
                      icon: str="", timeout: int=3_000) -> bool:
    """Notification message with information,based on D-Bus,with Fallbacks."""
    if dbus:  # Theorically the standard universal way.
        log.debug(f"Sending Notification message using the API of {dbus}.")
        return bool(dbus.Interface(dbus.SessionBus().get_object(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"),
            "org.freedesktop.Notifications").Notify(
                name, 0, icon, title, message, [], [], timeout))
    elif pynotify:  # The non-standard non-universal way.
        log.debug(f"Sending Notification message using the API of {pynotify}.")
        pynotify.init(name.lower() if name else title.lower())
        return pynotify.Notification(title, message).show()
    elif which("notify-send"):   # The non-standard non-universal sucky ways.
        log.debug("Sending Notification message via notify-send command.")
        comand = (which("notify-send"), f"--app-name={name}",
                  f"--expire-time={timeout}", title, message)
        return not bool(
            run(comand, timeout=timeout // 1_000 + 1, shell=True).returncode)
    elif which("kdialog"):
        log.debug("Sending Notification message via KDialog command.")
        comand = (which("kdialog"), f"--name={name}", f"--title={title}",
                  f"--icon={icon}", f"--caption={name}", "--passivepopup",
                  title + message, str(timeout // 1_000))
        return not bool(
            run(comand, timeout=timeout // 1_000 + 1, shell=True).returncode)
    elif which("zenity"):
        log.debug("Sending Notification message via Zenity command.")
        comand = (which("zenity"), f"--name={name}", f"--title={title}",
                  "--notification", f"--timeout={timeout // 1_000}",
                  f"--text={title + message}")
        return not bool(
            run(comand, timeout=timeout // 1_000 + 1, shell=True).returncode)
    else:  # Windows and Mac dont have API for that, complain to them.
        log.warning("Sending Notifications not supported by this OS.")
        return False
