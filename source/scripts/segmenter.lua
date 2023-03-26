window = Window("Hello from Lua");

theme = Theme("modern");
theme:setTheme("light");

window:setIcon(images("divider.ico"));
window:setSize(500, 500);

segments = Segmenter("horizontal");

seg2 = Segmenter("vertical");

list = ListBox();
list:setItems({"Omega Msiska", "New", "Lua", "Material", "Framework", "Malawi"});
list:onItemSelect(function (obj, txt)
  print(txt);
end);
segments:addChild(list);

list2 = ListBox();
list2:setItems({"Banana", "Mango", "Apple"});

list3 = ListBox();
list3:setItems({"Banana", "Mango", "Apple"});

seg2:addChild(list2, list3);

b = Button("Theme");

t = true;
b:onClick(function ()
  -- r = app.readFile("somefile.txt");
  theme.setTheme('dark');
  -- app.cPopup(window, "Title", "Some error has occured!");
end);

l = Label("gitub.com/mitosisx")
seg2:addChild(b, l);

segments.addChild(seg2);
window.addChild(segments);

window.show();
