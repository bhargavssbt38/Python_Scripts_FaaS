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

print(domainIDs[0])

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

chainToAdd = raw_input("Enter the chain to which rule has to be added: ")
lineNumberToAdd = raw_input("Enter the line number for the rule to be added: ")
command = 'sudo iptables -I '+str(chainToAdd)+' '+str(lineNumberToAdd)+' '
username = raw_input('Enter username: ')
password = raw_input('Enter Password: ')
port = raw_input('Enter port (ex, 22): ')

protocol = raw_input("Enter the protocol: ")
source = raw_input("Enter the source: ")
destination = raw_input("Enter the destination: ")
target = raw_input("Enter the target: ")
sourcePort = raw_input("Enter the source port: ")
destinationPort = raw_input("Enter the destination port: ")
action = raw_input("Enter the action(ACCEPT/REJECT/DROP): ")

if protocol:
    command+='-p '+str(protocol)+' '

if source:
    command+='-s '+str(source)+' '

if destination:
    command+='-d '+str(destination)+' '

if target:
    command+='-j '+str(target)+' '

if sourcePort:
    sourcePort+='--sport '+str(sourcePort)+' '

if destinationPort:
    destinationPort+='--dport '+str(destinationPort)+' '

if action:
    action+='-j '+str(action)+' '



try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    client.connect(hostname, port=int(port), username=str(username), password=str(password))

    stdin, stdout, stderr = client.exec_command(command)

finally:
    print('Specified firewall rule has been added')
    client.close()

conn.close()
exit(0)