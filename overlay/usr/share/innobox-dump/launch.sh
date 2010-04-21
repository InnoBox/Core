#!/bin/sh
/usr/share/innobox-dump/innobox-dump.py $1 &
# The purpose of this very small script is solely to allow
# innobox-dump.py to run asynchronously.  This is important
# because udev does not fork when RUNning scripts, so all
# udev processing is held up until the script returns.
# innobox-dump can potentially sit around beeping indefinitely,
# so it's important that it return to udev immediately.
