import psutil
from limekit.framework.core.engine.app_engine import EnginePart

"""
Cross-platform system information retrieval
"""


class SystemUtils(EnginePart):
    name = "__sysutils"

    @classmethod
    def get_processes(cls):
        process_dict = {}
        process_list = psutil.process_iter(attrs=["pid", "name"])

        # Print the PID and name of each process
        for process in process_list:
            name = process.info["name"]
            pid = process.info["pid"]
            process_dict.update({name: pid})

        return process_dict

    @classmethod
    def kill_process(cls, pid):
        # Check if the process with the specified PID exists
        if psutil.pid_exists(pid):
            try:
                # Get the process object for the specified PID
                target_process = psutil.Process(pid)

                # Terminate the process
                target_process.terminate()

                return True
            except psutil.NoSuchProcess:
                return False
        else:
            return False

    @classmethod
    def get_all_cpus(cls):
        return psutil.cpu_count()

    @classmethod
    def get_users(cls):
        user_details = []

        for user in psutil.users():
            user_details.append(user.name)

        return user_details

    @classmethod
    def get_battery_percent(cls):
        battery = psutil.sensors_battery()

        return {
            "percent": battery.percent,
            "remaining_time": battery.secsleft,
            "isPlugged": battery.power_plugged,
        }

    @classmethod
    def get_driver_letters(cls):
        disk_info = []
        disks = psutil.disk_partitions()

        for drive in disks:
            disk_info.append(
                {
                    "device": drive.device,
                    "mountpoint": drive.mountpoint,
                    "fstype": drive.fstype,
                    "opts": drive.opts,
                    "maxfile": drive.maxfile,
                    "maxpath": drive.maxpath,
                }
            )
        # print(disk_info)
        return disk_info

    # var: device, from the above method
    @classmethod
    def get_drive_info(cls, device_name):
        disk = psutil.disk_usage(device_name)
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    @classmethod
    def get_boot_time(cls):
        return psutil.boot_time()
