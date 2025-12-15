# Dell-Sonic-ZTP-Automation
This repository holds documentation on how Dell's zero touch provisioning (ZTP) can be leveraged. 
This will include setup tips that weren't included in https://github.com/twagar11/Dell-SONIC-ZTP-with-TPCM

This setup was done using a Dell E3248PXE-ON running Sonic 4.2.0-Edge_Standard.

We installed the isc_dhcp server onto the default vrf:
```
sudo tpcm install name isc_dhcp pull networkboot/dhcpd --args '-v /home/admin/data:/data --network=host --security-opt seccomp=unconfined --memory=1000M'
```

We then installed a dhcp server on the mgmt vrf:
```
sudo tpcm install name isc_dhcp pull networkboot/dhcpd --args "-v /home/admin/data:/data --network=host --security-opt seccomp=unconfined –memory=1000M" vrf-name mgmt
```
Confirm the containers installed successfully. (Install may fail, run the command again until it works.)


<img width="987" height="100" alt="image" src="https://github.com/user-attachments/assets/ccf20e68-f1a0-4524-9bb3-a6b4f9abcd9c" />


Then we created a vlan 100 set the vrf forwarding to mgmt vrf with the same IP range the dhcpd.conf file will use, we then gave it a dhcp-relay & helper-address to its own management IP.
Vlan 100 was then put on every access port.

As for the directories, we followed the ones provided in repository above. 

For pulling the config_db.json files from the production switches, we use the python script called Backup-Sonic-Files.
Backup-Sonic-Files takes in a CSV with the following fields, connects to each of the switches, and SFTP's the config file into a folder named backup_configdbs with their hostnames attached to the filename.\

ip	user	pass	hostname	type	building\

A second script, Parse-Clean-configs, then parses through each of the config_db.json files and removes 3 fields that will cause conflicts if not removed.

From there, the config files can be put onto the switch sideloaded with the DHCP and HTTP server. 

Getting a switch to take the correct config is pretty simple, 
1. The fresh switch's service tag has to be taken and put into the config's filename.
   
   For example, if a switches service tag is FAKESVZ, the file name should be 'FAKESVZ-config_db.json'\
      This is the block in 'ztp-lite.json' points to the service tag.\
\
      <img width="700" height="212" alt="image" src="https://github.com/user-attachments/assets/10709ed0-7ba7-45a2-81e8-d64954d1345b" />\

   Using the mac address is another option but we found it to be less consistant and messier when bulk configuring switches.
   
3. The 'to-be configured' switch's mgmt port should be plugged into the ZTP-mothership anywhere vlan100 is active
4. Next, while the new switch's mgmt port is connected to vlan 100, the dhcp server needs to be restarted.
   ```
   sudo docker -H unix:///run/docker-default.socket stop isc_dhcp
   sudo docker -H unix:///run/docker-default.socket start isc_dhcp
   ```
5. Next, confirm it's running properly
   ```
   sudo docker -H unix:///run/docker-default.socket ps -a
   ```
6. Console into the switch running the ztp discovery process, you should see it grab the new OS in block 1.\
   
7. It will then hit block 2 and grab the correct config from the http server.
8. Once block 3 finishes, on the sonic side, you can run:
```
show ztp-status
```
   If successful you should see step 1 and 2 as successful.\
   \
   <img width="361" height="515" alt="image" src="https://github.com/user-attachments/assets/efd7a404-0459-4b01-868c-9661774db935" />\

   \
We weren't worried about the ping connectivity test. It doesn't break the script if it fails so we left it to fail. 

