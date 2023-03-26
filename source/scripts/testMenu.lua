window = Window();

const menuTemplate = {
  label: "Menu",
  submenu: [
    {
      label: "File",
      submenu: [
        { label: "New", accelerator: "CmdOrCtrl+N" },
        { label: "Open", accelerator: "CmdOrCtrl+O" },
        { label: "Save", accelerator: "CmdOrCtrl+S" },
        { type: "separator" },
        { label: "Exit", accelerator: "CmdOrCtrl+Q" },
      ],
    },
    {
      label: "Edit",
      submenu: [
        { label: "Undo", accelerator: "CmdOrCtrl+Z", role: "undo" },
        { label: "Redo", accelerator: "Shift+CmdOrCtrl+Z", role: "redo" },
        { type: "separator" },
        { label: "Cut", accelerator: "CmdOrCtrl+X", role: "cut" },
        { label: "Copy", accelerator: "CmdOrCtrl+C", role: "copy" },
        { label: "Paste", accelerator: "CmdOrCtrl+V", role: "paste" },
        { type: "separator" },
        { label: "Select All", accelerator: "CmdOrCtrl+A", role: "selectAll" },
      ],
    },
    {
      label: "View",
      submenu: [
        { label: "Reload", accelerator: "CmdOrCtrl+R", role: "reload" },
        {
          label: "Toggle DevTools",
          accelerator: "Alt+CmdOrCtrl+I",
          role: "toggleDevTools",
        },
        { type: "separator" },
        {
          label: "Toggle Full Screen",
          accelerator: "F11",
          role: "toggleFullScreen",
        },
      ],
    },
    {
      label: "Help",
      submenu: [
        { label: "Learn More", click: "lambda" },
        { type: "separator" },
        { label: "About", role: "about" },
      ],
    },
  ],
};

tray = SysTray();
tray.setImage(images("heart.png"));
tray.setVisibility(true);

menu = Menu();

a = MenuItem("Hey");
b = MenuItem();
b.setSeparator(true);
c = MenuItem("Haha");

menu.addItems(a, b, c);
// print(a);
menu.fromTemplate(menuTemplate["submenu"]);
tray.setMenu(menu);
// window.setSystemMenu(menu);

button = Button("Hello world!");
button.onClick(function () {
  tray.gg();
  return;
  d = DDialog(window);
  d.show();
});
window.addChild(button);
window.show();
