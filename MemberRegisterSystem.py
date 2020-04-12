# SQLite3とTreeviewによる会員登録アプリ
import SQLites                           # 自作モジュールのインポート
from AppBase import AppBase              # 基底クラスのインポート
import tkinter as tk
from tkinter import messagebox as mbox
import tkinter.ttk as ttk                # TreeviewとStyleを利用
import os                                # DBの存在を確認する
from unicodedata import east_asian_width # 文字幅判定に利用

# 基底クラスを継承した会員登録クラスを定義
class MemberRegisterApp(AppBase):
    def __init__(self, master=None):
        '''コンストラクタでDBが存在するか確認し、なければDBとテーブルを作成。
        treeviewに表示可能な文字幅も定数として定義しておく'''
        super().__init__(master)
        self.NAME_WIDTH = 30
        self.AGE_WIDTH  =  3
        self.db_name = "member_register.DB"
        if not os.path.exists(self.db_name):
            SQL = "CREATE TABLE members(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, gender STRING, age INTEGER)"
            SQLites.exec_SQL(self.db_name, SQL)
        
    
    def get_str_width(self, string):
        '''半角換算の文字列の幅を取得する。
        (treeviewでは列を横スクロールできないため、文字幅の制御が必要)
        east_asian_width(文字)で引数のカテゴリを取得し、
        マルチバイト文字(カテゴリはA,F,Wのいずれか)では文字幅は2、
        それ以外の文字では文字幅1として足し合わせ、合計の文字幅を返す
        ※判定した文字列の表示については、等幅フォントを利用することを前提とする
        ※len関数は文字幅ではなく文字数を返す関数であるため利用できない'''
        width = 0
        for letter in string:
            if east_asian_width(letter) in "AFW":
                width += 2
            else:
                width += 1
        return width
        
    def get_valid_name_and_age(self):
        '''ウィジェットが正常な値の場合は名前と年齢を取得する。
        不正な値の場合はValueError例外を投げる'''
        # エラーメッセージと判定結果のデフォルト値を定義(エラーがなければ更新されない)
        msg = ""
        judge = True
        # 判定対象をウィジェットから取得(前後のスペースを削除するためにstripを噛ませる)
        name = self.name.get().strip()
        age = self.age.get().strip()

         # 名前入力内容チェック(空白判定-->文字長判定)
        if name != "":
            if self.get_str_width(name) > self.NAME_WIDTH:
                msg += "名前が長すぎます!\n"
                judge = False
        else:
            msg += "名前が入力されていません！\n"
            judge = False

        # 年齢入力内容チェック(空白判定-->数値判定-->桁数判定)
        if age != "":
            if age.isdigit():
                age = int(age) # intで0埋め削除と半角数字変換ができる
                # ※str.lstrip("0")では0を全て削除してしまうため使用しない
                if len(str(age)) > self.AGE_WIDTH:
                    msg += "年齢の桁数が多すぎます！\n"
                    judge = False
            else:
                msg += "年齢は数字で、空白を挟まずに入力してください！\n"
                judge = False
        else:
            msg += "年齢が入力されていません！\n"
            judge = False

        # 結果が真なら情報を返し、偽なら例外を投げる
        if judge == True: # judgeだけでもいいが可読性を考慮して 
                return name, age
        elif judge == False:
            raise ValueError(msg)
    

    def get_members(self):
        '''会員がいればlistを、いなければException例外を投げる
        ※リストは[{ID, 名前, 性別, 年齢}...]で構成されている'''
        members = SQLites.get_list_table(self.db_name, "members")
        if len(members) == 0:
            raise Exception("会員は1人も登録されていません！")
        return members
    

    def search_member(self):
        '''検索ウィジェットに入力された情報を判定し、SELECT文を実行する。
        会員情報があればリストを、ないまたは1人以上ならばException例外を投げる
        ※name検索では前方一致検索なので、該当者が複数いる可能性がある。
        この場合編集対象を絞り込めないため、mboxで全該当者の情報を表示して再入力を促す'''
        # 判定対象をウィジェットから取得(前後のスペースを削除するためにstripを噛ませる)
        target = self.ID_or_name.get().strip()

        # 空白判定
        if target == "":
            raise Exception("何も入力されていません！")

        # 入力値を判定しテーブル名に続く検索条件を分岐
        table = "members"
        if target.isdigit():  # 数字ならid検索(完全一致)
            table += " WHERE id={0}".format(int(target)) # intで0埋め無し半角数字化
        else:                 # それ以外ならname検索(前方一致)
            table += " WHERE name LIKE'{0}%'".format(target)

        # 条件に一致する会員情報をリストで取得する
        member = SQLites.get_list_table(self.db_name, table)

        # 取得した会員の人数を判定し処理を分岐
        if member == []:       # 該当者なし
            raise Exception("条件に該当する会員はいません！") 
        elif len(member) > 1:  # 該当者が複数
            # memberを表示用に加工しdispとして定義。表示を「項目名：会員情報」に編集する
            item = ["ID", "氏名", "性別", "年齢"]
            disp = ((i+"："+str(j) for i,j in zip(item, data)) for data in member)
            # 表示の項目間に全角スペースを挿入。会員ごとに年齢の単位と改行を付け足す
            disp = "歳\n".join("  ".join(person_data) for person_data in disp)+"歳"
            raise Exception("会員が複数見つかりました。\n編集する会員をIDで指定してください。\n" + disp)
        else:                  # 該当者が1人 
            return member      # リストを返す
    

    def set_treeview(self):
        '''get_membersで全ての会員情報を取得しTreeviewにセットする。
        会員がいない場合はException例外が発生する'''
        members = self.get_members()
        for member in members:
            self.tree.insert("", "end", values=member)


    # 以下は抽象基底クラスのメソッドoverride
    def register_member(self):
        '''self.reg_btnの登録モードcommand(抽象メソッド)
        名前と年齢を取得するメソッドでは、値が不正な場合に例外が発生する'''
        try:
            name, age = self.get_valid_name_and_age()
            gender = self.gender_sv.get()
            SQL = "INSERT INTO members(name, gender, age) VALUES('{0}', '{1}', {2})"
            msg = f"この会員を登録しますか？\n氏名：{name}\n性別：{gender}\n年齢：{age}歳"
            if mbox.askokcancel("登録確認", msg): # OK選択ならSQLを実行 
                SQLites.exec_SQL(self.db_name, SQL.format(name, gender, age))
                mbox.showinfo("登録完了", "会員情報を登録しました。\n登録情報は会員一覧で確認できます。")
                self.clear_widgets()
        except Exception as e:
            mbox.showerror('警告', f"会員を登録できません！\n{e}")


    def update_member(self):
        '''self.reg_btnの修正モードcommand(抽象メソッド)
        名前と年齢を取得するメソッドでは、値が不正な場合に例外が発生する'''
        try:
            name, age = self.get_valid_name_and_age()
            gender = self.gender_sv.get()
            id = self.header_lbl.cget("text").split(" ")[-1] # ヘッダーのIDをcgetメソッドで取得
            SQL = "UPDATE members SET name='{0}', gender='{1}', age={2} WHERE id={3}"
            msg = f"ID：{id} の会員を修正しますか？\n氏名：{name}\n性別：{gender}\n年齢：{age}歳"
            if mbox.askokcancel("修正確認", msg): # OK選択ならSQLを実行
                SQLites.exec_SQL(self.db_name, SQL.format(name, gender, age, id))
                mbox.showinfo("修正完了", "会員情報を修正しました。\n会員情報は会員一覧で確認できます。")
                self.clear_widgets()
        except Exception as e:
            mbox.showerror('警告', f"情報を修正できません！\n{e}")


    def delete_member(self):
        '''self.del_btnのcommand(抽象メソッド)
        idは編集できず前処理で該当者が確定しているため、tryを噛ませる必要はない'''
        id = self.header_lbl.cget("text").split(" ")[-1] # ヘッダーのIDをcgetメソッドで取得
        SQL = "DELETE FROM members WHERE id={0}"
        if mbox.askokcancel("削除確認", f"ID：{id} の会員を削除しますか？"): # OK選択ならSQLを実行
            SQLites.exec_SQL(self.db_name, SQL.format(id))
            mbox.showinfo("削除完了", "会員情報を削除しました。\n会員情報は会員一覧で確認できます。")
            self.clear_widgets()
        
    
    def search_widgets(self):
        '''検索ウィジェット生成commandをoverride。
        はじめに会員情報を取得して、会員がいれば会員検索用ウィジェットを生成。
        会員がいなければ警告し、ウィジェットを生成せずメニュー表示のままにする'''
        try:
            self.get_members()
            super().search_widgets()
        except Exception as e:
            mbox.showerror('警告', e)


    def show_list(self):
        '''一覧表示ボタン(self.show_lst_btn)のcommand(抽象メソッド)
        ウィジェットを生成し、会員情報をtreeviewにセットする'''
        try:
            self.show_list_widgets()
            self.set_treeview()
        except Exception as e:
            mbox.showerror('警告', e)
            self.clear_widgets()
    

    def search_cmd(self):
        '''検索ボタン(self.search_btn)のcommand(抽象メソッド)'''
        try:
            member = self.search_member()
            mbox.showinfo("検索完了", "該当する会員を見つけました。")
            self.search_frm.pack_forget()
            self.register_widgets()
            self.disp_header(f"修正・削除する会員のID： {member[0][0]}")
            self.name.insert(0, member[0][1])
            self.gender_sv.set(member[0][2])
            self.age.insert(0, member[0][3])
        except Exception as e:
            mbox.showerror('警告', e)

    
root = tk.Tk()
root.title("会員登録フォーム")
root.geometry("345x275+500+200")
app = MemberRegisterApp(root)
app.mainloop()

'''
今後の課題
・modeを数字にしているのがわかりにくい。
・抽象基底クラスやインターフェイスをもっと知りたい。
・GitHubやTortoiseGitでのバージョン管理をマスターしたい。
　→まずはブランチの理解と、プル・プッシュ・マージなどの基本操作を覚える。
　→(4/12)remoteブランチにpushしたつもりがmasterに入ってたので、この行の追加がどこに入るかpushしてみる。
   TortoiseGitをいろいろいじって、やっとリモートブランチとローカルブランチが理解できた気がする。
'''