#!/usr/bin/env bash
# XRDP starts this script inside the user's X session.
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
if [ -r /etc/profile ]; then . /etc/profile; fi
startxfce4
