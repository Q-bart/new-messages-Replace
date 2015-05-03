#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
# <----Requirements---->
# PyQt4
# grab
# pycurl
# lxml
# </----Requirements---->

import sys
from grab import Grab
from PyQt4 import QtGui, QtCore
import time


class Window(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(100, 100, 500, 200)
        self.setWindowTitle('Replace')
        self.label = QtGui.QLabel(u'Введіть посилання на тему з Українського форуму програмістів')
        self.hello = QtGui.QLabel(u'Вітаю!')
        self.hello.setAlignment(QtCore.Qt.AlignCenter)
        self.explane = QtGui.QLabel(u'''Програма відстежує наявність нових повідомлень з тем на
Українському форумі програмістів
REPLACE.org.ua''')
        self.link = QtGui.QLineEdit()
        self.submit = QtGui.QPushButton('Submit')

        self.Layout = QtGui.QVBoxLayout()
        self.Layout.addWidget(self.hello)
        self.Layout.addWidget(self.explane)
        self.Layout.addWidget(self.label)


        self.fields = QtGui.QHBoxLayout()
        self.fields.addWidget(self.link)
        self.fields.addWidget(self.submit)

        self.setLayout(self.Layout)
        self.Layout.addLayout(self.fields)
        self.connect(self.submit, QtCore.SIGNAL("clicked()"), self.submit_def)

    def submit_def(self):
        introduced = self.link.text() #введене посилання
        if introduced[-1:] != '/':
            introduced = introduced + '/' #Додаємо слеш, якщо немає
        for i in reversed(range(self.filds.count())):  #Видаляєм вміст вікна
            self.filds.itemAt(i).widget().deleteLater()
        for i in reversed(range(self.Layout.count())):
             if type(self.Layout.itemAt(i)) != QtGui.QHBoxLayout:
                self.Layout.itemAt(i).widget().deleteLater()
        label = QtGui.QLabel(u'Програма сповістить вас, коли будуть нові повідомлення')
        self.Layout.addWidget(label)
        self.showMinimized()
        self.tracking(introduced)


    def tracking(self, link):
        self.link = link
        g = Grab()
        g.go(self.link)
        try :                                          # Дізнаємось 1 сторінка чи більше
            self.pages = g.doc.select('//p[@class="paging"]/a')
            self.pages = self.pages.text()
        except Exception:
            self.pages = 1

        if self.pages != 1:       # Якщо сторінок більше ніж 1, формуєм посилання на останню сторінку
            self.pages = g.doc.select('//div[@class="h1"]/h1/small')
            self.pages = self.pages.text()
            self.last_page1 = self.pages[14:-1]
            self.last_page1 = int(self.last_page1)
            self.link_for_last_p1 = self.link + 'page/' + str(self.last_page1)+'/' # посилання на останню сторінку
        else:
            self.last_page1 = 1
            self.link_for_last_p1 = self.link

        g = Grab()
        g.go(self.link_for_last_p1)              #переходим на останню сторінку
        self.messages = g.xpath_list('//h3[@class="hn post-ident"]/span[@class="post-num"]')
        self.message_last1 = self.messages[-1].text   # Номер останнього повідомлення

        self.request = Requests(self.link_for_last_p1, self.message_last1, self.last_page1, self.link)
        self.request.start()  # Новий потік

        self.connect(self.request, QtCore.SIGNAL("mysignal(QString)"), self.open_window,
                     QtCore.Qt.QueuedConnection)

    def open_window(self ):

        modal_w = Popup_window()
        modal_w.show()
        modal_w.exec_()



class Requests(QtCore.QThread):
    def __init__(self, link_for_last_p, message_last, last_page, link, parent=None):
        self.link_for_last_p = link_for_last_p
        self.message_last = message_last
        self.last_page = last_page
        self.link = link
        QtCore.QThread.__init__(self, parent)


    def run(self):         #Потік
        while True:
            time.sleep(15)
            g = Grab()
            g.go(self.link_for_last_p)
            self.messages = g.xpath_list('//h3[@class="hn post-ident"]/span[@class="post-num"]')
            self.current_message = self.messages[-1].text



            if int(self.message_last) % 20 == 0:   #Якщо останнє повідомл. ділиться націло на 20
                self.last_page += 1                # то значить - кінець сторінки
                self.link_for_last_p = self.link + 'page/' + str(self.last_page)+'/' # формуєм посилання нової сторінки

            if int(self.current_message) > int(self.message_last):
                self.message_last = self.current_message
                self.emit(QtCore.SIGNAL("mysignal(QString)"), self.link_for_last_p) #Відкриваєм нове вікно




class Popup_window(QtGui.QWidget):         # вікно сповіщення
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowFlags(QtCore.Qt.Popup)
        self.resize(400, 100)

        self.new_mes_Label = QtGui.QLabel(u'<center>Нове повідомлення</center>')
        self.hyperlink = QtGui.QLabel(u'<center><a href="http://replace.org.ua/search/recent/">Останні активні теми</a></center>')
        self.hyperlink.setOpenExternalLinks(True)


        self.box = QtGui.QHBoxLayout()
        self.logo_label = QtGui.QLabel('<img src="logo.png" align="center">')
        self.box.addWidget(self.logo_label)

        self.text = QtGui.QVBoxLayout()
        self.text.addWidget(self.new_mes_Label)
        self.text.addWidget(self.hyperlink)
        self.setLayout(self.box)
        self.box.addLayout(self.text)
        self.desktop_1 = QtGui.QApplication.desktop()
        self.taskBarHeight = (self.desktop_1.screenGeometry().height() -
            self.desktop_1.availableGeometry().height())
        x = self.desktop_1.width() - self.frameSize().width() - 10
        y = self.desktop_1.height() - self.frameSize().height() - self.taskBarHeight - 10
        self.setGeometry(x, y,400, 100)
        QtGui.QSound("hello.wav").play()



        #self.ok = QtGui.QPushButton('OK')
        #self.ok.setFixedSize(50,20)
        #self.box.addWidget(self.ok)
        #QtCore.QObject.connect(self.ok, QtCore.SIGNAL("clicked()"),
            #QtGui.qApp, QtCore.SLOT("quit()"))



app = QtGui.QApplication(sys.argv)
main = Window()
main.show()
sys.exit(app.exec_())

