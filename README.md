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

For pulling the config_db.json files from the production switches, we use the python script called Backup-Sonic-Files.
Backup-Sonic-Files takes in a CSV with the following fields, connects to each of the switches, and SFTP's the config file into a folder named backup_configdbs with their hostnames attached to the filename. 
ip	user	pass	hostname	type	building

A second script, Parse-Clean-configs, then parses through each of the config_db.json files and removes 3 fields that will cause conflicts if not removed.

From there, the config files can be put onto the switch sideloaded with the DHCP and HTTP server. 

Getting a switch to take the correct config is pretty simple, 
1. The fresh switch's service tag has to be taken and put into the config's filename
   For example, if a switches service tag is FAKESVZ, the file name should be 'FAKESVZ-config_db.json'
2. The 'to-be configured' switch's mgmt port should be plugged into the ZTP-mothership anywhere vlan100 is active
3. Next, while the 'to-be configured' switch is connected, the dhcp server needs to be restarted.
   sudo docker -H unix:///run/docker-default.socket stop isc_dhcp
   sudo docker -H unix:///run/docker-default.socket start isc_dhcp
4. Next, confirm it's running properly
   sudo docker -H unix:///run/docker-default.socket ps -a
5. From there if you console into the 'to-be configured' switch, you should see it grab the new OS, and config file.
6. After a couple reboots, it will come back with the correct config.

