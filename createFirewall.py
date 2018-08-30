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

username = raw_input('Enter username: ')
password = raw_input('Enter Password: ')
port = raw_input('Enter port (ex, 22): ')


# Logging before dropping
iptable ='iptables dropped'

ruleA = 'sudo iptables -N LOG_AND_DROP'
ruleB = 'sudo iptables -A LOG_AND_DROP -j LOG --log-prefix '+str(iptable)
ruleC = 'sudo iptables -A LOG_AND_DROP -j DROP'

rule1 = 'sudo /sbin/iptables -t mangle -A PREROUTING -m conntrack --ctstate INVALID -j DROP'
rule2 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp ! --syn -m conntrack --ctstate NEW -j DROP'
rule3 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp -m conntrack --ctstate NEW -m tcpmss ! --mss 536:65535 -j DROP'
rule4 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags SYN,RST SYN,RST -j DROP'
rule5 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags FIN,RST FIN,RST -j DROP'
rule6 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ACK,FIN FIN -j DROP'
rule7 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ACK,URG URG -j DROP'
rule8 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ACK,FIN FIN -j DROP'
rule9 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ACK,PSH PSH -j DROP'
rule10 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ALL ALL -j DROP'
rule11 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ALL NONE -j DROP'
rule12 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ALL FIN,PSH,URG -j DROP'
rule13 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ALL SYN,FIN,PSH,URG -j DROP'
rule14 = 'sudo /sbin/iptables -t mangle -A PREROUTING -p tcp --tcp-flags ALL SYN,RST,ACK,FIN,URG -j DROP'
rule15 = 'sudo /sbin/iptables -A INPUT -p tcp -m connlimit --connlimit-above 500 -j LOG_AND_DROP'
rule16 = 'sudo /sbin/iptables -A INPUT -p tcp --tcp-flags RST RST -m limit --limit 2/s --limit-burst 2 -j ACCEPT'
rule17 = 'sudo /sbin/iptables -A INPUT -p tcp --tcp-flags RST RST -j LOG_AND_DROP'
rule18 = 'sudo /sbin/iptables -A INPUT -p tcp -m conntrack --ctstate NEW -m limit --limit 60/s --limit-burst 20 -j ACCEPT'
rule19 = 'sudo /sbin/iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT'
rule20 = 'sudo /sbin/iptables -A INPUT -i lo -j ACCEPT'
rule21 = 'sudo /sbin/iptables -A INPUT -m conntrack --ctstate INVALID -j LOG_AND_DROP'
rule22 = 'sudo /sbin/iptables -A INPUT -p icmp -m icmp --icmp-type 8 -m conntrack --ctstate NEW -j ACCEPT'
# rule23 = 'sudo /sbin/iptables -A INPUT -p udp -m conntrack --ctstate NEW -j UDP'
# rule24 = 'sudo /sbin/iptables -A INPUT -p tcp --tcp-flags FIN,SYN,RST,ACK SYN -m conntrack --ctstate NEW -j TCP'
# rule25 = 'sudo /sbin/iptables -A INPUT -p udp -j REJECT --reject-with icmp-port-unreachable'
# rule26 = 'sudo /sbin/iptables -A INPUT -p tcp -j REJECT --reject-with tcp-reset'

rule27 = 'sudo iptables -A INPUT -d 10.1.1.1 -p udp --dport 137 -j LOG_AND_DROP'
rule28 = 'sudo iptables -A INPUT -d 10.1.1.1 -p udp --dport 138 -j LOG_AND_DROP'
rule29 = 'sudo iptables -A INPUT -d 10.1.1.1 -p tcp --dport 139 -j LOG_AND_DROP'
rule30 = 'sudo iptables -A INPUT -d 10.1.1.1 -p tcp --dport 445 -j LOG_AND_DROP'
# rule31 = 'sudo iptables -A INPUT -p tcp –dport 23 -j LOG_AND_DROP'
# rule32 = 'sudo iptables -A INPUT -p tcp –dport 21 -j LOG_AND_DROP'
# rule33 = 'sudo iptables -A INPUT -p tcp –dport 52 -j LOG_AND_DROP'
# rule34 = 'sudo iptables -A INPUT -p tcp –dport 79 -j LOG_AND_DROP'

rule35 = 'sudo /sbin/iptables -A INPUT -p tcp -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 10 -j LOG_AND_DROP'
rule36 = 'sudo /sbin/iptables -N port-scanning'
rule37 = 'sudo /sbin/iptables -A port-scanning -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s --limit-burst 2 -j RETURN'
rule38 = 'sudo /sbin/iptables -A port-scanning -j LOG_AND_DROP'



try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    client.connect(hostname, port=int(port), username=str(username), password=str(password))

    stdin, stdout, stderr = client.exec_command(ruleA)
    stdin, stdout, stderr = client.exec_command(ruleB)
    stdin, stdout, stderr = client.exec_command(ruleC)

    stdin, stdout, stderr = client.exec_command(rule1)
    stdin, stdout, stderr = client.exec_command(rule2)
    stdin, stdout, stderr = client.exec_command(rule3)
    stdin, stdout, stderr = client.exec_command(rule4)
    stdin, stdout, stderr = client.exec_command(rule5)
    stdin, stdout, stderr = client.exec_command(rule6)
    stdin, stdout, stderr = client.exec_command(rule7)
    stdin, stdout, stderr = client.exec_command(rule8)
    stdin, stdout, stderr = client.exec_command(rule9)
    stdin, stdout, stderr = client.exec_command(rule10)
    stdin, stdout, stderr = client.exec_command(rule11)
    stdin, stdout, stderr = client.exec_command(rule12)
    stdin, stdout, stderr = client.exec_command(rule13)
    stdin, stdout, stderr = client.exec_command(rule14)
    stdin, stdout, stderr = client.exec_command(rule15)
    stdin, stdout, stderr = client.exec_command(rule16)
    stdin, stdout, stderr = client.exec_command(rule17)
    stdin, stdout, stderr = client.exec_command(rule18)
    stdin, stdout, stderr = client.exec_command(rule19)
    stdin, stdout, stderr = client.exec_command(rule20)
    stdin, stdout, stderr = client.exec_command(rule21)
    stdin, stdout, stderr = client.exec_command(rule22)
    # stdin, stdout, stderr = client.exec_command(rule23)
    # stdin, stdout, stderr = client.exec_command(rule24)
    # stdin, stdout, stderr = client.exec_command(rule25)
    # stdin, stdout, stderr = client.exec_command(rule26)
    stdin, stdout, stderr = client.exec_command(rule27)
    stdin, stdout, stderr = client.exec_command(rule28)
    stdin, stdout, stderr = client.exec_command(rule29)
    stdin, stdout, stderr = client.exec_command(rule30)
    # stdin, stdout, stderr = client.exec_command(rule31)
    # stdin, stdout, stderr = client.exec_command(rule32)
    # stdin, stdout, stderr = client.exec_command(rule33)
    # stdin, stdout, stderr = client.exec_command(rule34)
    stdin, stdout, stderr = client.exec_command(rule35)
    stdin, stdout, stderr = client.exec_command(rule36)
    stdin, stdout, stderr = client.exec_command(rule37)
    stdin, stdout, stderr = client.exec_command(rule38)

    

finally:
    print('Default IP table rules have been added to the VM')
    client.close()


conn.close()
exit(0)