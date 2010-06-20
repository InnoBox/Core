#!/usr/bin/python
from subprocess import Popen, PIPE
from sys import argv
import time
time.sleep(1) #FIXME: check if this is necessary.
debugfile = open('/tmp/dev%s' % argv[1],'w')

def debug(s):
	debugfile.write("%s\n" % s)
	debugfile.flush()

def beep(f):
	if f is None:
		f = 1024
	a = Popen("beep -f %d" % f, shell=True)
	a.wait()

def chime():
	beep(523.2)
	beep(440)
	beep(523.2)
	beep(293.7*2)
	beep(329.6*2)
	beep(329.6*2)

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
	match = re.search(r'inet addr:(\S+)\s', ifc_output)
	if match is None:
		ipaddr = None
	else:
		ipaddr = match.groups()[0]
	debug("IP address is %s" % ipaddr)
	match = re.search(r'HWaddr (\S+)\s', ifc_output)
	if match is None:
		macaddr = "ERROR: No MAC address detected!"
	else:
		macaddr = match.groups()[0]
	debug("MAC address is %s" % macaddr)
	return ipaddr, macaddr

def is_special_mountpoint(mountpoint):
	from os.path import join
	from os import access, F_OK
	SPECIAL = ".InnoBox_Stick_Identifier"
	return access(os.path.join(mountpoint,SPECIAL), F_OK)

def is_backup_mountpoint(mountpoint):
	from os.path import join
	from os import access, F_OK
	SPECIAL = "InnoBox_Backup_Directory"
	return access(os.path.join(mountpoint,SPECIAL), F_OK)

mountpoint = get_mountpoint(argv[1])
if mountpoint is None:
	#This script may be invoked with volume names like "sdc", in which
	#case we should exit silently, because volumes are not mountable
	debug("mountpoint is None!")
	exit()
debug("mountpoint is %s" % mountpoint)

if is_backup_mountpoint(mountpoint):
	debug("This is a backup device. No dump will be written.")
	exit()

ipaddr, macaddr = get_addrs()
# If ipaddr is none, then the interface has not yet been configured.
# Maybe DHCP is ongoing.  Retry for up to 30 seconds,
# in 2-second intervals, in case DHCP is awfully slow.
wait = 0
interval = 2
while ipaddr is None and wait < 30:
	time.sleep(interval)
	wait += interval
	ipaddr, macaddr = get_addrs()

if ipaddr is not None:
	from socket import getfqdn
	fqdn = getfqdn(ipaddr)
	templatefile = '/usr/share/innobox-dump/InnoBox_Startup_Page.html'
else:
	templatefile = '/usr/share/innobox-dump/InnoBox_Failure_Page.html'
	fqdn = None
f = open(templatefile,'r')
contents = f.read()
f.close()

ip_tag = "MY_IPADDRESS"
fqdn_tag = "MY_FQDN" #Fully Qualified Domain Name
mac_tag = "MY_MACADDRESS"
date_tag = "DATESTAMP"

#Run the string interpolation operation and replace teh strings in the dictionary 
outpage = contents % {ip_tag:ipaddr, mac_tag:macaddr, date_tag:time.asctime(),
                                        fqdn_tag:fqdn}
import os.path
f = open(os.path.join(mountpoint,'Welcome_to_InnoBox.html'),'w')
f.write(outpage)
f.close()
# the USB disk is mounted -o sync, so f.close() should be enough to
# flush the file to disk

import shutil
shutil.copy('/usr/share/innobox-dump/autorun.inf',mountpoint)
shutil.copy('/usr/share/innobox-dump/innobox_logo.ico',mountpoint)

interval = 15 #seconds between beeps
chime()
time.sleep(interval)
while mountpoint is not None and is_special_mountpoint(mountpoint):
	#chime every minute until the device is unmounted
	chime()
	time.sleep(interval)
	mountpoint = get_mountpoint(argv[1])
