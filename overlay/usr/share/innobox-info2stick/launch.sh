#!/bin/sh

# The purpose of this very small script is solely to allow
# innobox-info2stick.py to run asynchronously.  This is important
# because udev does not fork when RUNning scripts, so all
# udev processing is held up until the script returns.

/usr/share/innobox-info2stick/innobox-info2stick.py $1 &
