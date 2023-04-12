from Ui_无人机登录界面i import *
from Ui_无人机二级界面_改 import *
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QButtonGroup,QPushButton
from PyQt5.QtCore import Qt
from pre_run import *

import sys
import json
from multiprocessing import Process,Manager

#------------带添加，根据state读取不同lineedit中的内容，实现不同账号登录
#sh文件改进，判断哪些pyton文件结束并修改json文件内容
#在登录后，根据不同的登录角色更新json内容，value为0表示leader,1表示簇头，2表示普通无人机
#InterfaceWindow中的choose_name一定是无人机原本的名字，并不是按钮名称，在左侧按钮点击响应函数中已经将按钮名称转换为无人机名称
#debug 记录，将1035行ele改为self.job_2_name(ele_inner),4.10-12:42

path_json_online='temporary_save'
path_json_communicate='communication'
path_json_verify='verify'

def get_dic_from_json(path)->dict:#从json加载字典
    with open(path,'r') as file:
        tmp=json.load(file)
        print(tmp)
        return tmp

def save_dic_to_json(path,dic):
    with open(path,'w+') as file:
        json.dump(dic,file)

class program:
    ip='192.168.1.1'
    port='8888'
    controller=False
    def __init__(self,name):
        self.app = QApplication(sys.argv)
        self.win = LoginWindow(name)
        self.name=name
        sys.exit(self.app.exec_())

    
    # def refesh_list():#获得在线名单,具体方法在InterfaceWindow类中的get_list()中实现
        # self.list=


class LoginWindow(QMainWindow):
    def __init__(self,name):
        super().__init__()
        self.ui = Ui_MainWindow_1()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.pushButton.clicked['bool'].connect(lambda:self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_2.clicked['bool'].connect(lambda:self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.pushButton_5.clicked['bool'].connect(lambda:self.go_to_inter(2))
        self.ui.pushButton_7.clicked['bool'].connect(lambda:self.go_to_inter(0))
        self.ui.label.setText(name)
        self.name=name
        self.show()

    def go_to_inter(self,state):#state==0表示控制器登录，==1无人机登录
        if state==2:
            input_ip=self.ui.lineEdit.text()
            input_port=self.ui.lineEdit_2.text()
        else:
            input_ip=self.ui.lineEdit_5.text()
            input_port=self.ui.lineEdit_6.text()
        if(self.decide_legal(input_ip,input_port,state)):
            dic=get_dic_from_json(path_json_online)
            print(type(dic))
            dic_2=get_dic_from_json(path_json_verify)
            dic_2[self.name]=0#0未经验证，1经过验证
            save_dic_to_json(path_json_verify,dic_2) 
            print("verify_dic:",dic_2)

            if state==2:#自身是无人机
                print("self.name=",self.name)
                if len([k for k,v in dic.items() if v ==0])==1:
                    print("无人机登录")
                    dic[self.name]=2
                    save_dic_to_json(path_json_online,dic)
                    self.win=InterfaceWindow(self.name,state)
                    self.close()
                else:
                    msg_box=QMessageBox(QMessageBox.Warning,'警告','未发现控制器')
                    msg_box.exec_()
            
            else:#控制器登录
                print("控制器登录","self.name",self.name)
                dic[self.name]=0
                save_dic_to_json(path_json_online,dic)
                self.win=InterfaceWindow(self.name,state)
                self.close()

            print(dic)
        else:
            msg_box=QMessageBox(QMessageBox.Warning,'警告','密码或端口不匹配!')
            # msg_box.show()
            msg_box.exec_()

    def decide_legal(self,input_ip,input_port,state)->bool:#函数功能要求：判断ip和端口是否合法，合法返回True,账号以此作为登录许可凭证,state=0为无人机登录，为1为控制器登录
        print(input_ip)
        print(input_port)
        print(input_ip==program.ip)
        if input_ip==program.ip and input_port==program.port:
            return True
        else:
            return False
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, mouse_event):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(mouse_event.globalPos() - self.m_Position)  # 更改窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

class InterfaceWindow(QMainWindow):
    def __init__(self,name,state) -> None:
        super().__init__()
        self.ui = Ui_MainWindow_2()
        self.ui.setupUi(self)

        self.name=name#登录设备名称
        self.comu_name=None#选择左侧按钮的名称
        self.state=state#表明登录身份
        self.lst=[]#在线列表
        # self.leader_idx=-1

        self.button_lst=[]#为了更方便的遍历按钮,位于界面左侧的所有按钮
        self.weight_lst=[]
        self.textbrowser_lst=[]
        self.textedit_lst=[]
        self.button_send_lst=[]
        self.button_multi_func_lst=[]
        if self.state==0:
            self.controller_verify_lst=[]
            self.btg_controller_verify= QButtonGroup(self.ui.frame_2)
        self.weight_inner_tmp=None
        self.communicate_log={}
        self.verify_leader_display=False
        self.sub_label=False#表明右方列表名称为消息显示列表，True表示为认证信息显示列表
        # self.ui.frame_2.setVisible(False)
        
        # if state==0:
        #     self.ui.label.setText('控制器')
        # else:
        #     self.ui.label.setText(self.name)


        self.get_list()
        num_button=len(self.lst)#在线设备个数

        self.btg = QButtonGroup(self.ui.verticalLayout_2)#按钮集合
        self.btg_send = QButtonGroup(self.ui.frame_2)
        self.btg_multi_func=QButtonGroup(self.ui.frame_2)
        # self.btg_multi_func.
        # print('stackweight 页面数：',self.ui.stackedWidget.count())

#----------------------------------------------------------------添加Weight并设置stackweight前两页不可见
        weight_first= self.ui.stackedWidget.widget(0)
        weight_first.setVisible(False)
        self.weight_inner_tmp=QtWidgets.QFrame()
        self.weight_lst.append(self.weight_inner_tmp)
        self.weight_lst[0].setVisible(False)
#----------------------------------------------------------------

        self.ui.stackedWidget.addWidget(self.weight_lst[0])

        # controller_need_to_add=False#为True则控制器按钮需要添加
        # print('stackweight 页面数：',self.ui.stackedWidget.count())

        # cnt_inner=0#communicate函数传参，决定哪个按钮按下
        # self.refresh_button_left()

        self.dic=get_dic_from_json(path_json_online)#在program中写入过，但是为了最新的在线结果，进行dic的更新
        self.dic_verify=get_dic_from_json(path_json_verify)

        self.state=self.dic[self.name]
        print("start_dic:",self.dic)
        print("self.name",self.name)
        print("self.state",self.state)


        #-----------------------------设置界面顶端标签
        self.ui.label.setText(self.value_2_job(self.name))#因为传入dic所以该函数内，对于keys()的keyerror处理的函数对该调用没有影响
        #-----------------------------
        print("self.dic.keys():",self.dic.keys())

        self.i=0#用于创建左边部分按钮
        
        if self.state!=1:#不为簇头，删除frame_14
            self.ui.frame_14.setVisible(False)

        for ele in list(self.dic.keys()):
            # print("第",i,"个按钮")
            self.weight_inner_tmp=None
            # self.weight_lst[i+1]=None
            # prisnt("i:",i,"ele:",ele) 
            if self.dic[ele]==0:
                print("in here!")
                if self.state==0:#非控制器都显示
                    continue
                print("in here!")
                pushbutton_tmp=QtWidgets.QPushButton(self.value_2_job(ele),self.ui.frame_17)
                if self.dic_verify[ele]==1:
                    pushbutton_tmp.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n")
                self.ui.verticalLayout_2.addWidget(pushbutton_tmp)
                self.weight_inner_tmp=QtWidgets.QFrame()#等效page
                verticalLayout_1 = QtWidgets.QVBoxLayout(self.weight_inner_tmp)
                verticalLayout_1.setObjectName("verticalLayout_1"+str(self.i+1))
                # frame_inner=QtWidgets.QFrame(self.weight_inner_tmp)
                # frame_inner.setObjectName("frame_inner_1"+str(i+1))
                # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                # sizePolicy.setHorizontalStretch(0)
                # sizePolicy.setVerticalStretch(1)
                # sizePolicy.setHeightForWidth(frame_inner.sizePolicy().hasHeightForWidth())
                frame_inner_2=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(frame_inner_2.sizePolicy().hasHeightForWidth())
                frame_inner_2.setSizePolicy(sizePolicy)
                frame_inner_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_2.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_2.setObjectName("frame_inner_2_"+str(self.i+1))
                horizontalLayout= QtWidgets.QHBoxLayout(frame_inner_2)
                horizontalLayout.setObjectName("horizontalLayout_"+str(self.i+1))
                label_inner = QtWidgets.QLabel(frame_inner_2)#frame_inner_2(parent:weight_iinner_tmp)中添加label
                label_inner.setAlignment(QtCore.Qt.AlignCenter)
                label_inner.setObjectName("label_inner_"+str(self.i+1))
                horizontalLayout.addWidget(label_inner)
                verticalLayout_1.addWidget(frame_inner_2)
                print(2)
                frame_inner_3=QtWidgets.QFrame(self.weight_inner_tmp)#frame_inner_3(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(5)
                sizePolicy.setHeightForWidth(frame_inner_3.sizePolicy().hasHeightForWidth())
                frame_inner_3.setSizePolicy(sizePolicy)
                frame_inner_3.setStyleSheet("border-radius:30px;\n""background-color: rgb(156, 216, 191);")
                frame_inner_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_3.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_3.setObjectName("frame_inner_3_"+str(self.i+1))
                horizontalLayout_2=QtWidgets.QHBoxLayout(frame_inner_3)
                horizontalLayout_2.setObjectName("horizontalLayout_2_"+str(self.i+1))
                print(3)
                frame_inner_5=QtWidgets.QFrame(frame_inner_3)#frame_inner_5(parent:frame_inner_3)位于父窗口左边，用于承载textbrowser,见Line-228
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(2)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_5.sizePolicy().hasHeightForWidth())
                frame_inner_5.setSizePolicy(sizePolicy)
                frame_inner_5.setStyleSheet("border-radius:30px;")
                frame_inner_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_5.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_5.setObjectName("frame_inner_5_"+str(self.i+1))

                horizontalLayout_3=QtWidgets.QHBoxLayout(frame_inner_5)
                horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
                horizontalLayout_3.setObjectName("horizontalLayout_3_"+str(self.i+1))
                textbrowser=QtWidgets.QTextBrowser(frame_inner_5)
                textbrowser.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textbrowser.setObjectName("textBrowser_"+str(self.i+1))
                horizontalLayout_3.addWidget(textbrowser)
                horizontalLayout_2.addWidget(frame_inner_5)

                frame_inner_6=QtWidgets.QFrame(frame_inner_3)#frame_inner_6(parent:frame_inner_3),位于父窗口的右侧用于承载顶端Label,textedit和发送按钮，有可能承载认证按钮
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(1)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_6.sizePolicy().hasHeightForWidth())
                frame_inner_6.setSizePolicy(sizePolicy)
                frame_inner_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_6.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_6.setObjectName("frame_inner_6_"+str(self.i+1))
                
                verticalLayout_2=QtWidgets.QVBoxLayout(frame_inner_6)
                verticalLayout_2.setObjectName("verticalLayout_2_"+str(self.i+1))
                label_inner_2=QtWidgets.QLabel(frame_inner_6)
                label_inner_2.setAlignment(QtCore.Qt.AlignCenter)
                label_inner_2.setObjectName("label_inner_2_"+str(self.i+1))
                label_inner_2.setText("消息发送栏")
                textEdit=QtWidgets.QTextEdit(frame_inner_6)
                textEdit.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textEdit.setObjectName("textEdit")
                verticalLayout_2.addWidget(label_inner_2)
                verticalLayout_2.addWidget(textEdit)

                pushButton_inner = QtWidgets.QPushButton(frame_inner_6)
                pushButton_inner.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                pushButton_inner.setObjectName("pushButton_inner_"+str(self.i+1))


                pushButton_inner_2=None

                if self.state==2:#非簇头情况下添加pushbutton_inner_2,在此情况下为认证功能
                    pushButton_inner_2 =  QtWidgets.QPushButton(frame_inner_6)
                    pushButton_inner_2.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                    pushButton_inner_2.setObjectName("pushButton_inner_2"+str(self.i+1))
                    pushButton_inner_2.setText("认证") 
                    verticalLayout_2.addWidget(pushButton_inner_2)
                    pushButton_inner_2.setCheckable(True)
                    pushButton_inner_2.setChecked(False)
                    # self.button_multi_func_lst.append(pushButton_inner_2)
                    # print("len(self.button_multi):",len(self.button_multi_func_lst))
                    
                verticalLayout_2.addWidget(pushButton_inner)
                horizontalLayout_2.addWidget(frame_inner_6)

                verticalLayout_1.addWidget(frame_inner_3)

                frame_inner_4=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(3)
                sizePolicy.setHeightForWidth(frame_inner_4.sizePolicy().hasHeightForWidth())
                frame_inner_4.setSizePolicy(sizePolicy)
                frame_inner_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_4.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_4.setObjectName("frame_inner_4_"+str(self.i+1))
                verticalLayout_1.addWidget(frame_inner_4)
                
                print(4)

                label_inner.setText("当前对象信息发送列表_"+str(self.i+1))
                pushButton_inner.setText("发送")
                print(8)

                self.weight_lst.append(self.weight_inner_tmp)
                self.textbrowser_lst.append(textbrowser)
                self.textedit_lst.append(textEdit)
                pushButton_inner.setCheckable(True)
                pushButton_inner.setChecked(False)
                self.button_send_lst.append(pushButton_inner)
                self.button_multi_func_lst.append(pushButton_inner_2)
                print(9)
                self.btg_send.addButton(pushButton_inner)
                print(10)
                if self.state!=1:
                    self.btg_multi_func.addButton(pushButton_inner_2)
                print(11)
                # print("i=")
                self.ui.stackedWidget.addWidget(self.weight_lst[self.i+1])
                
                print('stackweight 页面数：',self.ui.stackedWidget.count())

                
                self.i+=1
                # pushButton_inner.clicked['bool'].connect(lambda:self.communicate(cnt_inner))
                # print("cnt_inner=",cnt_inner)
                # cnt_inner+=1
                # self.weight_lst[i+1]

                # controller_need_to_add=True

            else:#self.dic.keys()一定是真名，所以使用self.value_2_job转换为job
                if ele==self.name:
                    continue
                pushbutton_tmp=QtWidgets.QPushButton(self.value_2_job(ele),self.ui.frame_17)
                print("verify:",self.dic_verify)
                if self.dic_verify[ele]==1:
                    pushbutton_tmp.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n")
                self.ui.verticalLayout_2.addWidget(pushbutton_tmp)
                
                self.weight_inner_tmp=QtWidgets.QFrame()#等效page
                verticalLayout_1 = QtWidgets.QVBoxLayout(self.weight_inner_tmp)
                verticalLayout_1.setObjectName("verticalLayout_1"+str(self.i+1))
                # frame_inner=QtWidgets.QFrame(self.weight_inner_tmp)
                # frame_inner.setObjectName("frame_inner_1"+str(i+1))
                # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                # sizePolicy.setHorizontalStretch(0)
                # sizePolicy.setVerticalStretch(1)
                # sizePolicy.setHeightForWidth(frame_inner.sizePolicy().hasHeightForWidth())
                frame_inner_2=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(frame_inner_2.sizePolicy().hasHeightForWidth())
                frame_inner_2.setSizePolicy(sizePolicy)
                frame_inner_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_2.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_2.setObjectName("frame_inner_2_"+str(self.i+1))
                horizontalLayout= QtWidgets.QHBoxLayout(frame_inner_2)
                horizontalLayout.setObjectName("horizontalLayout_"+str(self.i+1))
                label_inner = QtWidgets.QLabel(frame_inner_2)#frame_inner_2(parent:weight_iinner_tmp)中添加label
                label_inner.setAlignment(QtCore.Qt.AlignCenter)
                label_inner.setObjectName("label_inner_"+str(self.i+1))
                horizontalLayout.addWidget(label_inner)
                verticalLayout_1.addWidget(frame_inner_2)
                print(2)
                frame_inner_3=QtWidgets.QFrame(self.weight_inner_tmp)#frame_inner_3(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(5)
                sizePolicy.setHeightForWidth(frame_inner_3.sizePolicy().hasHeightForWidth())
                frame_inner_3.setSizePolicy(sizePolicy)
                frame_inner_3.setStyleSheet("border-radius:30px;\n""background-color: rgb(156, 216, 191);")
                frame_inner_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_3.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_3.setObjectName("frame_inner_3_"+str(self.i+1))
                horizontalLayout_2=QtWidgets.QHBoxLayout(frame_inner_3)
                horizontalLayout_2.setObjectName("horizontalLayout_2_"+str(self.i+1))
                print(3)
                frame_inner_5=QtWidgets.QFrame(frame_inner_3)#frame_inner_5(parent:frame_inner_3)位于父窗口左边，用于承载textbrowser,见Line-228
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(2)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_5.sizePolicy().hasHeightForWidth())
                frame_inner_5.setSizePolicy(sizePolicy)
                frame_inner_5.setStyleSheet("border-radius:30px;")
                frame_inner_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_5.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_5.setObjectName("frame_inner_5_"+str(self.i+1))

                horizontalLayout_3=QtWidgets.QHBoxLayout(frame_inner_5)
                horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
                horizontalLayout_3.setObjectName("horizontalLayout_3_"+str(self.i+1))
                textbrowser=QtWidgets.QTextBrowser(frame_inner_5)
                textbrowser.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textbrowser.setObjectName("textBrowser_"+str(self.i+1))
                horizontalLayout_3.addWidget(textbrowser)
                horizontalLayout_2.addWidget(frame_inner_5)

                frame_inner_6=QtWidgets.QFrame(frame_inner_3)#frame_inner_6(parent:frame_inner_3),位于父窗口的右侧用于承载顶端Label,textedit和发送按钮，有可能承载认证按钮
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(1)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_6.sizePolicy().hasHeightForWidth())
                frame_inner_6.setSizePolicy(sizePolicy)
                frame_inner_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_6.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_6.setObjectName("frame_inner_6_"+str(self.i+1))
                
                verticalLayout_2=QtWidgets.QVBoxLayout(frame_inner_6)
                verticalLayout_2.setObjectName("verticalLayout_2_"+str(self.i+1))
                label_inner_2=QtWidgets.QLabel(frame_inner_6)
                label_inner_2.setAlignment(QtCore.Qt.AlignCenter)
                label_inner_2.setObjectName("label_inner_2_"+str(self.i+1))
                label_inner_2.setText("消息发送栏")
                textEdit=QtWidgets.QTextEdit(frame_inner_6)
                textEdit.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textEdit.setObjectName("textEdit")
                verticalLayout_2.addWidget(label_inner_2)
                verticalLayout_2.addWidget(textEdit)

                pushButton_inner = QtWidgets.QPushButton(frame_inner_6)
                pushButton_inner.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                pushButton_inner.setObjectName("pushButton_inner_"+str(self.i+1))


                pushButton_inner_2=None
                pushButton_inner_3=None
                if self.state!=1:#非簇头情况下添加pushbutton_inner_2,该按钮有两种功能，控制器为选择簇头，
                    pushButton_inner_2 =  QtWidgets.QPushButton(frame_inner_6)
                    pushButton_inner_2.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                    pushButton_inner_2.setObjectName("pushButton_inner_2"+str(self.i+1))
                    if self.state==2:
                        pushButton_inner_2.setText("认证") 
                    else:
                        pushButton_inner_2.setText("选择为簇头") 
                    verticalLayout_2.addWidget(pushButton_inner_2)
                    pushButton_inner_2.setCheckable(True)
                    pushButton_inner_2.setChecked(False)
                    if self.state==0:#自身为控制器，添加与簇头之间的认证按钮，控制器与所有无人机都有一认证按钮，但同时只能有一个可见
                        pushButton_inner_3= QtWidgets.QPushButton(frame_inner_6)
                        pushButton_inner_3.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                        pushButton_inner_3.setObjectName("pushButton_inner_3"+str(self.i+1))
                        pushButton_inner_3.setText("与簇头认证")
                        pushButton_inner_3.setCheckable(True)
                        pushButton_inner_3.setChecked(False)
                        verticalLayout_2.addWidget(pushButton_inner_3)
                        pushButton_inner_3.setVisible(False)
                        self.controller_verify_lst.append(pushButton_inner_3)                    # self.button_multi_func_lst.append(pushButton_inner_2)
                        self.btg_controller_verify.addButton(pushButton_inner_3)
                    # print("len(self.button_multi):",len(self.button_multi_func_lst))
                    
                verticalLayout_2.addWidget(pushButton_inner)
                horizontalLayout_2.addWidget(frame_inner_6)

                verticalLayout_1.addWidget(frame_inner_3)

                frame_inner_4=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(3)
                sizePolicy.setHeightForWidth(frame_inner_4.sizePolicy().hasHeightForWidth())
                frame_inner_4.setSizePolicy(sizePolicy)
                frame_inner_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_4.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_4.setObjectName("frame_inner_4_"+str(self.i+1))
                verticalLayout_1.addWidget(frame_inner_4)
                
                print(4)
                

                label_inner.setText("当前对象信息发送列表_"+str(self.i+1))
                pushButton_inner.setText("发送")
                print(8)

                self.weight_lst.append(self.weight_inner_tmp)
                self.textbrowser_lst.append(textbrowser)
                self.textedit_lst.append(textEdit)
                pushButton_inner.setCheckable(True)
                pushButton_inner.setChecked(False)
                self.button_send_lst.append(pushButton_inner)
                self.button_multi_func_lst.append(pushButton_inner_2)
                print(9)
                self.btg_send.addButton(pushButton_inner)
                print(10)
                if self.state!=1:
                    self.btg_multi_func.addButton(pushButton_inner_2)
                print(11)
                print("i=")
                self.ui.stackedWidget.addWidget(self.weight_lst[self.i+1])
                
                print('stackweight 页面数：',self.ui.stackedWidget.count())

                self.i+=1
                # pushButton_inner.clicked['bool'].connect(lambda:self.communicate(cnt_inner))
                # print("cnt_inner=",cnt_inner)
                # cnt_inner+=1
                # self.weight_lst[i+1]

            pushbutton_tmp.setFixedHeight(24)
            # self.ui.frame_17.addWidget(pushbutton_tmp)

            self.btg.addButton(pushbutton_tmp)
            self.button_lst.append(pushbutton_tmp)

            pushbutton_tmp.setCheckable(True)
            pushbutton_tmp.setChecked(False)
        self.btg.setExclusive(True)
        self.btg_send.setExclusive(True)
        self.btg_multi_func.setExclusive(True)
        self.btg.buttonClicked.connect(lambda:self.choose_comu_obj())
        self.btg_send.buttonClicked.connect(lambda:self.communicate())
        self.btg_multi_func.buttonClicked.connect(lambda:self.multi_func())
        if self.state==0:
            self.btg_controller_verify.buttonClicked.connect(lambda:self.verify(1))#不论有无内容均添加响应函数，为了refresh_left中更新button_inner_3方便
        print("name:",self.name,"len_button_multi:",len(self.button_multi_func_lst))
        # self.btg.setExclusive(True)
        # self.btg_send.setExclusive(True)

        # self.ui.pushButton_9.clicked['bool'].connect(lambda:self.verify())
#------------------------------------------------------------------------------------信号区
        # self.btg.buttonClicked.connect(lambda:self.choose_comu_obj())
        # self.btg_send.buttonClicked.connect(lambda:self.communicate())
        # self.btg_multi_func.buttonClicked.connect(lambda:self.multi_func())
        self.ui.pushButton_4.clicked.connect(lambda:self.refresh_textbrowser_middle())
        self.ui.pushButton_5.clicked.connect(lambda:self.refresh_textbrowser_down())
        self.ui.pushButton_6.clicked.connect(lambda:self.refresh_button_left())
        self.ui.pushButton_7.clicked.connect(lambda:self.refresh_label_top())
        self.ui.pushButton_skip.clicked.connect(lambda:self.refresh_label_sub_top())#将右方消息显示列表改为认证信息显示列表
#------------------------------------------------------------------------------------
        # self.ui.verticalLayout_3.setDirection(self.ui.verticalLayout_3.BottomToTop)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.show()

    def set_size(self,button):
        if button.isChecked():
            self.ui.Mainwindow.resize(1400,600)
            # print('size:',self.ui.Mainwindow.Width)
        else :
            self.ui.Mainwindow.resize(1000,600)

    def verify(self,mode:int):#算法产生Message,
        #
        # 最终将文本赋值给message
        # 
        # #
        self.verify_leader_display=True
        dic_verify={}
        if mode==1:#控制器和簇头认证协议
            message="启动socketserver服务器！\n \
                send_massage线程启动\n \
                第一次握手接收消息 ['IDLead', 'IDas', '2023-04-05 04:39:35.621294', '743988', '8e25779dd8a3146834a0460ada11fb06c82489aa1e39c6295cf1c7774932a46c']\n \
                第二次握手发送消息： ['IDas', 'IDLead', '2023-04-05 04:39:36.639948', '5343', '5cee09dacdc8ce410d25a1e3dc245aa95bddd557613eafbe6a61ab2453e367a2']\n \
                第三次握手发送消息： ['IDLead', 'IDas', '2023-04-05 04:39:36.645947', '4393', '8c16f263d05bf8f73f6edf93be2762f4a9d746cec00bbd648106e24e5c325c88']\n \
                AS_Lead完成秘钥协商：秘钥为: ['6dee631614a49a0816ca8f0d84e7c69e', '41b8febbd806998538f8cbe07e46b6b8']\n"
            message_opponent= "第一次握手发送消息： ['IDLead', 'IDas', '2023-04-05 04:39:35.621294', '743988', '8e25779dd8a3146834a0460ada11fb06c82489aa1e39c6295cf1c7774932a46c']\n \
                第二次握手接收消息： ['IDas', 'IDLead', '2023-04-05 04:39:36.639948', '5343', '5cee09dacdc8ce410d25a1e3dc245aa95bddd557613eafbe6a61ab2453e367a2']\n \
                第三次握手发送消息： ['IDLead', 'IDas', '2023-04-05 04:39:36.645947', '4393', '8c16f263d05bf8f73f6edf93be2762f4a9d746cec00bbd648106e24e5c325c88']\n \
                协商秘钥为： {'IDas': ['6dee631614a49a0816ca8f0d84e7c69e', '41b8febbd806998538f8cbe07e46b6b8']}\n" 
            dic_verify[self.name]=dic_verify.setdefault(self.name,{})
            dic_verify_inner=dic_verify[self.name]
            # dic_verify_inner[self.comu_name]#等待修改，后续会改成线程所以暂时的修改是无用功
            dic_verify[self.verify_leader_display]={"簇头无人机":message_opponent}
        else:
            return#
        self.ui.textBrowser_2.setText(message)

        with open("verify_dis",'w+') as file:
            json.dump(dic_verify,file)
            self.verify_leader_display=False

    def refresh_label_top(self):
        dic=get_dic_from_json(path_json_online)
        self.state=dic[self.name]#更新自身状态
        print("refresh_label_top",self.state)
        txt=self.value_2_job(self.name)
        self.ui.label.setText(txt)
        if self.state==1:#为簇头，将消息池设为可见
            self.ui.frame_14.setVisible(True)
            for ele in self.button_multi_func_lst:
                ele.setVisible(False)
        else:
            self.ui.frame_14.setVisible(False)
            for ele in self.button_multi_func_lst:
                ele.setVisible(True)



    def refresh_button_left(self):
        lst_already_exist=list(self.dic.keys())
        for ele in self.button_lst:
            txt=ele.text()
            ele.setText(self.job_2_name(txt))#还原各个按钮原名称

        self.dic=get_dic_from_json(path_json_online)
        self.dic_verify=get_dic_from_json(path_json_verify)
        print("lst_already_exist",lst_already_exist)
        print("self.dic_now",self.dic)
        print("self.dic_verify_now:",self.dic_verify)
        lst_diff=list(set(self.dic.keys())-set(list(lst_already_exist)))
        print("lst_diff",lst_diff)
        
        for ele in lst_diff:
            # print("第",i,"个按钮")
            self.weight_inner_tmp=None
            # self.weight_lst[i+1]=None
            print("i:",self.i,"ele:",ele) 
            if self.dic[ele]==0:
                print("in here!")
                if self.state==0:#非控制器都显示
                    continue
                print("in here!")
                pushbutton_tmp=QtWidgets.QPushButton(self.value_2_job(ele),self.ui.frame_17)
                if self.dic_verify[ele]==1:
                    pushbutton_tmp.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n")
                self.ui.verticalLayout_2.addWidget(pushbutton_tmp)
                self.weight_inner_tmp=QtWidgets.QFrame()#等效page
                verticalLayout_1 = QtWidgets.QVBoxLayout(self.weight_inner_tmp)
                verticalLayout_1.setObjectName("verticalLayout_1"+str(self.i+1))
                # frame_inner=QtWidgets.QFrame(self.weight_inner_tmp)
                # frame_inner.setObjectName("frame_inner_1"+str(i+1))
                # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                # sizePolicy.setHorizontalStretch(0)
                # sizePolicy.setVerticalStretch(1)
                # sizePolicy.setHeightForWidth(frame_inner.sizePolicy().hasHeightForWidth())
                frame_inner_2=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(frame_inner_2.sizePolicy().hasHeightForWidth())
                frame_inner_2.setSizePolicy(sizePolicy)
                frame_inner_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_2.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_2.setObjectName("frame_inner_2_"+str(self.i+1))
                horizontalLayout= QtWidgets.QHBoxLayout(frame_inner_2)
                horizontalLayout.setObjectName("horizontalLayout_"+str(self.i+1))
                label_inner = QtWidgets.QLabel(frame_inner_2)#frame_inner_2(parent:weight_iinner_tmp)中添加label
                label_inner.setAlignment(QtCore.Qt.AlignCenter)
                label_inner.setObjectName("label_inner_"+str(self.i+1))
                horizontalLayout.addWidget(label_inner)
                verticalLayout_1.addWidget(frame_inner_2)
                print(2)
                frame_inner_3=QtWidgets.QFrame(self.weight_inner_tmp)#frame_inner_3(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(5)
                sizePolicy.setHeightForWidth(frame_inner_3.sizePolicy().hasHeightForWidth())
                frame_inner_3.setSizePolicy(sizePolicy)
                frame_inner_3.setStyleSheet("border-radius:30px;\n""background-color: rgb(156, 216, 191);")
                frame_inner_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_3.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_3.setObjectName("frame_inner_3_"+str(self.i+1))
                horizontalLayout_2=QtWidgets.QHBoxLayout(frame_inner_3)
                horizontalLayout_2.setObjectName("horizontalLayout_2_"+str(self.i+1))
                print(3)
                frame_inner_5=QtWidgets.QFrame(frame_inner_3)#frame_inner_5(parent:frame_inner_3)位于父窗口左边，用于承载textbrowser,见Line-228
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(2)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_5.sizePolicy().hasHeightForWidth())
                frame_inner_5.setSizePolicy(sizePolicy)
                frame_inner_5.setStyleSheet("border-radius:30px;")
                frame_inner_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_5.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_5.setObjectName("frame_inner_5_"+str(self.i+1))

                horizontalLayout_3=QtWidgets.QHBoxLayout(frame_inner_5)
                horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
                horizontalLayout_3.setObjectName("horizontalLayout_3_"+str(self.i+1))
                textbrowser=QtWidgets.QTextBrowser(frame_inner_5)
                textbrowser.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textbrowser.setObjectName("textBrowser_"+str(self.i+1))
                horizontalLayout_3.addWidget(textbrowser)
                horizontalLayout_2.addWidget(frame_inner_5)

                frame_inner_6=QtWidgets.QFrame(frame_inner_3)#frame_inner_6(parent:frame_inner_3),位于父窗口的右侧用于承载顶端Label,textedit和发送按钮，有可能承载认证按钮
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(1)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_6.sizePolicy().hasHeightForWidth())
                frame_inner_6.setSizePolicy(sizePolicy)
                frame_inner_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_6.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_6.setObjectName("frame_inner_6_"+str(self.i+1))
                
                verticalLayout_2=QtWidgets.QVBoxLayout(frame_inner_6)
                verticalLayout_2.setObjectName("verticalLayout_2_"+str(self.i+1))
                label_inner_2=QtWidgets.QLabel(frame_inner_6)
                label_inner_2.setAlignment(QtCore.Qt.AlignCenter)
                label_inner_2.setObjectName("label_inner_2_"+str(self.i+1))
                label_inner_2.setText("消息发送栏")
                textEdit=QtWidgets.QTextEdit(frame_inner_6)
                textEdit.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textEdit.setObjectName("textEdit")
                verticalLayout_2.addWidget(label_inner_2)
                verticalLayout_2.addWidget(textEdit)

                pushButton_inner = QtWidgets.QPushButton(frame_inner_6)
                pushButton_inner.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                pushButton_inner.setObjectName("pushButton_inner_"+str(self.i+1))


                pushButton_inner_2=None

                if self.state==2:#非簇头情况下添加pushbutton_inner_2,在此情况下为认证功能
                    pushButton_inner_2 =  QtWidgets.QPushButton(frame_inner_6)
                    pushButton_inner_2.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                    pushButton_inner_2.setObjectName("pushButton_inner_2"+str(self.i+1))
                    pushButton_inner_2.setText("认证") 
                    verticalLayout_2.addWidget(pushButton_inner_2)
                    pushButton_inner_2.setCheckable(True)
                    pushButton_inner_2.setChecked(False)
                    # self.button_multi_func_lst.append(pushButton_inner_2)
                    # print("len(self.button_multi):",len(self.button_multi_func_lst))
                    
                verticalLayout_2.addWidget(pushButton_inner)
                horizontalLayout_2.addWidget(frame_inner_6)

                verticalLayout_1.addWidget(frame_inner_3)

                frame_inner_4=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(3)
                sizePolicy.setHeightForWidth(frame_inner_4.sizePolicy().hasHeightForWidth())
                frame_inner_4.setSizePolicy(sizePolicy)
                frame_inner_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_4.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_4.setObjectName("frame_inner_4_"+str(self.i+1))
                verticalLayout_1.addWidget(frame_inner_4)
                
                print(4)

                label_inner.setText("当前对象信息发送列表_"+str(self.i+1))
                pushButton_inner.setText("发送")
                print(8)

                self.weight_lst.append(self.weight_inner_tmp)
                self.textbrowser_lst.append(textbrowser)
                self.textedit_lst.append(textEdit)
                pushButton_inner.setCheckable(True)
                pushButton_inner.setChecked(False)
                self.button_send_lst.append(pushButton_inner)
                self.button_multi_func_lst.append(pushButton_inner_2)
                print(9)
                self.btg_send.addButton(pushButton_inner)
                print(10)
                if self.state!=1:
                    self.btg_multi_func.addButton(pushButton_inner_2)
                print(11)
                # print("i=")
                self.ui.stackedWidget.addWidget(self.weight_lst[self.i+1])
                
                print('stackweight 页面数：',self.ui.stackedWidget.count())

                
                self.i+=1
                # pushButton_inner.clicked['bool'].connect(lambda:self.communicate(cnt_inner))
                # print("cnt_inner=",cnt_inner)
                # cnt_inner+=1
                # self.weight_lst[i+1]

                # controller_need_to_add=True

            else:#self.dic.keys()一定是真名，所以使用self.value_2_job转换为job
                if ele==self.name:
                    continue
                pushbutton_tmp=QtWidgets.QPushButton(self.value_2_job(ele),self.ui.frame_17)
                print("verify:",self.dic_verify)
                if self.dic_verify[ele]==1:
                    pushbutton_tmp.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n")
                self.ui.verticalLayout_2.addWidget(pushbutton_tmp)
                
                self.weight_inner_tmp=QtWidgets.QFrame()#等效page
                verticalLayout_1 = QtWidgets.QVBoxLayout(self.weight_inner_tmp)
                verticalLayout_1.setObjectName("verticalLayout_1"+str(self.i+1))
                # frame_inner=QtWidgets.QFrame(self.weight_inner_tmp)
                # frame_inner.setObjectName("frame_inner_1"+str(i+1))
                # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                # sizePolicy.setHorizontalStretch(0)
                # sizePolicy.setVerticalStretch(1)
                # sizePolicy.setHeightForWidth(frame_inner.sizePolicy().hasHeightForWidth())
                frame_inner_2=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(frame_inner_2.sizePolicy().hasHeightForWidth())
                frame_inner_2.setSizePolicy(sizePolicy)
                frame_inner_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_2.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_2.setObjectName("frame_inner_2_"+str(self.i+1))
                horizontalLayout= QtWidgets.QHBoxLayout(frame_inner_2)
                horizontalLayout.setObjectName("horizontalLayout_"+str(self.i+1))
                label_inner = QtWidgets.QLabel(frame_inner_2)#frame_inner_2(parent:weight_iinner_tmp)中添加label
                label_inner.setAlignment(QtCore.Qt.AlignCenter)
                label_inner.setObjectName("label_inner_"+str(self.i+1))
                horizontalLayout.addWidget(label_inner)
                verticalLayout_1.addWidget(frame_inner_2)
                print(2)
                frame_inner_3=QtWidgets.QFrame(self.weight_inner_tmp)#frame_inner_3(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(5)
                sizePolicy.setHeightForWidth(frame_inner_3.sizePolicy().hasHeightForWidth())
                frame_inner_3.setSizePolicy(sizePolicy)
                frame_inner_3.setStyleSheet("border-radius:30px;\n""background-color: rgb(156, 216, 191);")
                frame_inner_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_3.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_3.setObjectName("frame_inner_3_"+str(self.i+1))
                horizontalLayout_2=QtWidgets.QHBoxLayout(frame_inner_3)
                horizontalLayout_2.setObjectName("horizontalLayout_2_"+str(self.i+1))
                print(3)
                frame_inner_5=QtWidgets.QFrame(frame_inner_3)#frame_inner_5(parent:frame_inner_3)位于父窗口左边，用于承载textbrowser,见Line-228
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(2)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_5.sizePolicy().hasHeightForWidth())
                frame_inner_5.setSizePolicy(sizePolicy)
                frame_inner_5.setStyleSheet("border-radius:30px;")
                frame_inner_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_5.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_5.setObjectName("frame_inner_5_"+str(self.i+1))

                horizontalLayout_3=QtWidgets.QHBoxLayout(frame_inner_5)
                horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
                horizontalLayout_3.setObjectName("horizontalLayout_3_"+str(self.i+1))
                textbrowser=QtWidgets.QTextBrowser(frame_inner_5)
                textbrowser.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textbrowser.setObjectName("textBrowser_"+str(self.i+1))
                horizontalLayout_3.addWidget(textbrowser)
                horizontalLayout_2.addWidget(frame_inner_5)

                frame_inner_6=QtWidgets.QFrame(frame_inner_3)#frame_inner_6(parent:frame_inner_3),位于父窗口的右侧用于承载顶端Label,textedit和发送按钮，有可能承载认证按钮
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(1)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(frame_inner_6.sizePolicy().hasHeightForWidth())
                frame_inner_6.setSizePolicy(sizePolicy)
                frame_inner_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_6.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_6.setObjectName("frame_inner_6_"+str(self.i+1))
                
                verticalLayout_2=QtWidgets.QVBoxLayout(frame_inner_6)
                verticalLayout_2.setObjectName("verticalLayout_2_"+str(self.i+1))
                label_inner_2=QtWidgets.QLabel(frame_inner_6)
                label_inner_2.setAlignment(QtCore.Qt.AlignCenter)
                label_inner_2.setObjectName("label_inner_2_"+str(self.i+1))
                label_inner_2.setText("消息发送栏")
                textEdit=QtWidgets.QTextEdit(frame_inner_6)
                textEdit.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textEdit.setObjectName("textEdit")
                verticalLayout_2.addWidget(label_inner_2)
                verticalLayout_2.addWidget(textEdit)

                pushButton_inner = QtWidgets.QPushButton(frame_inner_6)
                pushButton_inner.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                pushButton_inner.setObjectName("pushButton_inner_"+str(self.i+1))


                pushButton_inner_2=None

                if self.state!=1:#非簇头情况下添加pushbutton_inner_2,该按钮有两种功能，控制器为选择簇头，
                    pushButton_inner_2 =  QtWidgets.QPushButton(frame_inner_6)
                    pushButton_inner_2.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                    pushButton_inner_2.setObjectName("pushButton_inner_2"+str(self.i+1))
                    if self.state==2:
                        pushButton_inner_2.setText("认证") 
                    else:
                        pushButton_inner_2.setText("选择为簇头") 
                    verticalLayout_2.addWidget(pushButton_inner_2)
                    pushButton_inner_2.setCheckable(True)
                    pushButton_inner_2.setChecked(False)
                    # self.button_multi_func_lst.append(pushButton_inner_2)
                    # print("len(self.button_multi):",len(self.button_multi_func_lst))
                    if self.state==0:#自身为控制器，添加与簇头之间的认证按钮，控制器与所有无人机都有一认证按钮，但同时只能有一个可见
                        pushButton_inner_3= QtWidgets.QPushButton(frame_inner_6)
                        pushButton_inner_3.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                        pushButton_inner_3.setObjectName("pushButton_inner_3"+str(self.i+1))
                        pushButton_inner_3.setText("与簇头认证")
                        pushButton_inner_3.setCheckable(True)
                        pushButton_inner_3.setChecked(False)
                        verticalLayout_2.addWidget(pushButton_inner_3)
                        pushButton_inner_3.setVisible(False)
                        self.controller_verify_lst.append(pushButton_inner_3)                    # self.button_multi_func_lst.append(pushButton_inner_2)
                        self.btg_controller_verify.addButton(pushButton_inner_3)
                    
                verticalLayout_2.addWidget(pushButton_inner)
                horizontalLayout_2.addWidget(frame_inner_6)

                verticalLayout_1.addWidget(frame_inner_3)

                frame_inner_4=QtWidgets.QFrame(self.weight_inner_tmp)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(3)
                sizePolicy.setHeightForWidth(frame_inner_4.sizePolicy().hasHeightForWidth())
                frame_inner_4.setSizePolicy(sizePolicy)
                frame_inner_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
                frame_inner_4.setFrameShadow(QtWidgets.QFrame.Raised)
                frame_inner_4.setObjectName("frame_inner_4_"+str(self.i+1))
                verticalLayout_1.addWidget(frame_inner_4)
                
                print(4)
                

                label_inner.setText("当前对象信息发送列表_"+str(self.i+1))
                pushButton_inner.setText("发送")
                print(8)

                self.weight_lst.append(self.weight_inner_tmp)
                self.textbrowser_lst.append(textbrowser)
                self.textedit_lst.append(textEdit)
                pushButton_inner.setCheckable(True)
                pushButton_inner.setChecked(False)
                self.button_send_lst.append(pushButton_inner)
                self.button_multi_func_lst.append(pushButton_inner_2)
                print(9)
                self.btg_send.addButton(pushButton_inner)
                print(10)
                if self.state!=1:
                    self.btg_multi_func.addButton(pushButton_inner_2)
                print(11)
                print("i=")
                self.ui.stackedWidget.addWidget(self.weight_lst[self.i+1])
                
                print('stackweight 页面数：',self.ui.stackedWidget.count())

                self.i+=1
            pushbutton_tmp.setFixedHeight(24)
            # self.ui.frame_17.addWidget(pushbutton_tmp)

            self.btg.addButton(pushbutton_tmp)
            self.button_lst.append(pushbutton_tmp)

            pushbutton_tmp.setCheckable(True)
            pushbutton_tmp.setChecked(False)
        for ele in list(self.button_lst):
            txt=ele.text()
            ele.setText(self.value_2_job(txt))
        

        

    def refresh_textbrowser_down(self):
        self.communicate_log=get_dic_from_json(path_json_communicate)
        # dic=get_dic_from_json(path_json_online)
        # self.dic=dic
        st=str()
        for ele in self.communicate_log.keys():#ele为发送者设备名称
            dic_lst=self.communicate_log[ele]
            sender_name=self.value_2_job(ele)
            for i in dic_lst.keys():
                lst_inner=dic_lst[i]#为具体两个设备通讯内容列表
                get_info_name=self.value_2_job(i)
                if sender_name!="簇头无人机" and get_info_name!="簇头无人机":
                    st+=sender_name+"->(待转发)->"+get_info_name+":\n"
                    for i,content_log in enumerate(lst_inner):
                        st+=str(i+1)+":"+content_log+"\n"
        self.ui.textBrowser_3.setPlainText(st)
                

    def multi_func(self):#只有控制器选择普通无人机时才有可能进入此函数
        for i,ele in enumerate(self.button_lst):
            print("button_lst[",i,"]:",self.button_lst[i].text())
        print("len(self.button_lst):",len(self.button_lst))
        print("len(self.button_multi_func_lst):",len(self.button_multi_func_lst))
        
        for i,ele in enumerate(self.button_multi_func_lst):
            if ele.isChecked():
                # print('i:',i)
                # self.leader_idx=i
                # self.leader_name=ele.text()

                if ele.text()=="认证":
                    # ele_text=self.button_lst[i].text() if self.button_lst[i].text()!="簇头无人机" else self.leader_name
                    # ele_text=self.job_2_name(self.comu_name)
                    print("认证ele_text:",self.comu_name)
                    self.verify(2)
                    self.dic_verify=get_dic_from_json(path_json_verify)
                    self.dic_verify[self.comu_name]=1
                    print("self.verfy",self.dic_verify)
                    save_dic_to_json(path_json_verify,self.dic_verify)
                    print("i=",i)
                    self.button_lst[i].setStyleSheet("background-color: rgb(88, 213, 175);\n")
                else:#选择为簇头
                    lst_tmp=list(self.dic.keys())
                    self.dic=get_dic_from_json(path_json_online)
                    print("self.comu_name:",self.comu_name)
                    for i,ele_inner in enumerate(self.button_lst):
                        print("i:",i,"ele_text():",ele_inner.text())
                        if ele_inner.text()==self.comu_name:
                            ele_inner.setText("簇头无人机")
                            ele.setVisible(False)#将选择簇头设置为不可见
                            print("len(self.button_lst):",len(self.button_lst),"len(self.controller_verify_lst):",len(self.controller_verify_lst))

                            self.controller_verify_lst[i].setVisible(True)
                            # dic[self.comu_name]=1#将身份改为簇头
                            # break
                        else:
                            # print(lst_tmp[i])
                            # print('ele.text():',ele.text())
                            # ele.setText(lst_tmp[i])#restore the button's Text() to it's original name
                            ele.setVisible(True)#将选择簇头设置为可见
                            self.controller_verify_lst[i].setVisible(False)
                            ele_inner.setText(self.job_2_name(ele_inner.text()))
                            self.dic[self.job_2_name(ele_inner.text())]=2#将身份还原为Ordinary UAV
                    self.dic[self.comu_name]=1#延迟修改，避免影响else中self.job_2_name的判断
                    save_dic_to_json(path_json_online,self.dic)
                    print("multi_func_dic:",self.dic)  
 

    def refresh_label_sub_top(self):
        if self.sub_label==False:
            self.ui.label_2.setText("认证消息列表")
                # dic_verify_communication=None
            with open("verify_dis",'r') as file:
                dic_verify_communication=json.load(file)
                self.verify_leader_display=list(dic_verify_communication.keys())[0]
            print("self.verify_leader_display:",self.verify_leader_display)
            if self.verify_leader_display=="true":
                print("self.verify_communcation:",dic_verify_communication[self.verify_leader_display])
                print("self.value_2_job:",self.value_2_job(self.name))
                txt=dic_verify_communication[self.verify_leader_display].setdefault(self.value_2_job(self.name),None)
                print("txt:",txt)
                if txt is not None:
                    self.ui.textBrowser_2.setPlainText(txt)
                self.verify_leader_display=False
            self.communicate_log=get_dic_from_json(path_json_communicate)
            print("communicate_log",self.communicate_log)
            # dic=get_dic_from_json(path_json_online)
            # self.dic=dic#顺便更新一下self.dic在线列表
            # print("inhere!")
            print(self.communicate_log)  
            self.sub_label=True#下次skip时变为消息显示列表   
        else:
            self.ui.label_2.setText("消息显示列表")
            self.refresh_textbrowser_middle()
            self.sub_label=False        
                                                                            #与show_2不同点：1.只能刷新中间聊天窗口
                                                                                          #2.ID,ID_2,message按照格式添加入communication文件
    def show_1(self,obj:QtWidgets.QTextBrowser,ID:str,ID_2:str,message:str):#刷新中间聊天窗口内容，向其中添加ID->ID_2的一条message聊天内容
        dic=get_dic_from_json(path_json_communicate)
        # if name_bt.find("簇头")!=-1:
        #     name_bt=name_bt.strip("簇头")
        dic[ID]=dic.setdefault(ID,{})
        dic_inner=dic[ID]
        # print("in communicate(): self.comu_name=",self.comu_name)
        dic_inner[ID_2]=dic_inner.setdefault(ID_2,[])
        lst_comu_log=dic_inner[ID_2]
        st=str()
        for ele in lst_comu_log:
            st+=ele+"\n"
        # lst_comu_log.append(self.textedit_lst[idx].toPlainText())
        lst_comu_log.append(message)
        self.communicate_log=dic
        st+=message
        obj.setPlainText(st)
        # self.textbrowser_lst[idx].setPlainText(st)
        # self.textbrowser_lst[0].setPlainText("test_1")
        # self.textbrowser_lst[1].setPlainText("test_2")
        
        save_dic_to_json(path_json_communicate,dic)
        # self.ui.textBrowser_2.setPlainText()

    def show_2(self,obj:QtWidgets.QTextBrowser,message:str):#任何一个聊天窗口清空后显示message内容
        obj.setPlainText(message)
        

    def refresh_textbrowser_middle(self):#窗口右侧的总通信记录
        
        st=str()
        for ele in self.communicate_log.keys():#ele为发送者设备名称
            dic_lst=self.communicate_log[ele]
            print('ele:',ele)
            sender_name=self.value_2_job(ele)
            for i in dic_lst.keys():
                lst_inner=dic_lst[i]#为具体两个设备通讯内容列表
                print('i:',i)
                get_info_name=self.value_2_job(i)
                st+=sender_name+"->"+get_info_name+":\n"
                for cnt,content_log in enumerate(lst_inner):
                    st+=str(cnt+1)+":"+content_log+"\n"
        self.ui.textBrowser_2.setPlainText(st)

    def job_2_name(self,name):#将按钮文字转换为功能，控制器，簇头，无人机
        dic=get_dic_from_json(path_json_online)
        # text=dic[name]
        if name=="控制器":
            return [k for k,v in dic.items() if v==0][0]
        elif name=='簇头无人机':
            return [k for k,v in dic.items() if v==1][0]
        else:
            return name
    def value_2_job(self,value):
        dic=get_dic_from_json(path_json_online)
        if dic[value]==0:
            return "控制器"
        elif dic[value]==1:
            return "簇头无人机"
        else:
            return value


    def communicate(self):
        idx=-1
        for i,ele in enumerate(self.button_send_lst):
            if ele.isChecked():
                # self.comu_name=ele.text()
                idx=i
        self.show_1(self.textbrowser_lst[idx],self.name,self.comu_name,self.textedit_lst[idx].toPlainText())
        self.textedit_lst[idx].setPlainText("")
        # print('idx=',idx)
        # st=str()
        

    def choose_comu_obj(self):
        print('in choose_comu_obj_function!')
        print('stackweight 页面数：',self.ui.stackedWidget.count())
        # if self.state!=0:#非控制器不能选择簇头
        #     return 
        # name=str()
        for i,ele in enumerate(self.button_lst):
            # name=ele.text()
            ele_text=ele.text()
            print(ele_text)
            # if ele_text=="簇头无人机":
            #     ele_text=[k for k,v in self.dic.items() if v==1][0]
            # elif ele_text=="控制器":
            #     ele_text=[k for k,v in self.dic.items() if v==0][0]
            print(ele_text)
            ele_text=self.job_2_name(ele_text)
            print("choose_comu_obj_i:",i,"ele_text:",ele_text)
            # if ele.text()!="簇头无人机" else self.leader_name 
            if ele.isChecked():
                self.ui.stackedWidget.setCurrentIndex(i+3)
                self.comu_name=ele_text
                print(self.comu_name,"is clicked it's job is ",self.dic[self.comu_name])
                if self.dic_verify[ele_text]==1:
                    ele.setStyleSheet('background-color: rgb(88, 213, 175);\n')
                else:
                    ele.setStyleSheet("	background-color: rgb(193, 125, 17);\n")
                # self.comu_name=name
                # print("self.comu_name change_to:",self.comu_name)
            else:
                if self.dic_verify[ele_text]==1:#经过验证，恢复绿色渐变底色
                    ele.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n')
                else :
                    ele.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(184, 166, 132, 255), stop:1 rgba(255, 255, 255, 255));\n")
        # str_tmp=self.ui.label_2.text()[:2]
        # self.ui.comboBox.clear()
        # self.ui.comboBox.addItems(self.lst)
        # self.ui.label_2.setText(str_tmp+name)

    # def change_leader(self):#非控制器页面不会跳转此函数
    #     # print('stackweight 页面数：',self.ui.stackedWidget.count())
    #     if self.state!=0:#非控制器不能选择簇头
    #         return 
    #     name=str()
    #     for i,ele in enumerate(self.button_lst):
    #         name=ele.text()
    #         if ele.isChecked():
    #             ele.setStyleSheet('	background-color: rgb(78, 154, 6);\n')
    #             print(name)
    #             ele.setText(name+'簇头')
    #             self.lst[i]+="簇头"
    #             program.leader_idx=i
    #         else:
    #             if ele.text().find("簇头")!=-1:
    #                 ele.setText(name.strip("簇头"))
    #                 self.lst[i]=self.lst[i].strip("簇头")
    #             ele.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n')

    def set_color(self,ele):
        ele.setStyleSheet(lambda:"background-color: rgb(239, 41, 41);")

    def get_list(self)->list():#返回在线名单，列表的形式
        self.dic=get_dic_from_json(path_json_online)
        for ele in self.dic.keys():
            if self.dic[ele]==0 and self.state!=0:#控制器且自己不是控制器
                self.lst.append('控制器')
            else:
                self.lst.append(ele)
        program.leader_idx=-1

    def add_controls(self,frame,page,idx:int):#在stackweight中添加按键按下弹出的窗口
        #stackweight设置页面
        page=QtWidgets.QWidget()
        page.setObjectName("page_"+str(idx))
        verticalLayout=QtWidgets.QStackedWidget(frame)
        self.stackedWidget.setStyleSheet("background-color: rgba(0, 0, 0,0);")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, mouse_event):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(mouse_event.globalPos() - self.m_Position)  # 更改窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

if __name__=='__main__':
    # with Manager as manager:
    #     dic_online= manager.dict()
    #     dic_verify= manager.dict()
    # p1= Process(target=program,args=("无人机_1"))
    # p2= Process(target=program,args=("无人机_2"))
    # p3= Process(target=program,args=("无人机_3"))
    # p1.start()
    # p2.start()
    # p3.start()
    # p1.join()
    # p2.join()
    # p3.join()
    program(sys.argv[1])
