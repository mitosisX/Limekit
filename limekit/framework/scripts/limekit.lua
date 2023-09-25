app = {
    getNextDNAStrand = function(dna)
        return __converters.next_dna_strand(dna)
    end,
    splitString = function(text, delimeter)
        return __converters.string_split(text, delimeter)
    end,
    doQuickSort = function(list)
        return __sorter.quick_sort(list)
    end,
    makeHash = function(type_, text)
        return __converters.make_hash_string(type_, text)
    end,
    hexToRGB = function(hex)
        return __converters.hex_to_rgb(hex)
    end,
    readFileLines = function(file)
        return __fileutils.read_file_lines_count(file)
    end,
    bytesToReadableSize = function(bytes)
        return __converters.convert_bytes(bytes)
    end,
    -- ################## encoding
    toBase64 = function(text)
        return __encoding.base64_encode(text)
    end,
    fromBase64 = function(text)
        return __encoding.base64_decode(text)
    end,
    -- Encoding #######################
    setFont = function(font, size)
        __font.set_font(font, size)
    end,
    emoji = function(emoji)
        return __emoji.get(emoji)
    end,
    ---- ################## File and folder utils
    extractZip = function(file, dest)
        return __fileutils.extract_zip_file(file, dest)
    end,
    checkIsDir = function(path)
        return __fileutils.is_dir(path)
    end,
    checkIfExists = function(path)
        return __fileutils.exists(path)
    end,
    checkFileEmpty = function(file)
        return __fileutils.is_empty_file(file)
    end,
    checkDirEmpty = function(dir)
        return __fileutils.is_empty_dir(dir)
    end,
    getFileSize = function(file)
        return __fileutils.get_file_size(file)
    end,
    readFile = function(file, encoding)
        if not encoding then
            encoding = "UTF-8"
        end
        return __file.script_file_reader(file, encoding)
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
    writeJSON = function(file, content)
        __fileutils.write_file_json(file, content)
    end,
    -- File and folder utils ##################
    quit = function()
        __quit()
    end,
    alert = function(parent, title, message, icon, buttons)
        return __alert(parent, title, message, icon, buttons)
    end,
    aboutPopup = function(parent, title, message)
        return __aPopup(parent, title, message)
    end,
    criticalPopup = function(parent, title, message)
        return __cPopup(parent, title, message)
    end,
    infoPopup = function(parent, title, message)
        return __iPopup(parent, title, message)
    end,
    questionPopup = function(parent, title, message)
        return __qPopup(parent, title, message)
    end,
    warningPopup = function(parent, title, message)
        return __wPopup(parent, title, message)
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
    createDir = function(path)
        __fileutils.make_dirs(path)
    end,
    -- ################## CPU or Sys related
    playSound = function(file)
        __sound.play_sound(file)
    end,
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
    end,
    getDiskInfo = function(disk)
        -- Gets information for disk; total; free; used; percentage
        return __sysutils.get_drive_info(disk)
    end,
    getBootTime = function()
        return __sysutils.get_boot_time()
    end,
    getMachineType = function()
        return __sysutils.get_machine_type()
    end,
    getNetworkNodeName = function()
        return __sysutils.get_network_node_name()
    end,
    getProcessorName = function()
        return __sysutils.get_processor()
    end,
    getPlatformName = function()
        return __sysutils.get_platform_name()
    end,
    getSystemRelease = function()
        return __sysutils.get_system_release()
    end,
    getOSName = function()
        return __sysutils.get_os_name()
    end,
    getOSRelease = function()
        return __sysutils.get_os_release()
    end,
    getOSVersion = function()
        return __sysutils.get_os_release()
    end,
    -- CPU or Sys related ##################
    -- ################## validators
    checkUniqueChars = function(text)
        return __validators.is_contains_unique_chars(text)
    end
    -- validators ##################

}
