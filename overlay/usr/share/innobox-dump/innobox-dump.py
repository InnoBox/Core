#!/usr/bin/python
from subprocess import Popen, PIPE
from sys import argv
import time
time.sleep(1)
debugfile = open('/tmp/dev%s' % argv[1],'w')
def debug(s):
	debugfile.write("%s\n" % s)
	debugfile.flush()

def beep(f):
	if f is None:
		f = 1024
	a = Popen("beep -f %d" % f, shell=True)
	a.wait()
beep(880)
f = open('/etc/mtab','r')
mountpoint = None
beep(440)
for line in f:
	pieces = line.split(' ')
	if pieces[0] == "/dev/%s" % argv[1]:
		mountpoint = pieces[1]
		break
f.close()
beep(880)
if mountpoint is None:
	#This script may be invoked with volume names like "sdc", in which
	#case we should exit silently, because volumes are not mountable
	debug("mountpoint is None!")
	exit()
debug("mountpoint is %s" % mountpoint)
print mountpoint

ifc_output = Popen("/sbin/ifconfig eth0", shell=True, stdout=PIPE).communicate()[0]
beep(440)
import re
ipaddr = re.search(r'inet addr:(\S+)\s', ifc_output).groups()[0]
print ipaddr
macaddr = re.search(r'HWaddr (\S+)\s', ifc_output).groups()[0]
print macaddr

ip_placeholder = "WIKI_IPADDRESS"
mac_placeholder = "WIKI_MACADDRESS"
date_placeholder = "DATESTAMP"

f = open('/usr/share/innobox-dump/WikiInABox_Startup_Page.html','r')
contents = f.read()
f.close()
import string
outpage = string.replace(contents, ip_placeholder, ipaddr)
outpage = string.replace(outpage, mac_placeholder, macaddr)
import time
outpage = string.replace(outpage, date_placeholder, time.asctime())
import os.path
f = open(os.path.join(mountpoint,'Welcome_to_WikiInABox.html'),'w')
beep(1320)
f.write(outpage)
f.close()

beep(880)
