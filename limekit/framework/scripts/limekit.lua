app = {
    emoji = function(emoji)
        return __emoji.get(emoji)
    end,
    ---- ##### File utils
    readFile = function(file, encoding)
        if not encoding then
            encoding = "UTF-8"
        end
        return __file.read_file(file, encoding)
    end,
    writeFile = function(file, content, encoding)
        if not encoding then
            encoding = "UTF-8"
        end
        __file.write_file(file, content, encoding)
    end,
    createFile = function(file)
        __file.create_file(file)
    end,
    appendFile = function(file, content)
        __file.append_file(file, content)
    end,
    writeBytes = function(file, bytes)
        __file.writeBytes(file, bytes)
    end,
    readJSON = function(file)
        return __fileutils.read_file_json(file)
    end,
    -- ##### File utils
    aPopup = function(parent, title, message)
        __aPopup(parent, title, message)
    end,
    cPopup = function(parent, title, message)
        __cPopup(parent, title, message)
    end,
    iPopup = function(parent, title, message)
        __iPopup(parent, title, message)
    end,
    qPopup = function(parent, title, message, buttons)
        __qPopup(parent, title, message, buttons)
    end,
    wPopup = function(parent, title, message)
        __wPopup(parent, title, message)
    end,
    execute = function(script)
        __lua_execute(script)
    end,
    setClipboardText = function(text)
        __clipboard.setText(text)
    end,
    getClipboardText = function()
        return __clipboard.getText()
    end,
    listFolder = function(path)
        return __Path.listDir(path)
    end,
    -- ##### CPU or Sys related
    getProcesses = function()
        return __sysutils.get_processes()
    end,
    killProcess = function(pid)
        return __sysutils.kill_process(pid)
    end,
    getCPUCount = function()
        return __sysutils.get_all_cpus()
    end,
    getUsers = function()
        return __sysutils.get_users()
    end,
    getBatteryInfo = function()
        return __sysutils.get_battery_percent()
    end,
    getDiskPartitions = function()
        return __sysutils.get_driver_letters()
    end
    -- ##### 
}
