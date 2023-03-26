window = Window("Hello from Lua");
window.setIcon(images('lua.png'))
window.setSize(500, 400)

theme = Theme()
theme.setTheme('light_blue')

for a=5, 10 do
button = Button("Button " .. a);
button.onClick(function(obj)
    obj.setText('Changed')
end)
window.addChild(button);
end

window.show();
