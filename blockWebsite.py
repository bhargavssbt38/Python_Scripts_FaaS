from __future__ import print_function
import libvirt
import sys
import subprocess
from xml.dom import minidom
import paramiko


conn = libvirt.open('qemu:///system')

if conn == None:
    print('Failed to open connection to the hypervisor')
    sys.exit(1)

domainIDs = conn.listDomainsID()

if domainIDs == None:
    print('Failed to get a list of domain IDs', file=sys.stderr)


ipAddressOfDomain=0

rawXml = conn.lookupByID(domainIDs[0]).XMLDesc(0)
xml = minidom.parseString(rawXml)
interfaceTypes = xml.getElementsByTagName('interface')
for interfaceType in interfaceTypes:
    interfaceNodes = interfaceType.childNodes
    for interfaceNode in interfaceNodes:
            if interfaceNode.nodeName != '#text':
                for attr in interfaceNode.attributes.keys():
                    if attr == "address":
                        macAddress = interfaceNode.attributes[attr].value
                        proc = (subprocess.Popen("/usr/sbin/arp -n | grep %s | awk \'{print $1}\'" % macAddress, shell=True, stdout=subprocess.PIPE).stdout.read())
                        ipAddressOfDomain=proc.strip()



hostname = ipAddressOfDomain

websiteToBlock = raw_input('Enter name of website to block (ex. www.facebook.com): ')

command = 'iptables -A OUTPUT -d '+str(websiteToBlock)+' -j DROP'

username = raw_input('Enter username: ')
password = raw_input('Enter Password: ')
port = raw_input('Enter port (ex, 22): ')


try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    client.connect(hostname, port=int(port), username=str(username), password=str(password))

    stdin, stdout, stderr = client.exec_command(command)
    print(stdout.read())

finally:
    print('Website has been blocked.')
    client.close()


conn.close()
exit(0)