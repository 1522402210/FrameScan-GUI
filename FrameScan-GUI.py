#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import sys, os, webbrowser, threading,importlib
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import csv, re, requests, time, sqlite3
from GUI.FrameScan import Ui_MainWindow
from GUI.showPlugins import Ui_Form
from GUI.Plugins_information import Ui_Plugins_information
import win32con
import win32clipboard as wincld
import frozen_dir, queue

SETUP_DIR = frozen_dir.app_path()
sys.path.append(SETUP_DIR)
DB_NAME = 'POC_DB.db'
version = '1.2.6'
update_time = '20200530'
# 禁用安全警告
requests.packages.urllib3.disable_warnings()
class MainWindows(QtWidgets.QMainWindow, Ui_MainWindow):  # 主窗口
    def __init__(self, parent=None):
        super(MainWindows, self).__init__(parent)
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) #去掉标题栏
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('main.ico'))
        # self.setFixedSize(self.width(), self.height())  # 设置宽高不可变
        # self.Ui.exit.clicked.connect(QtCore.QCoreApplication.instance().quit)  #退出
        self.Ui.action_vuln_start.triggered.connect(self.vuln_Start)  # 开始扫描
        self.Ui.action_vuln_import.triggered.connect(self.vuln_import_file)  # 导入文件列表
        self.Ui.pushButton_vuln_file.clicked.connect(self.vuln_import_file)  # 导入地址
        self.Ui.action_vuln_export.triggered.connect(self.vuln_export_file)  # 导出扫描结果
        self.Ui.pushButton_vuln_export.clicked.connect(self.vuln_export_file)  # 导出结果
        self.Ui.action_vuln_reload.triggered.connect(self.vuln_reload_Plugins)  # 重新加载插件
        self.Ui.action_vuln_showplubins.triggered.connect(self.vuln_ShowPlugins)  # 查看插件
        self.Ui.pushButton_vuln_showplugins.clicked.connect(self.vuln_ShowPlugins)  # 查看插件
        self.Ui.pushButton_vuln_start.clicked.connect(self.vuln_Start)  # 开始扫描\
        self.Ui.action_about.triggered.connect(self.about)  # 关于
        self.Ui.action_update.triggered.connect(self.version_update)  # 更新
        self.Ui.action_ideas.triggered.connect(self.ideas)  # 意见反馈
        self.Ui.pushButton_vuln_all.clicked.connect(self.vuln_all)  # 全选
        self.Ui.pushButton_vuln_noall.clicked.connect(self.vuln_noall)  # 反选
        # 右键菜单
        self.Ui.tableWidget_vuln.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.Ui.tableWidget_vuln.customContextMenuRequested['QPoint'].connect(self.createtableWidget_vulnMenu)
        self.timer = QTimer()  # 设定一个定时器用来显示时间
        self.timer.timeout.connect(self.showtime)
        self.timer.start()
        self.loadplugins()
        self.url_list = []
        self.readfile()
        # 设置漏洞扫描表格属性  列宽度
        self.Ui.tableWidget_vuln.setColumnWidth(0, 150)
        self.Ui.tableWidget_vuln.setColumnWidth(1, 240)
        self.Ui.tableWidget_vuln.setColumnWidth(2, 280)
        self.Ui.tableWidget_vuln.setColumnWidth(3, 80)
        #帮助
        othersmenubar = self.menuBar()  # 获取窗体的菜单栏
        others = othersmenubar.addMenu("帮助")
        for i in ["关于",'更新','意见反馈']:
            sub_action = QAction(QIcon(''), i, self)
            others.addAction(sub_action)
        impMenu = QMenu("皮肤风格", self)
        for z in json_qss:
            sub_action = QAction(QIcon(''), z, self)
            impMenu.addAction(sub_action)
        others.addMenu(impMenu)
        others.triggered[QAction].connect(self.show_others)
    def readfile(self):
        try:
            global json_qss
            f=open('QSS/list.txt','r',encoding='utf-8')
            json_qss=json.load(f)
            # print(json_data)
            f.close()
            f=open('QSS/Setup.txt','r',encoding='utf-8')
            qss_Setup=json.load(f)
            with open("QSS/"+qss_Setup["QSS"], 'r', encoding='utf-8') as f:
                qss_style = f.read()
                f.close()
            MainWindows.setStyleSheet(self,qss_style)
            f.close()
        except Exception as e :
            QMessageBox.critical(self,'Error',str(e))
            pass
    def createtableWidget_vulnMenu(self):
        '''''
                创建右键菜单
                '''
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.Ui.tableWidget_vuln.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.Ui.tableWidget_vuln.customContextMenuRequested.connect(self.showContextMenu)
        # 创建QMenu
        self.contextMenu = QtWidgets.QMenu(self)
        self.copy_textEdit = self.contextMenu.addAction(u'复制')
        self.clear_textEdit = self.contextMenu.addAction(u'清空')
        self.delete_textEdit= self.contextMenu.addAction(u'删除')
        # 将动作与处理函数相关联
        # 这里为了简单，将所有action与同一个处理函数相关联，
        # 当然也可以将他们分别与不同函数关联，实现不同的功能
        self.copy_textEdit.triggered.connect(self.Copy_tableWidget_vuln)
        self.clear_textEdit.triggered.connect(self.Clear_tableWidget_vuln)
        self.delete_textEdit.triggered.connect(self.Delete_tableWidget_vuln)
    # 右键点击时调用的函数，移动鼠标位置
    def showContextMenu(self, pos):
        # 菜单显示前，将它移动到鼠标点击的位置
        self.contextMenu.move(QtGui.QCursor.pos())
        self.contextMenu.show()
    def Copy_tableWidget_vuln(self):
        try:
            data = self.Ui.tableWidget_vuln.selectedItems()[0].text()
            # print(data)
            # 访问剪切板，存入值
            wincld.OpenClipboard()
            wincld.EmptyClipboard()
            wincld.SetClipboardData(win32con.CF_UNICODETEXT, data)
            wincld.CloseClipboard()
        except:
            pass
    def Clear_tableWidget_vuln(self):
        for i in range(0, self.Ui.tableWidget_vuln.rowCount()):  # 循环行
            self.Ui.tableWidget_vuln.removeRow(0)
    def Delete_tableWidget_vuln(self):
        self.Ui.tableWidget_vuln.removeRow(self.Ui.tableWidget_vuln.currentRow())#删除选中的行
    # 显示时间
    def showtime(self):
        datetime = QDateTime.currentDateTime()
        text = datetime.toString("yyyy-MM-dd hh:mm:ss")
        self.setWindowTitle("FrameScan-GUI v"+version+" 测试版 "+update_time+"      %s" % text)
    # 得到选中的方法
    def get_methods(self):
        all_data = []
        conn2 = sqlite3.connect(DB_NAME)
        # 创建一个游标 curson
        cursor = conn2.cursor()
        item = QtWidgets.QTreeWidgetItemIterator(self.Ui.treeWidget_Plugins)
        # 该类的value()即为QTreeWidgetItem
        while item.value():
            if not item.value().parent():  # 判断有没有父节点
                pass
            else:  # 输出所有子节点
                if item.value().checkState(0) == QtCore.Qt.Checked:
                    # 参考网上的方法，判断有无父母结点后再分别操作的那个，实在找不到更直接的
                    sql = "SELECT  * from POC where pocmethods = '%s'"%(item.value().text(0))
                    cursor.execute(sql)
                    xuanzhong_data = cursor.fetchall()
                    all_data.append(xuanzhong_data)
            item = item.__iadd__(1)
        conn2.close()
        #返回所有选中的数据
        return all_data
    # 开始扫描
    def vuln_Start(self):
        threadnum = int(self.Ui.threadsnum.currentText())
        self.Ui.textEdit_log.clear()
        target = []  # 存放扫描的URL
        if self.url_list:
            target = self.url_list
        else:
            url = self.Ui.lineEdit_vuln_url.text()
            if 'http://' in url or 'https://' in url:
                target.append(url.strip())
        if not target:
            self.Ui.textEdit_log.append(
                "[%s]Info:未获取到URL地址。" % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
            return 0
        all_data = self.get_methods()
        if not all_data:
            self.Ui.textEdit_log.append(
                "[%s]Info:未选择插件。" % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
            return 0
        else:
            self.Ui.textEdit_log.append(
                "[%s]Info:共加载%s个插件。" % ((time.strftime('%H:%M:%S', time.localtime(time.time()))), len(all_data)))
            self.Ui.textEdit_log.append(
                "[%s]Info:共获取到%s个URL地址。" % ((time.strftime('%H:%M:%S', time.localtime(time.time()))), len(target)))
            self.Ui.textEdit_log.append(
                "[%s]Info:正在创建队列..." % ((time.strftime('%H:%M:%S', time.localtime(time.time())))))
            thread = threading.Thread(target=self.add_queue, args=(target,all_data,threadnum))
            thread.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
            thread.start()
    def add_queue(self,target,all_data,threadnum):
        portQueue = queue.Queue()  # 待检测端口队列，会在《Python常用操作》一文中更新用法
        if self.Ui.jump_url.checkState() != Qt.Checked:
            num=  len(target)
            for u in target:
                for xuanzhong_data in all_data:
                    for p in xuanzhong_data:
                        # print(p)
                        cms_name = p[1]
                        filename = 'Plugins/' + cms_name + '/' + p[2]
                        poc_methods = 'Plugins.' + cms_name + '.' + p[6]
                        portQueue.put(u + '$$$' + filename + '$$$' + poc_methods)
        else:
            num = 0
            for u in target:
                headers = {'content-type': 'application/json',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
                try:
                    dara = requests.get(u, timeout=3, headers=headers)
                except Exception as  e:
                    row = self.Ui.tableWidget_vuln.rowCount()  # 获取行数
                    self.Ui.tableWidget_vuln.setRowCount(row + 1)
                    urlItem = QTableWidgetItem(u)
                    resultItem = QTableWidgetItem('无法访问')
                    self.Ui.tableWidget_vuln.setItem(row, 0, urlItem)
                    self.Ui.tableWidget_vuln.setItem(row, 3, resultItem)
                    continue
                else:
                    for xuanzhong_data in all_data:
                        for p in xuanzhong_data:
                            # print(p)
                            cms_name = p[1]
                            filename = 'Plugins/' + cms_name + '/' + p[2]
                            poc_methods = 'Plugins.' + cms_name + '.' + p[6]
                            portQueue.put(u + '$$$' + filename + '$$$' + poc_methods)
                    num+= 1
                    # 限制线程数小于队列大小
        if threadnum > portQueue.qsize():
            threadnum = portQueue.qsize()
        # print(portQueue.qsize())
        self.Ui.textEdit_log.append(
            "[%s]Info:共获取到%s个有效URL地址。" % ((time.strftime('%H:%M:%S', time.localtime(time.time()))), num))
        self.Ui.textEdit_log.append(
            "[%s]Start:扫描开始..." % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
        self.Ui.action_vuln_import.setEnabled(False)
        self.Ui.pushButton_vuln_file.setEnabled(False)
        self.Ui.action_vuln_start.setEnabled(False)
        self.Ui.pushButton_vuln_start.setEnabled(False)
        for i in range(threadnum):
            thread = threading.Thread(target=self.vuln_scan, args=(portQueue, threadnum))
            thread.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
            thread.start()
    # 调用脚本
    def vuln_scan(self, portQueue, threadnum):
        # print(portQueue.queue)  #输出所有队列
        while 1:
            try:
                if portQueue.empty() :  # 队列空就结束
                    time.sleep(3)
                    self.Ui.action_vuln_import.setEnabled(True)
                    self.Ui.pushButton_vuln_file.setEnabled(True)
                    self.Ui.action_vuln_start.setEnabled(True)
                    self.Ui.pushButton_vuln_start.setEnabled(True)
                    return
                else:
                    all = portQueue.get()  # 从队列中取出
                    url = all.split('$$$')[0]
                    filename = all.split('$$$')[1]
                    poc_methods = all.split('$$$')[2]
                    # nnnnnnnnnnnn1 = importlib.import_module(poc_methods)
                    nnnnnnnnnnnn1 = importlib.machinery.SourceFileLoader(poc_methods, filename).load_module()
                    result = nnnnnnnnnnnn1.run(url)
                    # print(result)
                    result_url = url.replace("http://", "").replace("https://", "")
                    self.Ui.textEdit_log.append(
                        "[%s]Info:%s----%s----%s。" % (
                            (time.strftime('%H:%M:%S', time.localtime(time.time()))), result_url, result[0], result[2]))
                    if result[2] != '不存在' and result[2] != '':
                        row = self.Ui.tableWidget_vuln.rowCount()  # 获取行数
                        self.Ui.tableWidget_vuln.setRowCount(row + 1)
                        urlItem = QTableWidgetItem(result_url)
                        nameItem = QTableWidgetItem(result[0])
                        payloadItem = QTableWidgetItem(result[1])
                        resultItem = QTableWidgetItem(result[2])
                        filenameItem = QTableWidgetItem(filename)
                        self.Ui.tableWidget_vuln.setItem(row, 0, urlItem)
                        self.Ui.tableWidget_vuln.setItem(row, 1, nameItem)
                        self.Ui.tableWidget_vuln.setItem(row, 3, resultItem)
                        self.Ui.tableWidget_vuln.setItem(row, 2, filenameItem)
                        self.Ui.tableWidget_vuln.setItem(row, 4, payloadItem)
            except Exception as e:
                self.Ui.textEdit_log.append(
                    "[%s]Error:%s脚本执行错误！\n[Exception]:\n%s" % (
                        (time.strftime('%H:%M:%S', time.localtime(time.time()))), filename, e))
                pass
    # 初始化加载插件
    def loadplugins(self):
        if os.path.isfile(DB_NAME):
            conn = sqlite3.connect(DB_NAME)
        else:
            box = QtWidgets.QMessageBox()
            box.warning(self, "提示", "数据文件不存在，正在重新加载数据库！")
            self.vuln_reload_Plugins()
            return 0
        try:
            # 创建一个游标 curson
            cursor = conn.cursor()
            # 列出所有数据
            sql = "SELECT cmsname,pocmethods from POC"
            cursor.execute(sql)
            values = cursor.fetchall()
        except Exception as e:
            box = QtWidgets.QMessageBox()
            box.warning(self, "提示", "数据文件错误：\n%s" % e)
            return 0
        # 将查询的值组合为字典包含列表的形式
        cms_name = {}
        for cms in values:
            cms_name[cms[0]] = []
        for cms in values:
            if cms[0] in cms_name.keys():
                cms_name[cms[0]].append(cms[1])
        for cms in cms_name:
            # 设置root为self.treeWidget_Plugins的子树，故root是根节点
            root = QTreeWidgetItem(self.Ui.treeWidget_Plugins)
            root.setText(0, cms)  # 设置根节点的名称
            root.setCheckState(0, Qt.Unchecked)  # 开启复选框
            for poc in cms_name[cms]:
                # 为root节点设置子结点
                child1 = QTreeWidgetItem(root)
                child1.setText(0, poc)
                child1.setCheckState(0, Qt.Unchecked)
        self.Ui.treeWidget_Plugins.itemChanged.connect(self.handleChanged)
        self.Ui.treeWidget_Plugins.doubleClicked.connect(self.Show_Plugins_info)
        self.Ui.textEdit_log.append(
            "[%s]Success:插件加载完成，共%s个。" % (time.strftime('%H:%M:%S', time.localtime(time.time())), len(values)))
    def Show_Plugins_info(self):
        methods_name = self.Ui.treeWidget_Plugins.currentItem().text(0)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # 列出所有数据
        sql = "SELECT *  from POC where pocmethods='%s'"%methods_name
        cursor.execute(sql)
        values = cursor.fetchall()
        # print(values)
        try:
            self.dialog.close()
        except:
            pass
        if len(values) !=0:
            self.WChild_info = Ui_Plugins_information()
            self.dialog = QtWidgets.QDialog(self)
            self.WChild_info.setupUi(self.dialog)
            self.dialog.show()
            self.WChild_info.vuln_name.setText(values[0][3])
            self.WChild_info.cms_name.setText(values[0][1])
            self.WChild_info.plugins_methods.setText(values[0][6])
            self.WChild_info.file_path.setText("Plugins/"+values[0][1]+'/'+values[0][2])
            self.WChild_info.vuln_url.setText('<a href="'+values[0][4]+'">'+values[0][4]+'</a>')
            self.WChild_info.vuln_miaoshu.setText(values[0][5])
            return 0
        else:
            return
    # 父节点关联子节点
    def handleChanged(self, item, column):
        count = item.childCount()
        # print dir(item)
        if item.checkState(column) == Qt.Checked:
            # print "checked", item, item.text(column)
            for f in range(count):
                item.child(f).setCheckState(0, Qt.Checked)
        if item.checkState(column) == Qt.Unchecked:
            # print "unchecked", item, item.text(column)
            for f in range(count):
                item.child(f).setCheckState(0, Qt.Unchecked)
        #  self.Ui.treeWidget_Plugins.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 设置item可以多选
        # self.tree.itemChanged.connect(self.handleChanged)
        # self.Ui.treeWidget_Plugins.addTopLevelItem(root)

    # 导入文件列表
    def vuln_import_file(self):
        self.url_list = []
        filename = self.file_open(r"Text Files (*.txt);;All files(*.*)")
        if os.path.isfile(filename):
            self.Ui.textEdit_log.append(
                "[%s]Info:正在从文件中读取URL..." % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
            f = open(filename, 'r', encoding='utf-8')
            for line in f.readlines():
                if 'http' in line:
                    line = line.replace('\n', '').strip()
                    self.url_list.append(line)
            self.Ui.textEdit_log.append(
                "[%s]Info:读取完成，共加载%s条。" % (
                (time.strftime('%H:%M:%S', time.localtime(time.time()))), len(self.url_list)))
        self.Ui.lineEdit_vuln_url.setText(filename)

    # 导出扫描结果
    def vuln_export_file(self):
        data = []
        comdata = []
        for i in range(0, self.Ui.tableWidget_vuln.rowCount()):  # 循环行
            for j in range(0, self.Ui.tableWidget_vuln.columnCount()):  # 循环列
                if self.Ui.tableWidget_vuln.item(i, j) != None:  # 有数据
                    data.append(self.Ui.tableWidget_vuln.item(i, j).text())  # 空格分隔
            comdata.append(list(data))
            data = []
        if len(comdata) > 0:
            path = (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '.csv').replace(' ', '-').replace('-','').replace(
                ':', '')
            # print(path)
            file_name = self.file_save(path)
            if file_name != "":
                with open(file_name, 'w', newline='') as f:
                    writer = csv.writer(f)
                    for row in comdata:
                        writer.writerow(row)
                f.close()
                box = QtWidgets.QMessageBox()
                box.information(self, "Success", "导出成功！\n文件位置："+file_name)
            else:
                box2= QtWidgets.QMessageBox()
                box2.warning(self, "Error", "保存失败！文件名错误！" )
        else:
            self.Ui.textEdit_log.append(
                "[%s]Faile:没有扫描结果！" % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
    # 显示插件
    def vuln_ShowPlugins(self):
        self.widget = Ui_Form()
        self.dialog = QtWidgets.QDialog(self)
        self.widget.setupUi(self.dialog)
        self.dialog.setFixedSize(self.dialog.width(), self.dialog.height())  # 设置宽高不可变
        # 设置查看插件表格属性  列宽度
        self.widget.show_Plugins.setColumnWidth(0, 100)
        self.widget.show_Plugins.setColumnWidth(1, 350)
        self.widget.show_Plugins.setColumnWidth(2, 350)
        self.widget.show_Plugins.setColumnWidth(3, 383)
        self.widget.show_Plugins.setColumnWidth(4, 218)
        conn2 = sqlite3.connect(DB_NAME)
        # 创建一个游标 curson
        cursor = conn2.cursor()
        # self.Ui.textEdit_log.append("[%s]Info:正在查询数据..."%(time.strftime('%H:%M:%S', time.localtime(time.time()))))
        # 列出所有数据
        sql = "SELECT * from POC"
        cursor.execute(sql)
        values = cursor.fetchall()
        # self.Ui.textEdit_log.append("[%s]Success:数据查询成功！"%(time.strftime('%H:%M:%S', time.localtime(time.time()))))
        i = 0
        self.widget.show_Plugins.setRowCount(len(values))
        sql2 = "SELECT distinct cmsname from POC"
        cursor.execute(sql2)
        cms_name_data = cursor.fetchall()
        # 添加查询列表
        for cms_name in cms_name_data:
            self.widget.show_Plugins_comboBox.addItem(cms_name[0])
            # print(cms_name[0])
        for single in values:
            vuln_name = QTableWidgetItem(str(single[1]))
            vuln_url = QTableWidgetItem(str(single[3]))
            vuln_payload = QTableWidgetItem(str(single[4]))
            vuln_result = QTableWidgetItem(str(single[5]))
            vuln_motheds = QTableWidgetItem(str(single[2]))
            self.widget.show_Plugins.setItem(i, 0, vuln_name)
            self.widget.show_Plugins.setItem(i, 1, vuln_url)
            self.widget.show_Plugins.setItem(i, 2, vuln_payload)
            self.widget.show_Plugins.setItem(i, 3, vuln_result)
            self.widget.show_Plugins.setItem(i, 4, vuln_motheds)
            i = i + 1
        conn2.close()
        self.dialog.show()
        self.widget.show_Plugins_comboBox.currentIndexChanged.connect(self.show_plugins_go)  # comboBox事件选中触发刷新
    # 单击列表刷新显示控件
    def show_plugins_go(self):
        self.widget.show_Plugins.clearContents()
        conn2 = sqlite3.connect(DB_NAME)
        # 创建一个游标 curson
        cursor = conn2.cursor()
        cms_name = self.widget.show_Plugins_comboBox.currentText()  # 获取文本
        if cms_name == "ALL":
            sql = "SELECT * from POC "
        else:
            sql = "SELECT * from POC where cmsname = '%s'" % cms_name
        cursor.execute(sql)
        cms_data = cursor.fetchall()
        i = 0
        self.widget.show_Plugins.setRowCount(len(cms_data))
        for single in cms_data:
            vuln_name = QTableWidgetItem(str(single[1]))
            vuln_url = QTableWidgetItem(str(single[3]))
            vuln_payload = QTableWidgetItem(str(single[4]))
            vuln_result = QTableWidgetItem(str(single[5]))
            vuln_motheds = QTableWidgetItem(str(single[2]))
            self.widget.show_Plugins.setItem(i, 0, vuln_name)
            self.widget.show_Plugins.setItem(i, 1, vuln_url)
            self.widget.show_Plugins.setItem(i, 2, vuln_payload)
            self.widget.show_Plugins.setItem(i, 3, vuln_result)
            self.widget.show_Plugins.setItem(i, 4, vuln_motheds)
            i = i + 1
        conn2.close()
    # 重新加载插件
    def vuln_reload_Plugins(self):
        self.Ui.treeWidget_Plugins.clear()
        self.Ui.textEdit_log.setText("[%s]Start:正在重新加载插件..." % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
        # 删除数据库，重新建立
        if os.path.isfile(DB_NAME):
            try:
                # print(DB_NAME)
                os.remove(DB_NAME)
            except Exception as e:
                self.Ui.textEdit_log.append("[%s]Error:数据库文件删除失败！\n[Exception]:\n%s" % (
                    (time.strftime('%H:%M:%S', time.localtime(time.time()))), e))
                return 0
            self.Ui.textEdit_log.append(
                "[%s]Success:删除数据库完成！" % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
        else:
            self.Ui.textEdit_log.append(
                "[%s]Success:数据库文件不存在，尝试创建数据库！" % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
        try:
            # 连接数据库。如果数据库不存在的话，将会自动创建一个 数据库
            conn = sqlite3.connect(DB_NAME)
            # 创建一个游标 curson
            cursor = conn.cursor()
            # 执行一条语句,创建 user表 如不存在创建
            sql = "create table IF NOT EXISTS POC (id integer primary key autoincrement , cmsname varchar(30),pocfilename varchar(40),pocname  varchar(30),pocreferer varchar(50),pocdescription varchar(200),pocmethods  varchar(40))"
            cursor.execute(sql)
            self.Ui.textEdit_log.append(
                "[%s]Success:创建数据库完成！" % (time.strftime('%H:%M:%S', time.localtime(time.time()))))
        except Exception as e:
            self.Ui.textEdit_log.append(
                "[%s]Error:数据框创建失败！\n[Exception]:\n%s" % (time.strftime('%H:%M:%S', time.localtime(time.time())), e))
            return 0
        try:
            cms_path = "Plugins"
            cms_path = cms_path.replace("\\", "/")
            for cms_name in os.listdir(cms_path):  # 遍历目录名
                poc_path = os.path.join(cms_path, cms_name).replace("\\", "/")
                for path, dirs, poc_methos_list in os.walk(poc_path):  # 遍历poc文件，得到方法名称
                    # print(path,dirs,poc_methos_list)
                    for poc_file_name in poc_methos_list:
                        # self.Ui.textEdit_log.append(poc_file_name[-3:])
                        # self.Ui.textEdit_log.append(poc_file_name)
                        poc_name_path = cms_path + "\\" + cms_name + "\\" + poc_file_name
                        poc_name_path = poc_name_path.replace("\\", "/")
                        # print(poc_name_path)
                        # 判断是py文件在打开  文件存在
                        if os.path.isfile(poc_name_path) and poc_file_name.endswith('.py'):
                            # 判断py文件不包含.
                            # print(poc_name_path)
                            if '.' not in poc_file_name.replace(".py", ""):
                                # print(poc_name_path)
                                f = open(poc_name_path, "r", encoding="utf-8")
                                # 获取poc的中文名称
                                # printSkyBlue(cms_name)
                                poc_methos = ""  # 定义局部变量 存放poc方法
                                poc_name = ""  # 定义局部变量 存放poc名称
                                poc_referer = ""
                                if cms_name[0:2] != "__":  # 判断文件夹的前两位不是下划线
                                    for name in f.readlines():
                                        # print(name)
                                        # 得到中文poc_name
                                        if "name:" in name:
                                            poc_name = name.replace("name:", "").replace("\n", "").replace(
                                                "\r", "").replace("\r\n", "").strip()
                                            # print(poc_name)
                                        # 得到调用的poc_methos
                                            # self.Ui.textEdit_log.append(poc_methos)
                                        # 得到调用的poc_referer
                                        if "referer" in name:
                                            poc_referer = name.replace("referer:", "").replace("\n", "").replace(
                                                "\r", "").replace("\r\n", "").strip()
                                            # self.Ui.textEdit_log.append(poc_referer)
                                    # print(poc_referer)
                                    # 读取文件光标恢复到初始位置
                                    f.seek(0)
                                    condata = f.read()  ##所有数据
                                    # print(condata)
                                    # 匹配描述
                                    comment = re.compile(r"description:(.*?)'''", re.DOTALL)
                                    poc_description = str(comment.findall(condata)[0]).replace("\"", "").replace(" ",
                                                                                                                               "")
                                    if poc_name != "" :
                                        poc_methos = poc_file_name[:-3]
                                        # print(poc_methos)
                                        # 将数据插入到表中
                                        cursor.execute(
                                            'insert into POC (cmsname, pocname,pocfilename,pocreferer,pocdescription,pocmethods) values ("%s","%s","%s","%s","%s","%s")' % (
                                                cms_name, poc_name, poc_file_name, poc_referer, poc_description,
                                                poc_methos))
                                f.close()
                            else:
                                self.Ui.textEdit_log.append("[%s]Error:%s文件加载失败，文件名中不允许包含英文符号点！" % (
                                    (time.strftime('%H:%M:%S', time.localtime(time.time())))(
                                        cms_name + "/" + poc_file_name)))
                                return 0
                        else:
                            pass
            conn.commit()  # 提交
            result = cursor.fetchall()
            if not len(result):
                cursor.execute("select count(*) from POC")
                values = cursor.fetchall()
                self.Ui.textEdit_log.append(
                    "[%s]Success:共写入%s个插件" % ((time.strftime('%H:%M:%S', time.localtime(time.time()))), values[0][0]))
                self.loadplugins()  # 调用加载插件
            else:
                self.Ui.textEdit_log.append(
                    "[%s]Error:数据更新失败，原因:" % (time.strftime('%H:%M:%S', time.localtime(time.time()))), str(result))
                return 0
            conn.close()
            box = QtWidgets.QMessageBox()
            box.information(self, "Load Plugins", "数据更新完成！\n插件数量：%s" % values[0][0])
            # reboot = sys.executable
            # os.execl(reboot, reboot, *sys.argv)
        except Exception as e:
            self.Ui.textEdit_log.append(
                "[%s]Error:数据写入失败！\n[Exception]:\n%s" % ((time.strftime('%H:%M:%S', time.localtime(time.time()))), e))
            return 0
    def show_others(self,q):
        if q.text() =="关于":
            self.about()
            return
        if q.text() =="更新":
            self.version_update()
            return
        if q.text() =="意见反馈":
            self.ideas()
            return
        else:
            try:
                with open("QSS/" + json_qss[q.text()], 'r', encoding='utf-8') as f:
                    qss_style = f.read()
                    f.close()
                MainWindows.setStyleSheet(self, qss_style)
                f = open('QSS/Setup.txt', 'w', encoding='utf-8')
                f.write('{"QSS": "%s"}'%json_qss[q.text()])
                f.close()
                python = sys.executable
                os.execl(python, python, *sys.argv)
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))
                pass
    # 关于
    def about(self):
        box = QtWidgets.QMessageBox()
        box.setIcon(1)
        box.about(self, "About",
                  "\t\t\tAbout\n       此程序为一款CMS扫描工具，可自行选择扫描的插件进行漏洞检查，请勿非法使用！\n\t\t\t   Powered by qianxiao996")
    # 更新
    def version_update(self):
        webbrowser.open("https://github.com/qianxiao996/FrameScan-GUI/releases")

    # 意见反馈
    def ideas(self):
        box = QtWidgets.QMessageBox()
        box.setIcon(1)
        box.about(self, "意见反馈", "作者邮箱：qianxiao996@126.com\n作者主页：http://blog.qianxiao996.cn")

    # 全选
    def vuln_all(self):
        item = QtWidgets.QTreeWidgetItemIterator(self.Ui.treeWidget_Plugins)
        # 该类的value()即为QTreeWidgetItem
        while item.value():
            if item.value().checkState(0) != QtCore.Qt.Checked:
                item.value().setCheckState(0, Qt.Checked)
            item = item.__iadd__(1)
    # 反选
    def vuln_noall(self):
        item = QtWidgets.QTreeWidgetItemIterator(self.Ui.treeWidget_Plugins)
        # 该类的value()即为QTreeWidgetItem
        while item.value():
            if item.value().checkState(0) == QtCore.Qt.Checked:
                item.value().setCheckState(0, Qt.Unchecked)
            item = item.__iadd__(1)
    # 文件打开对话框
    def file_open(self, type):
        fileName, selectedFilter = QFileDialog.getOpenFileName(self, (r"上传文件"),'', type)
        return (fileName)  # 返回文件路径
    # 保存文件对话框
    def file_save(self, filename):
        fileName, filetype = QFileDialog.getSaveFileName(self, (r"保存文件"), (filename),r"All files(*.*)")
        return fileName
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindows()
    window.show()
    try:
        response = requests.get("https://qianxiao996.cn/FrameScan-GUI/version.txt",timeout = 2)
        if (int(response.text.replace('.',''))>int(version.replace('.',''))):
            reply = QMessageBox.question(window,'软件更新', "检测到软件已发布新版本，是否前去下载?",QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                webbrowser.open('https://github.com/qianxiao996/FrameScan-GUI/releases')
            else:
                pass
    except:
        pass
    sys.exit(app.exec_())
