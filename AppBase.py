# MemberRegisterSystemの抽象基底クラス
from abc import ABCMeta, abstractmethod
import tkinter as tk
from tkinter import messagebox as mbox
import tkinter.ttk as ttk              # Treeviewを利用

# 美しくない抽象基底クラス
class AppBase(tk.Frame, metaclass=ABCMeta):
    def __init__(self, master=None):
        ''' メニューの展開先をモード化し、実行後forgetするウィジェットを管理。
        モードは 0->メニュー, 1->登録, 2->一覧表示, 3->検索, 4->修正 とする'''
        super().__init__(master)
        self.mode = 0
        self.header_lbl = tk.Label(self,text="＜操作を選んでください＞")
        self.header_lbl.pack()
        self.menu_widgets()
        self.pack()
        #各モードからメニューへ戻るボタンを定義
        self.back_menu_btn = tk.Button(self, text="メニューに戻る", command=self.clear_widgets)


    def menu_widgets(self):
        '''各メニューへの展開用ボタン(メニュー展開後は隠す)'''
        self.menu_frm = tk.Frame(self)
        self.menu_frm.pack()
        self.register_btn = tk.Button(self.menu_frm, text="会員\n登録", command=self.register_widgets)
        self.register_btn.pack(side="left")
        self.show_lst_btn = tk.Button(self.menu_frm, text="会員\n一覧", command=self.show_list)
        self.show_lst_btn.pack(side="left")
        self.search_btn =  tk.Button(self.menu_frm, text="情報\n修正", command=self.search_widgets)
        self.search_btn.pack(side="left")


    def register_widgets(self):
        '''登録・修正用ウィジェット。
        登録時はmode=0で展開されるが、修正時はmode=3で展開するため、
        隠すフレームと表示内容をmodeで分岐処理させ、エラーが出ないようにする'''
        self.reg_frm = tk.Frame(self)
        self.reg_frm.pack()
        self.reg_btn = tk.Button(self.reg_frm) # configするので先に定義
        if self.mode == 0:                     # 展開元がメニューモードなら
            self.menu_frm.pack_forget()        # メニューボタン(menu_frm)を隠す
            self.disp_header("＜会員情報を入力してください＞")
            self.reg_btn.config(text="登録する", command=self.register_member)
            self.mode = 1
        elif self.mode == 3:                   # 展開元が検索モードなら
            self.reg_btn.config(text="修正する", command=self.update_member)
            self.del_btn = tk.Button(self.reg_frm, text="削除する", command=self.delete_member)
            self.del_btn.pack(side=tk.BOTTOM)
            self.mode = 4 
        tk.Label(self.reg_frm, text="名前").pack(side=tk.TOP)
        self.name = tk.Entry(self.reg_frm, width=30)
        self.name.pack()
        tk.Label(self.reg_frm, text="性別").pack()
        gender_frm = tk.Frame(self.reg_frm)
        genders = ["男性", "女性", "その他"]
        self.gender_sv = tk.StringVar()
        self.gender_sv.set(genders[0])
        for gender in genders:
            rb = tk.Radiobutton(gender_frm, value= gender, text=gender, variable=self.gender_sv)
            rb.pack(side=tk.LEFT)
        gender_frm.pack()
        tk.Label(self.reg_frm, text="年齢").pack()
        age_frm = tk.Frame(self.reg_frm)
        self.age = tk.Entry(age_frm, width=7)
        self.age.pack(side=tk.LEFT)
        tk.Label(age_frm, text="歳").pack(side=tk.LEFT)
        age_frm.pack()
        self.reg_btn.pack()
        self.back_menu_btn.pack()


    def show_list_widgets(self):
        '''一覧表示用ウィジェット'''
        self.disp_header("＜会員一覧＞")
        self.menu_frm.pack_forget()
        self.mode = 2
        self.lst_frm = tk.Frame(self)
        self.lst_frm.pack()

        # treeviewのヘッダー、表示する行数と幅を設定
        self.tree = ttk.Treeview(self.lst_frm)
        self.tree["column"] = (1, 2, 3, 4)
        self.tree["show"] = "headings"
        self.tree.heading(1, text="ID")
        self.tree.heading(2, text="名前")
        self.tree.heading(3, text="性別")
        self.tree.heading(4, text="年齢")
        self.tree.column(1, width=40, anchor=tk.CENTER)
        self.tree.column(2, width=190)
        self.tree.column(3, width=45, anchor=tk.CENTER)
        self.tree.column(4, width=40, anchor=tk.CENTER)

        # 表の中身を等幅フォントで表示するための設定
        style = ttk.Style()
        style.configure("Treeview",font=("MS Gothic",9))
        self.tree.pack()
        self.back_menu_btn.pack()


    def search_widgets(self):
        ''' 検索用ウィジェット(IDか氏名入力後に修正用ウィジェットを呼び出す)'''
        self.disp_header("＜修正・削除する会員のIDか氏名を入力してください＞")
        self.menu_frm.pack_forget()
        self.mode = 3
        self.search_frm = tk.Frame(self)
        self.search_frm.pack()
        self.ID_or_name = tk.Entry(self.search_frm, width=30)
        self.ID_or_name.pack()
        self.search_btn = tk.Button(self.search_frm, text="会員を検索",command=self.search_cmd)
        self.search_btn.pack()
        self.back_menu_btn.pack()
    

    def clear_widgets(self):
        ''' 処理後にウィジェットを初期化する'''
        # 隠すウィジェットをモードで判定する
        if self.mode in(1, 4): # 登録モードまたは修正モード
            self.name.delete(0, "end")
            self.age.delete(0, "end")
            self.reg_frm.pack_forget()
            if  self.mode == 4: # 修正モード
                self.del_btn.pack_forget() 
        elif self.mode == 2: # 一覧表示モード
            self.lst_frm.pack_forget()
        elif self.mode == 3: # 検索モード
            self.ID_or_name.delete(0, "end")
            self.search_frm.pack_forget()

        # メニューモードに初期化
        self.back_menu_btn.pack_forget()
        self.mode = 0
        self.disp_header("＜操作を選んでください＞")
        self.menu_frm.pack()
    

    def disp_header(self, txt):
        '''ヘッダーラベルに表示する(1行で済むが可読性が良くなりそうなので定義)'''
        self.header_lbl.config(text=txt)
    

    '''以下は抽象メソッド。commandメソッドは実態を持たないため、派生クラスでoverrideさせる'''
    @abstractmethod
    def register_member(self):
        raise NotImplementedError("未実装のメソッドがあります！")

    @abstractmethod
    def update_member(self):
        raise NotImplementedError("未実装のメソッドがあります！")

    @abstractmethod
    def delete_member(self):
        raise NotImplementedError("未実装のメソッドがあります！")
    
    @abstractmethod
    def show_list(self):
        raise NotImplementedError("未実装のメソッドがあります！")

    @abstractmethod
    def search_cmd(self):
        raise NotImplementedError("未実装のメソッドがあります！")

    