-- I use dot nation when accessing functions that return or set something
-- as the syntactic sugar gets in the way

local window = Window()
window:setIcon(images("calc.png"))
window:setSize(280, 80)

local theme = Theme("misc")
theme:setTheme("ue")

local mainLay = Layout("vertical")
local display = TextEdit()
display.setReadonly()
display.setFixedHeight(35)
mainLay:addChild(display)

local grid = GridLayout()
mainLay.addLayout(grid)

local buttonMap = {}

local keyBoard = {
  {"7", "8", "9", "/", "C"},
  {"4", "5", "6", "*", "("},
  {"1", "2", "3", "-", ")"},
  {"0", "00", ".", "+", "="},
}

for row = 1, #keyBoard do
  for col = 1, #keyBoard[row] do
    local key = keyBoard[row][col]
    buttonMap[key] = Button(key)
    if key == "C" then
      buttonMap[key]:setMatProperty("danger")
    elseif key == "=" then
      buttonMap[key]:setMatProperty("success")
    end
    grid:addChild(buttonMap[key], row - 1, col - 1)
  end
end

for keySymbol, button in pairs(buttonMap) do
  if keySymbol ~= "=" and keySymbol ~= "C" then
    button:onClick(function (obj)
      local calText = display.getText()
      local newCalText = calText .. obj:getText()
      display.setText(newCalText)
    end)
  end
end

buttonMap["="]:onClick(function ()
  local expression = eval(display.getText())
  display.setText(str(expression))
end)

buttonMap["C"]:onClick(function ()
  display.setText("")
end)

window:addLayout(mainLay)
window.show()