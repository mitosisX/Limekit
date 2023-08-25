window = Window();
window.setIcon(images("javascript.png"));
window.setSize(400, 100);

not = Notification();
// not.setMessage('Hello', 'This is some test message',
// images('furniture.png'), 1000)
// not.show()

toolbar = Toolbar();

tray = SysTray();
tray.setImage(images("heart.png"));
tray.setVisibility(true);

menu = Menu();
compose = MenuItem("Compose");
compose.setImage(images("add.png"));

// window.setMenu(menu);

open = MenuItem("Open");
open.setImage(images("open.png"));

exit = MenuItem("Exit");
exit.setImage(images("exit.png"));
menu.addItems(compose, open, exit);
tray.setMenu(menu);

malawi = ToolbarButton();
malawi.setTooltip("Develoepd from Malawi");
malawi.setImage(images("malawi.png"));
toolbar.addAction(malawi);

toolbar.addSeparator();

b = ToolbarButton();
b.setTooltip("hey");
b.setImage(images("icons8_send_50px.png"));
b.onClick(function (self) {
  self.setImage(images("icons8_curriculum_50px.png"));
});
b.setCheckable(true);
toolbar.addAction(b);

window.addToolbar(toolbar);

//menu = Menu(window);

//Theme to be used
theme = Theme("misc");
// theme.setTheme("dark");

mainLayout = HLayout();

mainLay1 = VLayout();

button = Button();
button.setText("Click me");
button.setToolTip("I am a tooltip");
button.onClick(function (x) {
  Clipboard.setText("Hello, from Clipboard!!");

  alert(window, "Alert title", Clipboard.getText());
  return;
  alert(window, "Title here", "Content here", "question", [
    "ok",
    "save",
    "close",
    "cancel",
    "ignore",
    "notoall",
  ]);
  return;
  dialog = InputDialog(window);
  obtainedText = dialog.getText();
  if (obtainedText) x.setText(obtainedText);
});

mainLay1.addChild(button);

// label = Label("Hello World");
combo = ComboBox();
// combo.addItems(["Omega", "Msiska", "Mitosis", "X"]);
combo.addItems(theme.getThemes());
combo.onItemSelect(function (sender, data) {
  theme.setTheme(data);
  // console.log(data);
});

progress = ProgressBar();
progress.setValue(20);

spin = Spinner();
spin.setPrefix("%");
spin.setToolTip("Progressbar percentage");
spin.onValueChange(function (sender, value) {
  progress.setValue(value);
});
spin.setRange(10, 50);

slider = Slider();
slider.setSingleStep(3);
slider.setMaximum(100);
slider.onValueChange(function (sender, value) {
  progress.setProgress(value);
});

timer = Timer(2000);
cou = 40;

timer.onTick(function (self) {
  progress.setValue(cou);
  cou += 10;
  self.stop();
});

timer.start();

edit = TextEdit();
// edit.setInputMask('000.000.000.000;_');
edit.setPlaceholderText("Hello");
edit.onTextChange(function (sender, text) {
  console.log(text);
});

lunch_list = ["egg", "turkey sandwich", "ham sandwich", "cheese", "hummus"];

totalLabel = Label("Total: $0");
totalLabel.setImage(images("icons8_plus_1_year_50px.png"));
// totalLabel.setTextAlign("right");

lay1 = HLayout();
combo1 = ComboBox();
spin1 = Spinner();
spin1.setPrefix("$");
spin1.setRange(1, 100);
combo1.addItems(lunch_list);

lay1.addChildren(combo1, spin1);

lay2 = HLayout();

combo2 = ComboBox();
combo2.addItems(lunch_list);

spin2 = Spinner();
spin2.setPrefix("$");
spin2.setRange(1, 100);
lay2.addChildren(combo2, spin2);

spin1.onValueChange(calculateTotal);
spin2.onValueChange(calculateTotal);

function calculateTotal(sender) {
  total = spin1.getValue() + spin2.getValue();
  totalLabel.setText("Total Spent: " + total);
}

styles = ComboBox();
styles.addItems(window.getStyles());
styles.onItemSelect(function (sender, style) {
  window.setStyle(style);
});

mainLay1.addChildren(combo, spin, progress, slider, edit, styles);
mainLay1.addLayouts(lay1, lay2);
mainLay1.addChild(totalLabel);

mainLay2 = VLayout();

tab = Tab();
tabitem1 = TabItem();

tab.addTabitem(tabitem1, "Cas&h");

tabitem2 = TabItem();

grid1 = GridLayout();
label1 = Label("Ch&eck No.:");
tedit1 = TextEdit();
grid1.addChild(label1, 0, 0);
grid1.addChild(tedit1, 0, 1);

label2 = Label("Bank:");
tedit2 = TextEdit();
grid1.addChild(label2, 0, 2);
grid1.addChild(tedit2, 0, 3);

label3 = Label("Account No.:");
tedit3 = TextEdit();
grid1.addChild(label3, 1, 0);
grid1.addChild(tedit3, 1, 1);

label4 = Label("Sort Code:");
tedit4 = TextEdit();
grid1.addChild(label4, 1, 2);
grid1.addChild(tedit4, 1, 3);

tabitem2.addChild(grid1);

tab.addTabitem(tabitem2, "Chec&k");

tabitem3 = TabItem();
tab.addTabitem(tabitem3, "Credit &Card");

mainLay1.addChild(tab);

mainLayout.addLayouts(mainLay1, mainLay2);

window.setLayout(mainLayout);
window.show();
