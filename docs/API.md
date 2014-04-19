## Project Ginger REST API Specification

The Ginger API provides all functionalities of the plugin that may be used
directly by external tools. In the following sections you will find the
specification of all Collections and Resource types that are supported and
URIs where they can be accessed. As Ginger API uses Kimchi framework, it uses
the same general conventions of Kimchi. In order to use the API effectively,
please consider the following general conventions (from Kimchi documentation):

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
