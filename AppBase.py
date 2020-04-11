# MemberRegisterSystemのコードが長くなってきたので、AppBaseを分割
# 継承させるソースファイル内では、始めに以下のように宣言すればOK
# from ソースファイル名 import クラス名

import tkinter as tk
from tkinter import messagebox as mbox
import tkinter.ttk as ttk              # Treeviewを利用

# 基底クラス
class AppBase(tk.Frame):
    def __init__(self, master=None):
        ''' コンストラクタ
        メニューの展開先をモードで管理し、実行後forgetするウィジェットを管理
        0->メニュー, 1->登録, 2->一覧表示, 3->修正, 4->削除 として分岐させる '''
        super().__init__(master)
        self.mode = 0
        self.header_lbl = tk.Label(self,text="操作を選んでください")
        self.header_lbl.pack()
        self.menu_widgets()
        self.pack()
        #各モードからメニューへ戻るボタンを定義
        self.back_menu_btn = tk.Button(self, text="メニューに戻る", command=self.clear_widgets)
    
    def menu_widgets(self):
        ''' メニューウィジェット(他フォーム展開時に閉じる)
            呼び出すと各メニューへ展開するボタンが表示される '''
        self.menu_frm = tk.Frame(self)
        self.menu_frm.pack()
        self.register_btn = tk.Button(self.menu_frm, text="会員\n登録", command=self.register_widgets)
        self.register_btn.pack(side="left")
        self.show_lst_btn = tk.Button(self.menu_frm, text="会員\n一覧", command=self.show_list)
        self.show_lst_btn.pack(side="left")
        self.fix_del_btn =  tk.Button(self.menu_frm, text="情報\n修正", command=self.fix_del_widgets)
        self.fix_del_btn.pack(side="left")

    def register_widgets(self):
        ''' 登録・修正用ウィジェット
        登録時はメニューから展開されるが、
        修正時はmode=3でfix_del_widgetsから展開するため、
        menu_frmのforgetはモードで分岐させ、エラーにさせないようにする '''
        self.reg_frm = tk.Frame(self)
        self.reg_frm.pack()
        self.reg_btn = tk.Button(self.reg_frm) # configするので先に定義
        if self.mode == 0:              # メニューから直展開なら
            self.menu_frm.pack_forget() # メニューを隠す
            self.disp_header("会員情報を入力してください")
            self.reg_btn.config(text="登録する", command=self.register_member)
            self.mode = 1
        else:
            self.reg_btn.config(text="修正する", command=self.update_member)
            self.del_btn = tk.Button(self.reg_frm, text="削除する", command=self.delete_member)
            self.del_btn.pack()
            self.mode = 4 
        tk.Label(self.reg_frm, text="名前").pack()
        self.name = tk.Entry(self.reg_frm)
        self.name.pack()
        tk.Label(self.reg_frm, text="性別").pack()
        gender_frm = tk.Frame(self.reg_frm)
        genders = ["男性", "女性", "その他"]
        self.gender_sv = tk.StringVar()
        self.gender_sv.set(genders[0])
        for gender in genders:
            rb = tk.Radiobutton(gender_frm, value= gender, text=gender, variable=self.gender_sv)
            rb.pack(side="left")
        gender_frm.pack()
        tk.Label(self.reg_frm, text="年齢").pack()
        self.age = tk.Entry(self.reg_frm)
        self.age.pack()
        self.reg_btn.pack()
        self.back_menu_btn.pack()

    def show_list_widgets(self):
        '''一覧表示用ウィジェット(登録が1件でもあれば表示可能)'''
        self.disp_header("会員一覧")
        self.menu_frm.pack_forget()
        self.mode = 2
        self.lst_frm = tk.Frame(self)
        self.lst_frm.pack()
        #　treeviewの表示内容をセット
        self.tree = ttk.Treeview(self.lst_frm)
        self.tree["column"] = (1, 2, 3, 4)
        self.tree["show"] = "headings"
        self.tree.heading(1, text="ID")
        self.tree.heading(2, text="名前")
        self.tree.heading(3, text="性別")
        self.tree.heading(4, text="年齢")
        self.tree.column(1, width=40)
        self.tree.column(2, width=190)
        self.tree.column(3, width=40)
        self.tree.column(4, width=40)
        self.tree.pack()
        self.back_menu_btn.pack()

    def fix_del_widgets(self):
        ''' 修正・削除用ウィジェット(IDか氏名入力後に登録用ウィジェットを呼び出す)'''
        self.disp_header("修正・削除したい会員の\nIDか氏名を入力してください")
        self.menu_frm.pack_forget()
        self.mode = 3
        self.fix_del_frm = tk.Frame(self)
        self.fix_del_frm.pack()
        self.ID_or_name = tk.Entry(self.fix_del_frm)
        self.ID_or_name.pack()
        self.search_btn = tk.Button(self.fix_del_frm, text="会員を検索",command=self.search_cmd)
        self.search_btn.pack()
        self.back_menu_btn.pack()
    
    def clear_widgets(self):
        ''' 処理後にウィジェットを初期化するメソッド'''
        if self.mode == 3:
            self.ID_or_name.delete(0, "end")
            self.fix_del_frm.pack_forget()
            #return # 修正なら以降の処理はしない
        elif self.mode == 2:
            self.lst_frm.pack_forget()
        elif self.mode == 1 or 4:
            self.name.delete(0, "end")
            self.age.delete(0, "end")
            self.reg_frm.pack_forget()
            if  self.mode == 4:
                self.del_btn.pack_forget() # ここで行けるか
        self.back_menu_btn.pack_forget()
        self.mode = 0 # モードを0に初期化
        self.disp_header("操作を選んでください")
        self.menu_frm.pack()
    
    def disp_header(self, txt):
        '''ヘッダーラベルに表示するメソッド(1行で済むが可読性が良くなりそうなので定義)'''
        #self.header_lbl.delete(0, "end") # Entryにしか
        #self.header_lbl.insert(text=txt) # delete,insertは使えんぞ
        self.header_lbl.config(text=txt)
    
    # 以下のメソッドは継承先での実装を前提としている
    def register_member(self):
        '''基底クラスでは実態を持たないため派生クラスでoverrideすること'''
        pass

    def update_member(self):
        '''基底クラスでは実態を持たないため派生クラスでoverrideすること'''
        pass

    def delete_member(self):
        '''基底クラスでは実態を持たないため派生クラスでoverrideすること'''
        pass
    
    def show_list(self):
        '''基底クラスでは実態を持たないため派生クラスでoverrideすること'''
        pass

    def search_cmd(self):
        '''基底クラスでは実態を持たないため派生クラスでoverrideすること'''
        pass

    