# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Ui_NewConnectDlg(object):
    def setupUi(self, NewConnectDlg):
        NewConnectDlg.setWindowTitle(u"Connect VHD")
        self.gridlayout = QGridLayout(NewConnectDlg)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)

        urlLabel = QLabel(u"URL*:")
        self.urlLineEdit = QLineEdit()
        urlLabel.setBuddy(self.urlLineEdit)
        self.gridlayout.addWidget(urlLabel, 0, 0)
        self.gridlayout.addWidget(self.urlLineEdit, 0, 1)

        accountkeyLabel = QLabel(u"ACCOUNT_KEY:")
        self.accountkeyLineEdit = QLineEdit()
        accountkeyLabel.setBuddy(self.accountkeyLineEdit)
        self.gridlayout.addWidget(accountkeyLabel, 1, 0)
        self.gridlayout.addWidget(self.accountkeyLineEdit, 1, 1)

        filenameLabel = QLabel(u"FILENAME:")
        self.filenameLineEdit = QLineEdit()
        filenameLabel.setBuddy(self.filenameLineEdit)
        self.gridlayout.addWidget(filenameLabel, 2, 0)
        self.gridlayout.addWidget(self.filenameLineEdit, 2, 1)

        pathLabel = QLabel(u"PATH*:")
        self.pathLineEdit = QLineEdit()
        pathLabel.setBuddy(self.pathLineEdit)
        self.gridlayout.addWidget(pathLabel, 3, 0)
        self.gridlayout.addWidget(self.pathLineEdit, 3, 1)

        extensionLabel = QLabel(u"EXTENSION:")
        self.extensionLineEdit = QLineEdit()
        extensionLabel.setBuddy(self.extensionLineEdit)
        self.gridlayout.addWidget(extensionLabel, 4, 0)
        self.gridlayout.addWidget(self.extensionLineEdit, 4, 1)

        typeLabel = QLabel(u"TYPE:")
        self.typeLineEdit = QLineEdit()
        typeLabel.setBuddy(self.typeLineEdit)
        self.gridlayout.addWidget(typeLabel, 5, 0)
        self.gridlayout.addWidget(self.typeLineEdit, 5, 1)

        self.buttonBox = QDialogButtonBox(NewConnectDlg)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|
                    QDialogButtonBox.NoButton|QDialogButtonBox.Ok)
        self.gridlayout.addWidget(self.buttonBox, 6, 1)

        QObject.connect(self.buttonBox, SIGNAL("accepted()"),
                               NewConnectDlg.accept)
        QObject.connect(self.buttonBox, SIGNAL("rejected()"),
                               NewConnectDlg.reject)
        QMetaObject.connectSlotsByName(NewConnectDlg)
