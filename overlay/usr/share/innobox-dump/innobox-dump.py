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

def get_mountpoint(devicename):
	f = open('/etc/mtab','r')
	for line in f:
		pieces = line.split(' ')
		if pieces[0] == "/dev/%s" % devicename:
			f.close()
			return pieces[1]
	f.close()
	return None

def get_addrs():
	ifc_output = Popen("/sbin/ifconfig eth0", shell=True, stdout=PIPE).communicate()[0]
	import re
	ipaddr = re.search(r'inet addr:(\S+)\s', ifc_output).groups()[0]
	debug("IP address is %s" % ipaddr)
	macaddr = re.search(r'HWaddr (\S+)\s', ifc_output).groups()[0]
	debug("MAC address is %s" % macaddr)
	return ipaddr, macaddr

mountpoint = get_mountpoint(argv[1])
if mountpoint is None:
	#This script may be invoked with volume names like "sdc", in which
	#case we should exit silently, because volumes are not mountable
	debug("mountpoint is None!")
	exit()
debug("mountpoint is %s" % mountpoint)

ipaddr, macaddr = get_addrs()

f = open('/usr/share/innobox-dump/InnoBox_Startup_Page.html','r')
contents = f.read()
f.close()

ip_tag = "MY_IPADDRESS"
mac_tag = "MY_MACADDRESS"
date_tag = "DATESTAMP"

outpage = contents % {ip_tag:ipaddr, mac_tag:macaddr, date_tag:time.asctime()}

import os.path
f = open(os.path.join(mountpoint,'Welcome_to_InnoBox.html'),'w')
f.write(outpage)
f.close()
# the USB disk is mounted -o sync, so f.close() should be enough to
# flush the file to disk

beep(440)
beep(880)
beep(440)
beep(880)
beep(440)
