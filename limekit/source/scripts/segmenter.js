window = Window();
// window.setStyle("Fusion");
theme = Theme();
// theme.setTheme("light_blue");

window.setIcon(images("divider.ico"));
window.setSize(500, 500);

segments = Segmenter("horizontal");

seg2 = Segmenter("vertical");

list = ListBox();
list.setItems(["JavaScript", "Python", "PySide6"]);
list.onItemSelect(function (obj, txt) {
  print(txt);
});
segments.addChild(list);

list2 = ListBox();
list2.setItems(["Banana", "Mango", "Apple"]);

list3 = ListBox();
list3.setItems(["Banana", "Mango", "Apple"]);

seg2.addChild(list2, list3);

b = Button("Theme");

t = true;
b.onClick(function () {
  r = app.readFile("D:/PyQt/a.txt");
  theme.setTheme(r);
  app.cPopup(window, "Title", "Some error has occured!");
});
seg2.addChild(b);

segments.addChild(seg2);
window.addChild(segments);

window.show();
