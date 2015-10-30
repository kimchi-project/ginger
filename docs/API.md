## Project Ginger REST API Specification

The Ginger API provides all functionalities of the plugin that may be used
directly by external tools. In the following sections you will find the
specification of all Collections and Resource types that are supported and
URIs where they can be accessed. As Ginger API uses Wok (Webserver Originated
from Kimchi) framework, it uses the same general conventions of Kimchi. In order
to use the API effectively, please consider the following general conventions
(from Kimchi documentation):

* The **Content Type** of the API is JSON.  When making HTTP requests to this
  API you should specify the following headers:
    * Accept: application/json
    * Content-type: application/json
* A **Collection** is a group of Resources of a given type.
    * A **GET** request retrieves a list of summarized Resource representations
      This summary *may* include all or some of the Resource properties but
      *must* include a link to the full Resource representation.
    * A **POST** request will create a new Resource in the Collection. The set
      of Resource properties *must* be specified as a JSON object in the request
      body.
    * No other HTTP methods are supported for Collections
* A **Resource** is a representation of a singular object in the API
    * A **GET** request retrieves the full Resource representation.
    * A **DELETE** request will delete the Resource. This request *may* contain
      a JSON object which specifies optional parameters.
    * A **PUT** request is used to modify the properties of a Resource
    * A **POST** request commits an *action* upon a Resource. The request body
      *must* contain a JSON object which specifies parameters.
* URIs begin with a '/plugins/ginger' to indicate the root of the Ginger API.
    * Variable segments in the URI begin with a ':' and should replaced with the
      appropriate resource identifier.

### Resource: Firmware (Power System firmware)

**URI:** /plugins/ginger/firmware

**Methods:**

* **GET**: Retrieve the current firmware levels.
    * level: The firmware levels (MI and ML, or Maint. Level)
             The final group is the currently booted firmware.
* **PUT**: Update the firmware level of the booted side.
    * path: The remote file path pointing to the firmware image
            file.
    * overwrite-perm-ok: Indicate whether possibly overwriting the
            permanent boot side while updating the fw is acceptable.
            * Required: No
            * Default: True
            * A value of 'False' guarantees the current perm side image
              remains untouched.
              Note: If running permanent image, this will result in
              an error.

**URI:** /plugins/ginger/firmware/commit

** Methods**

* **POST**: Commit the image running on the temp side to the perm side.
            In order to do this, the machine must be running the temp
            image.

**URI:** /plugins/ginger/firmware/reject

** Methods**

* **POST**: Reject the image on the temp side, overwriting it with
            the image from the perm side. In order to do this,
            the machine must be running the permanent image.


### Collection: SAN Adapters (Fibre Channel SCSI Hosts - HBAs)

**URI:** /plugins/ginger/san_adapters

**Methods:**

* **GET**: Retrieve a summarized list with the names of all defined fibre
           channel scsi hosts found in the server system.

### Resource: SAN Adapter (Fibre Channel SCSI Host - HBA)

**URI:** /plugins/ginger/san_adapters/*:name*

**Methods:**

* **GET**: Retrieve many information from a given SAN Adapter
    * name: The name of the adapter in the system (usually "hostXX").
    * wwpn: World Wide Port Name of the adapter.
    * wwnn: World Wide Node Name of the adapter.
    * state: Indicates the current state of the adapter port (eg. Online or
             Offline).
    * max_vports: Maximum number of virtual ports supported in a NVIP (N-port
                  ID virtualization) configuration by the adapter.
    * vports_inuse: Number of virtual ports being used in a NVIP configuration.
    * speed: Transfer speed being used by the adapter (eg. 1 Gbit, 2 Gbit, 4
             Gbit, 8 Gbit, or more).
    * symbolic_name: HBA overview information.

### Resource: Sensors

**URI:** /plugins/ginger/sensors

**Methods:**

* **GET**: Get sensors data for devices on the system, including
            CPU temperatures, fan speeds, and hard disk temperatures.
            This command uses lm-sensors, so it will return all
            sensor data located in sysfs files, or in the sensors.conf
            file, if it has been created by the system admin.

            Note: The default unit for temperature is Celsius. This
            can be changed to Fahrenheit in ginger.conf.

            Due to the large number of sensors in existence, and the
            user's ability to customize sensor names, the output
            will vary greatly from system to system. The only consistency
            will be the json items named 'sensors' and 'hdds'
    * sensors: Each sensor or sensor group returned by 'sensors', depending on
            whether there are multiple sensors on a chip. For example, a CPU
            may return a package temperature reading (along with a min, max,
            critical, and alarm temps) and additional readings for each core.
            If fan speeds are reported by lm-sensors, these will be returned
            as well. The last element of each device will be its unit, instead
            of appending a unit to each value.
            Note: Power supplies may report a negative value, which is valid.
    * hdds: The temperatures for disk drives in the system, returned by hddtemp.
            These will be in the format { "/dev/sda":102.0 } for each drive.
            The last item in the list will be a the temperature unit.

### Resource: IBM Serviceable Event Provider (SEP)

**URI:** /plugins/ginger/ibm_sep

**Methods:**

* **GET**: Retrieve a dictionary with the SEP status and subscription information:
    * status: Status of the SEP agent. Can be 'running' or 'not running'.
    * subscription: Dictionaries with the SEP subscription information:
        * hostname: Hostname of the host server.
        * port: Number of the network port used by the SEP agent.
        * community: SNMP community name which host server is member.
* **PUT**: Create and/or update a subscription

*Actions (POST):**

* start: Start the SEP daemon on host server.
* stop: Stop the SEP daemon on host server.

### Resource: IBM Serviceable Event Provider (SEP)

**URI:** /plugins/ginger/ibm_sep

**Methods:**

* **GET**: Retrieve a dictionary with the SEP status and subscription information:
    * status: Status of the SEP agent. Can be 'running' or 'not running'.
    * subscription: Dictionaries with the SEP subscription information:
        * hostname: Hostname of the host server.
        * port: Number of the network port used by the SEP agent.
        * community: SNMP community name which host server is member.
* **PUT**: Create and/or update a subscription

*Actions (POST):**

* start: Start the SEP daemon on host server.
* stop: Stop the SEP daemon on host server.

### Collection: File Systems

URI: /plugins/ginger/filesystems

**Methods:**

* **GET**: Retrieve a summarized list of all mounted filesystems

* **POST**: Mount a file system
       * blk_dev : Path of the device to be mounted.
       * mount_point : Mount point for the filesystem

### Resource: File System

URI: /plugins/ginger/filesystems/*:mount_point*

*Methods:**

* **GET**: Retrieve the full description of the mounted filesystem

       * use%: Percentage of the filesystem used
       * used: Amount of space used in filesystem
       * size:  Total size of the filesystem
       * mounted_on: Mount point of the filesystem
       * avail : Total space available on the filesystem
       * device_name : Backing device name of the filesystem.
       * type : Filesystem type.

* **DELETE**: Unmount the Filesystem

### Resource: Network Interface Configuration

**URI:** /plugins/ginger/network/cfginterfaces/*:name*

**Methods:**

* **GET**: Retrieve the information available in network interface
           file /etc/sysconfig/network-scripts/ifcfg-<name>
    * BASIC_INFO: Basic information of network interface:
        * NAME: Name of the interface.
        * DEVICE: Device name of the interface.
        * ONBOOT: 'Yes' if interface is to be brought up during boot,
                  'No' if interface should not be brought up during boot.
        * TYPE: Interface type (Ethernet,Bond,Vlan)
        * MACADDR: Mac address of ethernet device.
        * VLAN: 'Yes' If its vlan device.
        * VLAN_ID: Vland of the vlan device.
        * PHYSDEV: physical device associated with the vlan device.
        * BONDING_OPTS: Bonding parameters of the Bond device.
        * BONDING_MASTER: 'yes' if its bond device.
        * SLAVES: Returns slaves associated with the bond.
    * IPV4_INFO:IPV4 information of network interface:
        * BOOTPROTO: Boot protocol for ipv4(dhcp,none,autoip)
        * DEFROUTE: 'yes' Use default route
        * DNS: 'DNS' ip
        * PEERROUTES: 'yes' use PEERROUTES
        * IPV4_FAILURE_FATAL: 'yes' ipv4 connections fails then
                              interface is considered inactive
        * PEERDNS: 'yes' use the peerdns configured
        * IPADDR: ipv4 address of the interface
        * NETMASK: netmask of the ipv4 address
        * GATEWAY: Gateway assigned to the ipv4 address
    * IPV6_INFO:IPV6 information of network interface:
        * IPV6INIT: 'yes' to initalize ipv6 for the interface
        * IPV6_AUTOCONF: 'yes' automatic mode for ipv6
        * DHCPV6C: 'yes' dhcp automatic mode for ipv6
        * IPV6_DEFROUTE: 'yes' Use default route
        * IPV6_PEERROUTES: 'yes' use PEERROUTES
        * IPV6_FAILURE_FATAL: 'yes' ipv6 connections fails then
                              interface is considered inactive
        * IPV6_PEERDNS: 'yes' use the peerdns configured
        * IPV6ADDR: ipv6 address of the interface
        * IPV6_DEFAULTGW: Gateway assigned to the ipv6 address
