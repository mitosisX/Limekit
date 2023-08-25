window = Window();
window.setIcon(images("calc.png"));
window.setSize(280, 80);

theme = Theme("material");
theme.setTheme("light_blue");

mainLay = Layout("vertical");
display = TextEdit();
display.setReadOnly(true);
display.setFixedHeight(35);

mainLay.addChild(display);

grid = GridLayout();
mainLay.addLayout(grid);

let buttonMap = {};

const keyBoard = [
  ["7", "8", "9", "/", "C"],
  ["4", "5", "6", "*", "("],
  ["1", "2", "3", "-", ")"],
  ["0", "00", ".", "+", "="],
];

for (let row = 0; row < keyBoard.length; row++) {
  for (let col = 0; col < keyBoard[row].length; col++) {
    const key = keyBoard[row][col];

    buttonMap[key] = Button(key);
    if (key == "C") buttonMap[key].setMatProperty("danger");
    else if (key == "=") buttonMap[key].setMatProperty("success");

    grid.addChild(buttonMap[key], row, col);
  }
}

for (var keySymbol in buttonMap) {
  if (buttonMap.hasOwnProperty(keySymbol)) {
    var button = buttonMap[keySymbol];
    if (keySymbol !== "=" && keySymbol !== "C") {
      button.onClick(function (obj) {
        const calText = display.getText();
        const newCalText = calText + obj.getText();
        display.setText(newCalText);
      });
    }
  }
}

buttonMap["="].onClick(function () {
  const expression = eval(display.getText());
  display.setText(str(expression));
});
buttonMap["C"].onClick(function () {
  display.setText("");
});

window.setLayout(mainLay);
window.show();
