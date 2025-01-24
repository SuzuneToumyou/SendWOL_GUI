#!/usr/bin/python3
# coding: utf-8

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import csv

import socket
import binascii

class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Entry")
        self.layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Name")
        self.layout.addWidget(self.name_input)
        
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("IP")
        self.layout.addWidget(self.ip_input)
        
        self.mac_input = QLineEdit(self)
        self.mac_input.setPlaceholderText("MAC Address")
        self.layout.addWidget(self.mac_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def getInputs(self):
        return self.name_input.text(), self.ip_input.text(), self.mac_input.text()

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.setWindowTitle("SendWOL")
        self.tablewidget = QTableWidget()
        self.tablewidget.setColumnCount(3)
        self.tablewidget.setHorizontalHeaderLabels(["Name", "IP", "MAC Address"])
        
        Any_Cast = "192.168.0.255"
        P_Port = 8019
        
        
        # Set column widths
        self.tablewidget.setColumnWidth(0, 100)  # Set width for "Name" column
        self.tablewidget.setColumnWidth(1, 100)  # Set width for "IP" column
        self.tablewidget.setColumnWidth(2, 150)  # Set width for "MAC Address" column
        
        self.load_data()
        
        self.tablewidget.clicked.connect(self.clicked)
        
        # 行ヘッダーを非表示にする
        self.tablewidget.verticalHeader().setVisible(False)       
        layout.addWidget(self.tablewidget)
        
        # 初期ウィンドウサイズを設定する
        self.resize(375, 400)
        
        # 右クリックメニューを設定する
        self.tablewidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablewidget.customContextMenuRequested.connect(self.openMenu)
        
        # Enable sorting
        self.tablewidget.setSortingEnabled(True)

    def closeEvent(self, event):
        self.save_data()
        event.accept()

    def clicked(self, qmodelindex):
        row = qmodelindex.row()
        col = qmodelindex.column()
        item = self.tablewidget.item(row, col)
        #print(f"Row: {row}, Column: {col}, Text: {item.text()}")

    def openMenu(self, position):
        menu = QMenu()
        
        sendWOLAction = QAction("SendWOL", self)
        sendWOLAction.triggered.connect(self.sendWOL)
        menu.addAction(sendWOLAction)

        addAction = QAction("Add", self)
        addAction.triggered.connect(self.addRow)
        menu.addAction(addAction)
        
        deleteAction = QAction("Delete", self)
        deleteAction.triggered.connect(self.deleteRow)
        menu.addAction(deleteAction)
        
        menu.exec_(self.tablewidget.viewport().mapToGlobal(position))

    def mgpk_send(self, ip_bc, port_bc, macs):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            macs = macs.translate({ord(c): None for c in ':-'})
            data_sent = b'\xff' * 6 + binascii.unhexlify(macs) * 16
            s.sendto(data_sent, (ip_bc, port_bc))
           
    def sendWOL(self):
        selected = self.tablewidget.selectedItems()
        if selected:
            row = selected[0].row()
            item = self.tablewidget.item(row, 2)  # 3列目のカラム
            if item:
                #print(f"sendWOL: {item.text()}")
                self.mgpk_send(Any_Cast, P_Port, item.text())

    def deleteRow(self):
        selected = self.tablewidget.selectedItems()
        if selected:
            row = selected[0].row()
            self.tablewidget.removeRow(row)
            #print(f"Deleted row: {row}")

    def addRow(self):
        dialog = AddDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, ip, mac = dialog.getInputs()
            row_position = self.tablewidget.rowCount()
            self.tablewidget.insertRow(row_position)
            self.tablewidget.setItem(row_position, 0, QTableWidgetItem(name))
            self.tablewidget.setItem(row_position, 1, QTableWidgetItem(ip))
            self.tablewidget.setItem(row_position, 2, QTableWidgetItem(mac))
            #print(f"Added row: {name}, {ip}, {mac}")

    def save_data(self):
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for row in range(self.tablewidget.rowCount()):
                row_data = []
                for column in range(self.tablewidget.columnCount()):
                    item = self.tablewidget.item(row, column)
                    row_data.append(item.text() if item else '')
                writer.writerow(row_data)

    def load_data(self):
        try:
            with open('data.csv', 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
                self.tablewidget.setRowCount(len(rows))
                for row_index, row_data in enumerate(rows):
                    for column_index, data in enumerate(row_data):
                        self.tablewidget.setItem(row_index, column_index, QTableWidgetItem(data))
        except FileNotFoundError:
            pass

app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec_())