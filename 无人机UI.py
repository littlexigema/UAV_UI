from Ui_无人机登录界面i import *
from Ui_无人机二级界面_改 import *
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QButtonGroup,QPushButton
from PyQt5.QtCore import Qt

import sys
import json

#------------带添加，根据state读取不同lineedit中的内容，实现不同账号登录
#sh文件改进，判断哪些pyton文件结束并修改json文件内容
#在登录后，根据不同的登录角色更新json内容，value为0表示leader,1表示簇头，2表示普通无人机

path_json_online='temporary_save'
path_json_communicate='communication'
path_json_verify='verify'

def get_dic_from_json(path):#从json加载字典
    with open(path,'r') as file:
        return json.load(file)

def save_dic_to_json(path,dic):
    with open(path,'w+') as file:
        json.dump(dic,file)

class program:
    ip='192.168.1.1'
    port='8888'
    cnt_online_uav=0
    controller=False
    def __init__(self,name):
        self.app = QApplication(sys.argv)
        self.win = LoginWindow(name)
        dic=None
        dic=get_dic_from_json(path_json_online)
        dic_2=get_dic_from_json(path_json_verify)
        print(dic)
        dic[name]=2
        dic_2[name]=0#0未经验证，1经过验证
        save_dic_to_json(path_json_online,dic)
        save_dic_to_json(path_json_verify,dic_2)

        print(dic)

        self.name=name
        sys.exit(self.app.exec_())

    
    # def refesh_list():#获得在线名单,具体方法在InterfaceWindow类中的get_list()中实现
        # self.list=


class LoginWindow(QMainWindow):
    def __init__(self,name):
        program.cnt_online_uav+=1
        super().__init__()
        self.ui = Ui_MainWindow_1()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.pushButton.clicked['bool'].connect(lambda:self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_2.clicked['bool'].connect(lambda:self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.pushButton_5.clicked['bool'].connect(lambda:self.go_to_inter(2))
        self.ui.pushButton_7.clicked['bool'].connect(lambda:self.go_to_inter(0))

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
            if state==0:#控制器登录
                dic=get_dic_from_json(path_json_online)
                dic[self.name]=0
                print(dic)
                save_dic_to_json(path_json_online,dic)

            # dic[program.name]
            self.win=InterfaceWindow(self.name,state)
            print("打开次级窗口")
            self.close()
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
        self.leader_idx=-1

        self.button_lst=[]#为了更方便的遍历按钮,位于界面左侧的所有按钮
        self.weight_lst=[]
        self.textbrowser_lst=[]
        self.textedit_lst=[]
        self.button_send_lst=[]
        self.button_multi_func_lst=[]
        self.weight_inner_tmp=None
        self.communicate_log={}

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
        self.ui.label.setText(self.value_2_job(self.dic,self.name,self.name))#因为传入dic所以该函数内，对于keys()的keyerror处理的函数对该调用没有影响
        #-----------------------------
        print("self.dic.keys():",self.dic.keys())

        i=0
        for ele in list(self.dic.keys()):
            # print("第",i,"个按钮")
            self.weight_inner_tmp=None
            # self.weight_lst[i+1]=None
            print("i:",i,"ele:",ele) 
            if self.dic[ele]==0:
                print("in here!")
                if self.state==0:#非控制器都显示
                    continue
                print("in here!")
                pushbutton_tmp=QtWidgets.QPushButton('控制器',self.ui.frame_17)
                if self.dic_verify[ele]==1:
                    pushbutton_tmp.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n")
                self.ui.verticalLayout_2.addWidget(pushbutton_tmp)
                self.weight_inner_tmp=QtWidgets.QFrame()#等效page
                verticalLayout_1 = QtWidgets.QVBoxLayout(self.weight_inner_tmp)
                verticalLayout_1.setObjectName("verticalLayout_1"+str(i+1))
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
                frame_inner_2.setObjectName("frame_inner_2_"+str(i+1))
                horizontalLayout= QtWidgets.QHBoxLayout(frame_inner_2)
                horizontalLayout.setObjectName("horizontalLayout_"+str(i+1))
                label_inner = QtWidgets.QLabel(frame_inner_2)#frame_inner_2(parent:weight_iinner_tmp)中添加label
                label_inner.setAlignment(QtCore.Qt.AlignCenter)
                label_inner.setObjectName("label_inner_"+str(i+1))
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
                frame_inner_3.setObjectName("frame_inner_3_"+str(i+1))
                horizontalLayout_2=QtWidgets.QHBoxLayout(frame_inner_3)
                horizontalLayout_2.setObjectName("horizontalLayout_2_"+str(i+1))
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
                frame_inner_5.setObjectName("frame_inner_5_"+str(i+1))

                horizontalLayout_3=QtWidgets.QHBoxLayout(frame_inner_5)
                horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
                horizontalLayout_3.setObjectName("horizontalLayout_3_"+str(i+1))
                textbrowser=QtWidgets.QTextBrowser(frame_inner_5)
                textbrowser.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textbrowser.setObjectName("textBrowser_"+str(i+1))
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
                frame_inner_6.setObjectName("frame_inner_6_"+str(i+1))
                
                verticalLayout_2=QtWidgets.QVBoxLayout(frame_inner_6)
                verticalLayout_2.setObjectName("verticalLayout_2_"+str(i+1))
                label_inner_2=QtWidgets.QLabel(frame_inner_6)
                label_inner_2.setAlignment(QtCore.Qt.AlignCenter)
                label_inner_2.setObjectName("label_inner_2_"+str(i+1))
                label_inner_2.setText("消息发送栏")
                textEdit=QtWidgets.QTextEdit(frame_inner_6)
                textEdit.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textEdit.setObjectName("textEdit")
                verticalLayout_2.addWidget(label_inner_2)
                verticalLayout_2.addWidget(textEdit)

                pushButton_inner = QtWidgets.QPushButton(frame_inner_6)
                pushButton_inner.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                pushButton_inner.setObjectName("pushButton_inner_"+str(i+1))


                pushButton_inner_2=None

                if self.state!=1:#非簇头情况下添加pushbutton_inner_2,该按钮有两种功能，控制器为选择簇头，
                    pushButton_inner_2 =  QtWidgets.QPushButton(frame_inner_6)
                    pushButton_inner_2.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                    pushButton_inner_2.setObjectName("pushButton_inner_2"+str(i+1))
                    if self.state==2:
                        pushButton_inner_2.setText("认证") 
                    else:
                        pushButton_inner_2.setText("选择为簇头") 
                    verticalLayout_2.addWidget(pushButton_inner_2)
                    pushButton_inner_2.setCheckable(True)
                    pushButton_inner_2.setChecked(False)
                    self.button_multi_func_lst.append(pushButton_inner_2)
                    
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
                frame_inner_4.setObjectName("frame_inner_4_"+str(i+1))
                verticalLayout_1.addWidget(frame_inner_4)
                
                print(4)
                if self.state==1:#为簇头,添加消息池
                    print(5)
                    horizontalLayout_4=QtWidgets.QHBoxLayout(frame_inner_4)
                    horizontalLayout_4.setObjectName("horizontalLyout_4")
                    label_inner_4=QtWidgets.QLabel(frame_inner_4)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                    sizePolicy.setHorizontalStretch(1)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(label_inner_4.sizePolicy().hasHeightForWidth())
                    label_inner_4.setSizePolicy(sizePolicy)
                    label_inner_4.setAlignment(QtCore.Qt.AlignCenter)
                    label_inner_4.setObjectName("label_Inner_4")
                    horizontalLayout_4.addWidget(label_inner_4)
                    textbrowser_inner_pool=QtWidgets.QTextBrowser(frame_inner_4)
                    print(6)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                    sizePolicy.setHorizontalStretch(5)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(textbrowser_inner_pool.sizePolicy().hasHeightForWidth())
                    textbrowser_inner_pool.setSizePolicy(sizePolicy)
                    textbrowser_inner_pool.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                    textbrowser_inner_pool.setObjectName("text_broswer_info_pool")
                    horizontalLayout_4.addWidget(textbrowser_inner_pool)
                    pushButton_inner_refresh=QtWidgets.QPushButton(frame_inner_4)
                    pushButton_inner_refresh.setText("")
                    icon2 = QtGui.QIcon()
                    print(7)
                    icon2.addPixmap(QtGui.QPixmap(":/icon/Pictures/icon_white/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    pushButton_inner_refresh.setIcon(icon2)
                    pushButton_inner_refresh.setObjectName("pushButton_refresh_in_pool")
                    horizontalLayout_4.addWidget(pushButton_inner_refresh)
                    pushButton_inner_refresh.clicked.connect(lambda:self.refresh_textbrowser_down())
                    # verticalLayout_1.addWidget(frame_inner_4)





                label_inner.setText("当前对象信息发送列表_"+str(i+1))
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
                self.ui.stackedWidget.addWidget(self.weight_lst[i+1])
                
                print('stackweight 页面数：',self.ui.stackedWidget.count())

                
                i+=1
                # pushButton_inner.clicked['bool'].connect(lambda:self.communicate(cnt_inner))
                # print("cnt_inner=",cnt_inner)
                # cnt_inner+=1
                # self.weight_lst[i+1]

                # controller_need_to_add=True

            else:
                if ele==self.name:
                    continue
                pushbutton_tmp=QtWidgets.QPushButton(ele,self.ui.frame_17)
                if self.dic_verify[ele]==1:
                    pushbutton_tmp.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n")
                self.ui.verticalLayout_2.addWidget(pushbutton_tmp)
                
                self.weight_inner_tmp=QtWidgets.QFrame()#等效page
                verticalLayout_1 = QtWidgets.QVBoxLayout(self.weight_inner_tmp)
                verticalLayout_1.setObjectName("verticalLayout_1"+str(i+1))
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
                frame_inner_2.setObjectName("frame_inner_2_"+str(i+1))
                horizontalLayout= QtWidgets.QHBoxLayout(frame_inner_2)
                horizontalLayout.setObjectName("horizontalLayout_"+str(i+1))
                label_inner = QtWidgets.QLabel(frame_inner_2)#frame_inner_2(parent:weight_iinner_tmp)中添加label
                label_inner.setAlignment(QtCore.Qt.AlignCenter)
                label_inner.setObjectName("label_inner_"+str(i+1))
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
                frame_inner_3.setObjectName("frame_inner_3_"+str(i+1))
                horizontalLayout_2=QtWidgets.QHBoxLayout(frame_inner_3)
                horizontalLayout_2.setObjectName("horizontalLayout_2_"+str(i+1))
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
                frame_inner_5.setObjectName("frame_inner_5_"+str(i+1))

                horizontalLayout_3=QtWidgets.QHBoxLayout(frame_inner_5)
                horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
                horizontalLayout_3.setObjectName("horizontalLayout_3_"+str(i+1))
                textbrowser=QtWidgets.QTextBrowser(frame_inner_5)
                textbrowser.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textbrowser.setObjectName("textBrowser_"+str(i+1))
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
                frame_inner_6.setObjectName("frame_inner_6_"+str(i+1))
                
                verticalLayout_2=QtWidgets.QVBoxLayout(frame_inner_6)
                verticalLayout_2.setObjectName("verticalLayout_2_"+str(i+1))
                label_inner_2=QtWidgets.QLabel(frame_inner_6)
                label_inner_2.setAlignment(QtCore.Qt.AlignCenter)
                label_inner_2.setObjectName("label_inner_2_"+str(i+1))
                label_inner_2.setText("消息发送栏")
                textEdit=QtWidgets.QTextEdit(frame_inner_6)
                textEdit.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                textEdit.setObjectName("textEdit")
                verticalLayout_2.addWidget(label_inner_2)
                verticalLayout_2.addWidget(textEdit)

                pushButton_inner = QtWidgets.QPushButton(frame_inner_6)
                pushButton_inner.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                pushButton_inner.setObjectName("pushButton_inner_"+str(i+1))


                pushButton_inner_2=None

                if self.state!=1:#非簇头情况下添加pushbutton_inner_2,该按钮有两种功能，控制器为选择簇头，
                    pushButton_inner_2 =  QtWidgets.QPushButton(frame_inner_6)
                    pushButton_inner_2.setStyleSheet("border-radius:5px;\n""background-color: rgb(119, 169, 185);")
                    pushButton_inner_2.setObjectName("pushButton_inner_2"+str(i+1))
                    if self.state==2:
                        pushButton_inner_2.setText("认证") 
                    else:
                        pushButton_inner_2.setText("选择为簇头") 
                    verticalLayout_2.addWidget(pushButton_inner_2)
                    pushButton_inner_2.setCheckable(True)
                    pushButton_inner_2.setChecked(False)
                    self.button_multi_func_lst.append(pushButton_inner_2)
                    
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
                frame_inner_4.setObjectName("frame_inner_4_"+str(i+1))
                verticalLayout_1.addWidget(frame_inner_4)
                
                print(4)
                if self.state==1:#为簇头,添加消息池
                    print(5)
                    horizontalLayout_4=QtWidgets.QHBoxLayout(frame_inner_4)
                    horizontalLayout_4.setObjectName("horizontalLyout_4")
                    label_inner_4=QtWidgets.QLabel(frame_inner_4)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                    sizePolicy.setHorizontalStretch(1)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(label_inner_4.sizePolicy().hasHeightForWidth())
                    label_inner_4.setSizePolicy(sizePolicy)
                    label_inner_4.setAlignment(QtCore.Qt.AlignCenter)
                    label_inner_4.setObjectName("label_Inner_4")
                    horizontalLayout_4.addWidget(label_inner_4)
                    textbrowser_inner_pool=QtWidgets.QTextBrowser(frame_inner_4)
                    print(6)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                    sizePolicy.setHorizontalStretch(5)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(textbrowser_inner_pool.sizePolicy().hasHeightForWidth())
                    textbrowser_inner_pool.setSizePolicy(sizePolicy)
                    textbrowser_inner_pool.setStyleSheet("border-radius:30px;\n""background-color: rgb(255, 255, 255);")
                    textbrowser_inner_pool.setObjectName("text_broswer_info_pool")
                    horizontalLayout_4.addWidget(textbrowser_inner_pool)
                    pushButton_inner_refresh=QtWidgets.QPushButton(frame_inner_4)
                    pushButton_inner_refresh.setText("")
                    icon2 = QtGui.QIcon()
                    print(7)
                    icon2.addPixmap(QtGui.QPixmap(":/icon/Pictures/icon_white/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    pushButton_inner_refresh.setIcon(icon2)
                    pushButton_inner_refresh.setObjectName("pushButton_refresh_in_pool")
                    horizontalLayout_4.addWidget(pushButton_inner_refresh)
                    pushButton_inner_refresh.clicked.connect(lambda:self.refresh_textbrowser_down())
                    # verticalLayout_1.addWidget(frame_inner_4)





                label_inner.setText("当前对象信息发送列表_"+str(i+1))
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
                self.ui.stackedWidget.addWidget(self.weight_lst[i+1])
                
                print('stackweight 页面数：',self.ui.stackedWidget.count())

                i+=1
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
        # self.btg.setExclusive(True)
        # self.btg_send.setExclusive(True)

        # self.ui.pushButton_9.clicked['bool'].connect(lambda:self.verify())
#------------------------------------------------------------------------------------信号区
        # self.btg.buttonClicked.connect(lambda:self.choose_comu_obj())
        # self.btg_send.buttonClicked.connect(lambda:self.communicate())
        # self.btg_multi_func.buttonClicked.connect(lambda:self.multi_func())
        self.ui.pushButton_4.clicked.connect(lambda:self.refresh_textbrowser_middle())
        # self.ui.pushButton_6.clicked.connect(lambda:self.refresh_button_left())
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

    def verify(self):#算法产生Message,
        #
        # 最终将文本赋值给message
        # 
        # #
        message="verifying...\nwait a second......"
        self.ui.textBrowser_2.setText(message)

    # def refresh_button_left(self):
    #     for ele in self.weight_lst:
    #         self.ui.stackedWidget.removeWidget(ele)#移出页
    #     for ele in self.button_send_lst:
    #         self.btg_send.removeButton(ele)
    #     for ele in self.button_lst:
    #         self.btg.removeButton(ele)

    #     item_list = list(range(self.ui.verticalLayout_2.count()))
    #     item_list.reverse()# 倒序删除，避免影响布局顺序

    #     for i in item_list:
    #         item = self.ui.verticalLayout_2.itemAt(i)
    #         if i==len(item_list)-1:
    #             break
    #         self._ui.myLayout.removeItem(item)
    #         if item.widget():
    #             item.widget().deleteLater()

    #     for ele in self.button_multi_func_lst:
    #         self.btg_multi_func.removeButton(ele)

        

    def refresh_textbrowser_down(self):
        self.communicate_log=get_dic_from_json(path_json_communicate)
        dic=get_dic_from_json(path_json_online)
        self.dic=dic
        st=str()
        for ele in self.communicate_log.keys():#ele为发送者设备名称
            dic_lst=self.communicate_log[ele]
            sender_name=self.value_2_job(dic,ele,ele)
            for i in dic_lst.keys():
                lst_inner=dic_lst[i]#为具体两个设备通讯内容列表
                get_info_name=self.value_2_job(dic,i,i)
                st+=sender_name+"->"+get_info_name+":\n"
                for cnt,content_log in enumerate(lst_inner):
                    st+=str(cnt+1)+":"+content_log+"\n"

    def multi_func(self):#只有控制器选择普通无人机时才有可能进入此函数
        for i,ele in enumerate(self.button_multi_func_lst):
            if ele.isChecked():
                print('i:',i)
                self.leader_idx=i
                self.leader_name=ele.text()

                if ele.text()=="认证":
                    ele_text=self.button_lst[i].text() if self.button_lst[i].text()!="簇头无人机" else self.leader_name
                    self.verify()
                    self.dic_verify=get_dic_from_json(path_json_verify)
                    self.dic_verify[ele_text]=1
                else:#选择为簇头
                    lst_tmp=list(self.dic.keys())
                    dic=get_dic_from_json(path_json_online)
                    for i,ele in enumerate(self.button_lst):
                        if ele.text()==self.comu_name:
                            ele.setText("簇头无人机")
                            dic[self.comu_name]=1#将身份改为簇头
                            break
                        # else:
                        #     print(lst_tmp[i])
                        #     print('ele.text():',ele.text())
                        #     ele.setText(lst_tmp[i])#restore the button's Text() to it's original name
                        #     dic[ele.text()]=2#讲身份还原为Ordinary UAV
                    
                    
                    save_dic_to_json(path_json_online,dic)
                    print("multi_func_dic:",dic)
                        

                    
                

    def refresh_textbrowser_middle(self):#窗口右侧的总通信记录
        self.communicate_log=get_dic_from_json(path_json_communicate)
        print("communicate_log",self.communicate_log)
        dic=get_dic_from_json(path_json_online)
        self.dic=dic#顺便更新一下self.dic在线列表
        # print("inhere!")
        print(self.communicate_log)
        st=str()
        for ele in self.communicate_log.keys():#ele为发送者设备名称
            dic_lst=self.communicate_log[ele]
            sender_name=self.value_2_job(dic,ele,ele)
            for i in dic_lst.keys():
                lst_inner=dic_lst[i]#为具体两个设备通讯内容列表
                get_info_name=self.value_2_job(dic,i,i)
                st+=sender_name+"->"+get_info_name+":\n"
                for cnt,content_log in enumerate(lst_inner):
                    st+=str(cnt+1)+":"+content_log+"\n"
        self.ui.textBrowser_2.setPlainText(st)

    def value_2_job(self,dic,value,default_name):
        print(dic,value)
        if value=="簇头无人机":
            value=self.leader_name
        if dic[value]==0:#发送信息者为控制器
            return "控制器"
        elif dic[value]==1:#发送信息者为簇头
            return "簇头无人机"
        else:
            return default_name



    def communicate(self):
        idx=-1
        for i,ele in enumerate(self.button_send_lst):
            if ele.isChecked():
                idx=i
        print('idx=',idx)
        st=str()
        dic=get_dic_from_json(path_json_communicate)
        # if name_bt.find("簇头")!=-1:
        #     name_bt=name_bt.strip("簇头")
        dic[self.name]=dic.setdefault(self.name,{})
        dic_inner=dic[self.name]
        dic_inner[self.comu_name]=dic_inner.setdefault(self.comu_name,[])
        lst_comu_log=dic_inner[self.comu_name]
        for ele in lst_comu_log:
            st+=ele
        lst_comu_log.append(self.textedit_lst[idx].toPlainText())
        self.communicate_log=dic
        st+=self.textedit_lst[idx].toPlainText()
        self.textedit_lst[idx].setText("")
        # print("st=",st)
        # print(self.textedit_lst[idx].toPlainText())
        # lst_comu_log.append(textbrowser.text())
        self.textbrowser_lst[idx].setPlainText(st)
        # self.textbrowser_lst[0].setPlainText("test_1")
        # self.textbrowser_lst[1].setPlainText("test_2")
        
        save_dic_to_json(path_json_communicate,dic)


    def choose_comu_obj(self):
        print('in choose_comu_obj_function!')
        print('stackweight 页面数：',self.ui.stackedWidget.count())
        # if self.state!=0:#非控制器不能选择簇头
        #     return 
        # name=str()
        for i,ele in enumerate(self.button_lst):
            # name=ele.text()
            ele_text=ele.text() if ele.text()!="簇头无人机" else self.leader_name 
            if ele.isChecked():
                self.ui.stackedWidget.setCurrentIndex(i+3)
                if self.dic_verify[ele_text]==1:
                    ele.setStyleSheet('background-color: rgb(88, 213, 175);\n')
                else:
                    ele.setStypeSheet("	background-color: rgb(193, 125, 17);\n")
                # self.comu_name=name
                # print("self.comu_name change_to:",self.comu_name)
            else:
                if self.dic_verify[ele_text]==1:#经过验证，恢复绿色渐变底色
                    ele.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(88, 213, 175, 255), stop:1 rgba(255, 255, 255, 255));\n')
                else :
                    ele.setStypeSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(184, 166, 132, 255), stop:1 rgba(255, 255, 255, 255));\n")
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
    program(sys.argv[1])
