# Dell-Sonic-ZTP-Automation
This repository holds documentation on how Dell's zero touch provisioning (ZTP) can be leveraged. 
This will include setup tips that weren't included in https://github.com/twagar11/Dell-SONIC-ZTP-with-TPCM

This setup was done using a Dell 3248PXE-ON. We installed the isc_dhcp server onto the default vrf:
sudo tpcm install name isc_dhcp pull networkboot/dhcpd --args '-v /home/admin/data:/data --network=host --security-opt seccomp=unconfined --memory=1000M'

We then installed a dhcp server on the mgmt vrf. 
sudo  tpcm install name isc_dhcp pull networkboot/dhcpd --args "-v /home/admin/data:/data --network=host --security-opt seccomp=unconfined –memory=1000M" vrf-name mgmt

We created a vlan 100 set the vrf forwarding to mgmt vrf with the same IP range the dhcpd.conf file will use, we then gave it a dhcp-relay & helper-address to its own management IP. 
Vlan 100 was then put on every access port.

As for the directories, we followed the ones provided in repository above. 
