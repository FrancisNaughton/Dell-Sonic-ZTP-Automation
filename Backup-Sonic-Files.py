#This script takes a csv of sonic switches
#It ssh to each switch and copies the config_db.json file 
#Input file CSV -> ip	user	pass	hostname	type	building
#It will ask for your credentials, then ssh and parse through each of the IPs
#
import paramiko
import os 
import pandas as pd

from datetime import datetime
from getpass import getpass


#takes in ip address, username, password, hostname, and folder name. 
def backup_device(ip, username, password, hostname, folder):
    #gets time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #sets paths, takes names from data frame
    remote_temp_path = "/tmp/config_copy.json"
    local_dir = f"backup_configdbs"
    local_path = f"{local_dir}/{hostname}config_db.json"
    

    #ensures directory is created/exists
    os.makedirs(local_dir, exist_ok=True)
    
    print(f"\n Backing up {hostname} ({ip})...")
    
    #paramiko setup
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=ip, username=username, password=password)
        
        #copy/paste makes it readable
        cmd = f"sudo cp /etc/sonic/config_db.json {remote_temp_path} && sudo chmod 644 {remote_temp_path}"
        stdin,stdout, stderr = client.exec_command(cmd)
        
        if stdout.channel.recv_exit_status() != 0:
            raise Exception(f"Copy Failed: {stderr.read().decode()}")
        

        #Download
        sftp = client.open_sftp()
        sftp.get(remote_temp_path, local_path)
        sftp.close()
        print(f"Backup Saved to: {local_path}")

        stdin, stdout, stderr = client.exec_command(f"sudo rm {remote_temp_path}")
        
        if stdout.channel.recv_exit_status() != 0:
            print("Warning: Cleanup failed:", stderr.read().decode())
        else:
            print("Remote cleanup finished.")
    
    except Exception as e:
        print(f"Error backing up {hostname}: {e}")
    
    finally:
        client.close()

#main~~~~~~~~~~~~~~LOGICTIME~~~~~~~~~~~~~~~~~~~~~~~main#

csv_path = 'oneswitchtest.csv'

#Prompt for that cred
shared_user = input("Enter SSh Username: ")
shared_pass = getpass("Enter SSh Password: ")

#load csv into dataframe
df = pd.read_csv(csv_path)#, delimiter=';')

print('\nAvailable buildings: ', df['building'].unique())
print('\nAvailable types: ', df['type'].unique())

#filter prompt
building_filter = input("Filter by building (to skip hit enter): ").strip()
type_filter = input("Filter by switch type (to skip hit enter): ").strip()

#apply filters
if building_filter:
    df = df[df['building'].str.strip().str.lower() == building_filter.lower()]
if type_filter:
    df = df[df['type'].str.strip().str.lower() == type_filter.lower()]

if df.empty:
    print("No devices matched the given filters.")
else:
    for _, row in df.iterrows():
        backup_device(
            ip=row['ip'].strip(),
            username=shared_user,
            password=shared_pass,
            hostname=row['hostname'].strip(),
            folder=row['building'].strip()
        )
