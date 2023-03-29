theme = Theme('material');
theme.setTheme('light_blue')

window = Window("GroupBox - Limekit")
window.setIcon(images('lua.png'))
window.setSize(300,200)

mainLay = HLayout()

group1 = GroupBox("&GroupBox 1")
groupLay = VLayout()
b = Button("Hi")
groupLay.addChild(b)
group1.setLayout(groupLay)

group2 = GroupBox("GroupBox 2")
groupLay = VLayout()
b = Button("Hey")
groupLay.addChild(b)
group2.setLayout(groupLay)

group3 = GroupBox("GroupBox 3")
groupLay = VLayout()
b = Button("Hello")
groupLay.addChild(b)
group3.setLayout(groupLay)

mainLay.addChildren(group1, group2, group3)

window.addLayout(mainLay)
window.show()