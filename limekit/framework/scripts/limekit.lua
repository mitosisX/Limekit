app = {
    readFile = function(file)
        return __file.read_file(file)
    end,
    writeFile = function(file, content)
        __file.write_file(file, content)
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
    end
}
