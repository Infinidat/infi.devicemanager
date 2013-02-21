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

Checking out the code
=====================

This project uses buildout and infi-projector, and git to generate setup.py and __version__.py.
In order to generate these, first get infi-projector:

    easy_install infi.projector

    and then run in the project directory:

        projector devenv build
