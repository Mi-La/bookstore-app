import sys
import os
import pandas as pd
from pathlib import Path
from io import StringIO
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget
)

class FilePicker(QWidget):
    def __init__(self, parent=None, file_filter="Všechny soubory (*.*)", mode="open"):
        super().__init__(parent)

        self._mode = mode;
        self._file_filter = file_filter
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText(self._file_filter)
        self._browse_button = QToolButton()
        self._browse_button.setText("...")
        self._browse_button.clicked.connect(self.select_file)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self._path_edit)
        hbox.addWidget(self._browse_button)

    def select_file(self):
        if self._mode == "open":
            file, _ = QFileDialog.getOpenFileName(
                self,
                self._file_filter,
                self._path_edit.text(),
                self._file_filter,
            )
            if file:
                self._path_edit.setText(file)
        else:
            file, _ = QFileDialog.getSaveFileName(
                self,
                self._file_filter,
                self._path_edit.text(),
                self._file_filter,
            )

            if file:
                self._path_edit.setText(file)

    @property
    def text(self):
        return self._path_edit.text()


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path


def readOrdersXML(filename):
    orders = pd.read_xml(filename, stylesheet=resource_path("data/orders.xsl")).dropna(axis=1, how="all")
    orders_cust = orders[orders["code"] == "cust"]
    orders_no_code = orders[orders["code"].isnull()].copy()
    orders_no_code["code"] = "no-code"
    orders = orders[(orders["code"] != "cust") & orders["code"].notnull()]

    columns_to_sum = pd.Index(["pieces"])
    other_columns = orders.columns.drop(columns_to_sum)
    sold = orders.groupby(by=["code"]).agg({
        **{col: "sum" for col in columns_to_sum},
        **{col: "first" for col in other_columns}
    })
    sold = pd.concat([sold, orders_cust.set_index("code"), orders_no_code.set_index("code")])
    return sold


def writeOrdersToCSV(orders, filename):
    orders_csv = orders[["name", "pieces", "priceIncldVAT"]]
    orders_csv.to_csv(filename, sep=";", decimal=",")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Knihkupectví U Pašků")
        self.setMinimumWidth(320);
        self.setMinimumHeight(240);

        central = QWidget()
        self.setCentralWidget(central)

        vbox = QVBoxLayout(central)
        self._xml = FilePicker(self, "XML soubor (*.xml)")
        vbox.addWidget(self._xml)
        self._csv = FilePicker(self, "CSV soubor (*.csv)", mode="save")
        vbox.addWidget(self._csv)

        vbox.addStretch();

        ok = QPushButton("Ok")
        ok.clicked.connect(self.ok)
        vbox.addWidget(ok)

    def ok(self):
        if not self._xml.text:
            QMessageBox.warning(self, "Chyba", "Vyber XML soubor pro otevření!")
            return
        if not self._csv.text:
            QMessageBox.warning(self, "Chyba", "Vyber CSV soubor pro uložení!")
            return

        try:
            orders = readOrdersXML(self._xml.text)
        except Exception as e:
            QMessageBox.warning(self, "Chyba", f"Selhalo čtení XML: {e}")
            return

        try:
            writeOrdersToCSV(orders, self._csv.text)
        except Exception as e:
            QMessageBox.warning(self, "Chyba", f"Selhalo ukládání CSV: {e}")
            return

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
