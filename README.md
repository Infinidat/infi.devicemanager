Overview
========

A Python module for travelling the Windows Device Manager.

Usage
-----

Here's an example on how to use this module:

```python
from infi.devicemanager import DeviceManager
dm = DeviceManager()
dm.root.rescan()
disks = dm.disk_drives
names = [disk.friendly_name for disk in disks]
```

Supported Operating Systems
---------------------------
infi.devicemanager supports Windows Vista and later versions of Windows.

Checking out the code
=====================

Run the following:

    easy_install -U infi.projector
    projector devenv build

Python 3
========

Python 3 support is experimental at this stage.
