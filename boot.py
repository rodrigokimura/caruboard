import storage
import supervisor
import usb_cdc


def rename(new_name: str):
    storage.remount("/", readonly=False)
    m = storage.getmount("/")
    m.label = new_name
    storage.remount("/", readonly=True)


if __name__ == "__main__":
    usb_cdc.disable()
    supervisor.set_usb_identification(manufacturer="caruboard", product="caruboard")
    rename("caruboard")
