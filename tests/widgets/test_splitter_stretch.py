import pytest
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def test_stretch_factors_share_out_growth(qapp):
    from limekit.widgets.label import Label
    from limekit.widgets.splitter import Splitter
    split = Splitter("horizontal")
    a, b, c = Label("a"), Label("b"), Label("c")
    for w in (a, b, c):
        w.setMinimumWidth(10)
        split.addChild(w)
    split.setStretchFactors([0, 1, 0])
    split.resize(900, 100)
    split.show()
    QApplication.processEvents()
    sizes = split.sizes()
    assert sizes[1] > sizes[0] and sizes[1] > sizes[2]
