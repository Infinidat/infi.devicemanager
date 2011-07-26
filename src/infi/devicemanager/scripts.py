
def rescan():
    from . import DeviceManager
    dm = DeviceManager()
    for controller in dm.storage_controllers:
        if not controller.is_real_device():
            continue
        controller.rescan()
