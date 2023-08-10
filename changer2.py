#The subprocess module allows you to spawn new processes, 
# connect to their input/output/error pipes, and obtain their return codes
import subprocess 
#---------------------------------------------------------------------------------
#The Windows Registry is a hierarchical database that stores low-level settings for the Microsoft Windows operating system and for applications that opt to use the registry. 
#The kernel, device drivers, services, Security Accounts Manager, and user interfaces can all use the registry
#These functions expose the Windows registry API to Python. Instead of using an integer as the registry handle, 
#a handle object is used to ensure that the handles are closed correctly, even if the programmer neglects to explicitly close them.
import winreg
#-------------------------------------------------------------------------------------------------------------
#can be used to work with Regular Expressions.
import re
#-------------------------------------------------------------------------------------------------------------
#access to internal python registry, to handle encode decode and related error handling  
#import codecs



# MAC Addresses to attempt using. You will select one when the script is used.
# You can change the names in this list or add names to this list.
# Make sure you use 12 valid hexadecimal values. 
# If the MAC address change fails try setting the second character to 2 or 6 or A or E,
# for example: 0A1122334455 or 0A5544332211
# If unsure, leave the MAC addresses listed here as is.
mac_to_change_to = ["0A1122334455", "0E1122334455", "021122334455", "061122334455","CC6B1E0ACE39"]

# We create an empty list where we'll store all the MAC addresses.
mac_addresses = list()

# We start off by creating a regular expression (regex) for MAC addresses.
macAddRegex = re.compile(r"([A-Fa-f0-9]{2}[:-]){5}([A-Fa-f0-9]{2})")


#The column marked "Transport Name" will give some indication as to whether or not the adapter is active. 
#If it shows as Media disconnected,then the adapter is likely not active and is therefore not suitable for use
#This is the location of the Network Adapter.
# We create a regex for the transport names
transportName = re.compile("({.+})")  

#This index value identifies the network connection on an extensible switch port. 
# The index value is unique for each network adapter connection to a port. 
# We create regex to pick out the adapter index
#The extensible switch interface creates and configures a port before a network connection is made.
adapterIndex = re.compile("([0-9]+)")

# Python allows us to run system commands by using a function provided by the subprocess module: 
# (subprocess.run(<list of command line arguments goes here>, 
# <specify the second argument if you want to capture the output>))
# The script is a parent process and creates a child process which runs the system command, 
# and will only continue once the child process has completed.
# To save the content that gets sent to the standard output stream (the terminal), 
# we have to specify that we want to capture the output, so we specify the second 
# argument as capture_output = True. This information gets stored in the stdout attribute. 
# The information is stored in bytes and we need to decode it to Unicode before we use it
# as a String in Python.
# We use Python to run the getmac command, and then capture the output. 
# We split the output at the newline so that we can work with the individual lines 
# (which will contain the Mac and transport name).
getmac_output = subprocess.run("getmac", capture_output=True).stdout.decode().split('\n') 
print(getmac_output)
# We loop through the output
for macAdd in getmac_output:
    # We use the regex to find the Mac Addresses.
    macFind = macAddRegex.search(macAdd)
    # We use the regex to find the transport name. 
    transportFind = transportName.search(macAdd)
    # If you don't find a Mac Address or Transport name the option won't be listed.
    if macFind == None or transportFind == None:
        continue
    # We append a tuple with the Mac Address and the Transport name to a list.
    mac_addresses.append((macFind.group(0),transportFind.group(0)))

# Create a simple menu to select which Mac Address the user want to update.
print("Which MAC Address do you want to update?")
for index, item in enumerate(mac_addresses):
    print(f"{index} - Mac Address: {item[0]} - Transport Name: {item[1]}")

# Prompt the user to select Mac Address they want to update.
option = input("Select the menu item number corresponding to the MAC that you want to change:")

# Create a simple menu so the user can pick a MAC address to use
while True:
    print("Which MAC address do you want to use? This will change the Network Card's MAC address.")
    for index, item in enumerate(mac_to_change_to):
        print(f"{index} - Mac Address: {item}")

    # Prompt the user to select the MAC address they want to change to.
    update_option = input("Select the menu item number corresponding to the new MAC address that you want to use:")
    # Check to see if the option the user picked is a valid option.
    if int(update_option) >= 0 and int(update_option) < len(mac_to_change_to):
        print(f"Your Mac Address will be changed to: {mac_to_change_to[int(update_option)]}")
        break
    else:
        print("You didn't select a valid option. Please try again!")

# We know the first part of the key, we'll append the folders where we'll search the values
controller_key_part = r"SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
#A registry key can be thought of as being a bit like a file folder, but it exists only in the Windows Registry. 
# Registry keys contain registry values, just like folders contain files.
# We connect to the HKEY_LOCAL_MACHINE registry. If we specify None, 
# it means we connect to local machine's registry. 
#contains the majority of the configuration information for the software you have installed, as well as for the Windows operating system itself.
#In addition to software configuration data, 
# this hive also contains lots of valuable information about currently detected hardware and device drivers.
with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
    # Create a list for the 21 folders. I used a list comprehension. The expression part of the list comprehension
    # makes use of a ternary operator. The transport value for you Mac Address should fall within this range. 
    # You could write multiple lines.
    controller_key_folders = [("\\000" + str(item) if item < 10 else "\\00" + str(item)) for item in range(0, 21)]
    # We now iterate through the list of folders we created.
    for key_folder in controller_key_folders:
        # We try to open the key. If we can't we just except and pass. But it shouldn't be a problem.
        try:
            # We have to specify the registry we connected to, the controller key 
            # (This is made up of the controller_key_part we know and the folder(key) name we created
            # with the list comprehension).
            #Opens the specified key, returning a handle object. this object automatically closes it and cleansup
            with winreg.OpenKey(hkey, controller_key_part + key_folder, 0, winreg.KEY_ALL_ACCESS) as regkey:
                # We will now look at the Values under each key and see if we can find the "NetCfgInstanceId" 
                # with the same Transport Id as the one we selected.
                try:
                    # Values start at 0 in the registry and we have to count through them. 
                    # This will continue until we get a WindowsError (Where we will then just pass) 
                    # then we'll start with the next folder until we find the correct key which contains 
                    # the value we're looking for.
                    count = 0
                    while True:
                        # We unpack each individual winreg value into name, value and type.
                        name, value, type = winreg.EnumValue(regkey, count)
                        # To go to the next value if we didn't find what we're looking for we increment count.
                        count = count + 1
                        # We check to see if our "NetCfgInstanceId" is equal to our Transport number for our 
                        # selected Mac Address.
                        if name == "NetCfgInstanceId" and value == mac_addresses[int(option)][1]:
                            new_mac_address = mac_to_change_to[int(update_option)]
                            winreg.SetValueEx(regkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac_address)
                            print("Successly matched Transport Number")
                            # get list of adapters and find index of adapter you want to disable.
                            break
                except WindowsError:
                    pass
        except:
            pass


# Code to disable and enable Wireless devicess
run_disable_enable = input("Do you want to disable and reenable your wireless device(s). Press Y or y to continue:")
# Changes the input to lowercase and compares to y. If not y the while function which contains the last part will never run.
if run_disable_enable.lower() == 'y':
    run_last_part = True
else:
    run_last_part = False

# run_last_part will be set to True or False based on above code.
while run_last_part:

    # Code to disable and enable the network adapters
    # We get a list of all network adapters. You have to ignore errors, as it doesn't like the format the command returns the data in.
    network_adapters = subprocess.run(["wmic", "nic", "get", "name","index"], capture_output=True).stdout.decode('utf-8', errors="ignore").split('\r\r\n')
    print("NETWORK ADAPTERS")
    print(network_adapters,"\n")
    print("ADAPTERS")
    for adapter in network_adapters:
        # We get the index for each adapter
        adapter_index_find = adapterIndex.search(adapter.lstrip())
        print(adapter,"\n")
        # If there is an index and the adapter has wireless in description we are going to disable and enable the adapter
        if adapter_index_find and "Wi-Fi" in adapter:
            #disable = subprocess.run(["wmic", "path", "win32_networkadapter", "where", f"index={adapter_index_find.group(0)}", "call", "disable"],capture_output=True)
            disable=subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disable"],capture_output=True)
            print(disable.returncode)
            # If the return code is 0, it means that we successfully disabled the adapter
            if(disable.returncode == 0):
                print(f"Disabled {adapter.lstrip()}")
            # We now enable the network adapter again.
            #enable = subprocess.run(["wmic", "path", f"win32_networkadapter", "where", f"index={adapter_index_find.group(0)}", "call", "enable"],capture_output=True)
            enable=subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enable"],capture_output=True)
            # If the return code is 0, it means that we successfully enabled the adapter
            if (enable.returncode == 0):
                print(f"Enabled {adapter.lstrip()}")

    # We run the getmac command again
    getmac_output = subprocess.run("getmac", capture_output=True).stdout.decode()
    print(getmac_output)
    # We recreate the Mac Address as ot shows up in getmac XX-XX-XX-XX-XX-XX format from the 12 character string we have. 
    # We split the string into strings of length 2 using list comprehensions and then. We use "-".join(list) to recreate the address
    mac_add = "-".join([(mac_to_change_to[int(update_option)][i:i+2]) for i in range(0, len(mac_to_change_to[int(update_option)]), 2)])
    # We want to check if Mac Address we changed to is in getmac output, if so we have been successful.
    print(mac_add)
    print(getmac_output)
    if mac_add in getmac_output:
        print("Mac Address Success")
    else : 
        print("Mac Address Fail")
    # Break out of the While loop. Could also change run_last_part to False.
    break
