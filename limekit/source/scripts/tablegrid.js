window = Window();

mainLay = HLayout();

table = TableGrid(10, 10);

Plugin2.change(window);
// The first arg is row, column is second
table.setData(1, 0, "Text");
table.onCellEditFinish(function (obj, row, column) {
  //
});

rightDock = Dock("Employees");

window.addDock(rightDock, "right");
window.setCentralChild(table);

window.show();
