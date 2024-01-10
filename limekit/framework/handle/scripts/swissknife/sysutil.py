import psutil
import platform

from limekit.framework.core.runner.app import App
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


"""
Cross-platform system information retrieval
"""


class SystemUtils(EnginePart):
    name = "__sysutils"

    @staticmethod
    def get_processes():
        process_dict = {}
        process_list = psutil.process_iter(attrs=["pid", "name"])

        # Print the PID and name of each process
        for process in process_list:
            name = process.info["name"]
            pid = process.info["pid"]
            process_dict.update({name: pid})

        return Converter.table_from(process_dict)

    @staticmethod
    def kill_process(pid):
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

    @staticmethod
    def get_all_cpus():
        return psutil.cpu_count()

    @staticmethod
    def get_users():
        user_details = []

        for user in psutil.users():
            user_details.append(user.name)

        return Converter.to_lua_table(user_details)

    @staticmethod
    def get_battery_percent():
        battery = psutil.sensors_battery()

        return Converter.table_from(
            {
                "percent": battery.percent,
                "remaining_time": battery.secsleft,
                "isPlugged": battery.power_plugged,
            }
        )

    @staticmethod
    def get_driver_letters():
        disk_info = []
        disks = psutil.disk_partitions()

        for drive in disks:
            disk_info.append(
                Converter.table_from(
                    {
                        "device": drive.device,
                        "mountpoint": drive.mountpoint,
                        "fstype": drive.fstype,
                        "opts": drive.opts,
                        "maxfile": drive.maxfile,
                        "maxpath": drive.maxpath,
                    }
                )
            )
        # print(disk_info)
        return Converter.to_lua_table(disk_info)

    # var: device, from the above method
    @staticmethod
    def get_drive_info(device_name):
        disk = psutil.disk_usage(device_name)
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    @staticmethod
    def get_boot_time():
        return psutil.boot_time()

    @staticmethod
    def get_machine_type():
        # Such as AMD64
        return platform.machine()

    @staticmethod
    def get_network_node_name():
        # Gets network node name
        return platform.node()

    @staticmethod
    def get_processor():
        # Intel Family 6 Model 142
        return platform.processor()

    @staticmethod
    def get_platform_name():
        # Windo1-10-10.0.22621-SP0
        return platform.platform()

    @staticmethod
    def get_system_release():
        # returns: 10 when using windows 11
        return platform.release()

    @staticmethod
    def get_os_name():
        # Window, Darwin, Linux
        return platform.system()

    @staticmethod
    def get_os_release():
        return platform.release()

    @staticmethod
    def get_os_version():
        return platform.version()

    @staticmethod
    def get_screen_dimensions():
        screen = App.app.primaryScreen()

        rect = screen.availableGeometry()

        return Converter.table_from({"width": rect.width(), "height": rect.height()})
