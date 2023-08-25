theme = Theme("material");
theme.setTheme("light_blue");

window = Window();

mainLay = Layout("vertical");

cal = Calendar();
cal.setDate("12/13/1996");

button = Button("Hello world!");
mainLay.addChild(cal, button);

window.setLayout(mainLay);
window.show();
