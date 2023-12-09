class Script:
    @classmethod
    def read_app_lua(cls):
        return """
    app = {
    isIDE = function()
        return __engineState()
    end,
    joinPaths = function(...)
        return __paths.join_paths(...)
    end,
    getStandardPath = function(path)
        return __paths.get_path(path)
    end,
    runProject = function(path)
        return __appCore(path)
    end,
    randomChoice = function(table_)
        return __utils.random_string(table_)
    end,
    splitString = function(string, delimeter)
        return __utils.str_split(string, delimeter)
    end,
    range = function(start, end_)
        return __utils.int_range(start, end_)
    end,
    sortArray = function(array)
        return __utils.sort_array(array)
    end,
    sortTable = function(tbl)
        return __utils.sort_table(tbl)
    end,
    joinTables = function(...)
        return __utils.join_tables(...)
    end,
    -- Time not to be in thousands, ie, 1000, but 1, 2...
    sleep = function(seconds)
        __utils.sleep(seconds)
    end,
    weightedGraph = function(...)
        return __utils.weighted_graph(...)
    end,
    -- Global theming ##################
    getStyles = function()
        return __appMisc.getStyles()
    end,
    setStyle = function(style)
        __appMisc.setStyle(style)
    end,
    -- ################## Global theming
    quickSort = function(list)
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
    setFontFile = function(file, size)
        __font.set_font(file, size)
    end,
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
    checkIfFolder = function(path)
        return __fileutils.is_dir(path)
    end,
    exists = function(path)
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
    -- Gets the file name and extension from given path
    getFileExt = function(path)
        return __fileutils.get_filename_ext(path)
    end,
    copyFile = function(source, destination)
        __fileutils.copy_file(source, destination)
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
    ---- ################## Popups
    fontPickerDialog = function()
        return __fontDialog().display()
    end,
    saveFileDialog = function(window, title, dir, filters)
        return __saveFileDialog(window).display(window, title, dir, filters)
    end,
    folderPickerDialog = function(window, title)
        return __folderPickerDialog().display(window, title)
    end,
    openFileDialog = function(window, title, dir, filters)
        return __openFileDialog(window).display(window, title, dir, filters)
    end,
    colorPickerDialog = function(window, type_)
        return __colorPicker(window).display(type_)
    end,
    -- ## Input Dialogs
    textInputDialog = function(parent, title, label)
        return __textInputDialog.show(parent, title, label)
    end,
    multilineInputDialog = function(parent, title, label, content)
        if not content then
            content = ""
        end
        return __multilineInputDialog.show(parent, title, label, content)
    end,
    comboBoxInputDialog = function(parent, title, label, items, index)
        if not index then
            index = 0
        end
        return __itemInputDialog.show(parent, title, label, items, index)
    end,
    integerInputDialog = function(parent, title, label, value, minValues, maxValue, step)
        if not step then
            step = 2
        end
        return __integerInputDialog.show(parent, title, label, value, minValues, maxValue, step)
    end,
    doubleInputDialog = function(parent, title, label, value, minValues, maxValue, step)
        if not step then
            step = 2
        end
        return __doubleInputDialog.show(parent, title, label, value, minValues, maxValue, step)
    end,
    -- ## Input Dialogs
    alert = function(parent, title, message)
        return Alert.show(parent, title, message)
    end,
    -- Contains the 'do not show this message again' button
    infoMessageDialog = function(parent, title, message)
        __errorDialog(parent, title, message)
    end,
    aboutAlertDialog = function(parent, title, message)
        return __aPopup(parent, title, message)
    end,
    criticalAlertDialog = function(parent, title, message)
        return __cPopup(parent, title, message)
    end,
    infoAlertDialog = function(parent, title, message)
        return __iPopup(parent, title, message)
    end,
    questionAlertDialog = function(parent, title, message)
        return __qPopup(parent, title, message).display()
    end,
    warningAlertDialog = function(parent, title, message)
        return __wPopup(parent, title, message)
    end,
    ---- ################## Popups
    evaluate = function(script)
        __lua_evaluate(script)
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
    renameFile = function(file, file_new)
        return __fileutils.rename_file(file, file_new)
    end,
    renameFolder = function(dir, dir_new)
        return __fileutils.rename_dir(dir, dir_new)
    end,
    createFolder = function(path)
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

    """
