# SQLite3による会員登録システム
import SQLites              # 自作モジュールのインポート
from AppBase import AppBase # 基底クラスのインポート
import tkinter as tk
from tkinter import messagebox as mbox
import tkinter.ttk as ttk   # Treeviewを利用
import traceback
from unicodedata import east_asian_width # 文字幅判定に利用

# 基底クラスを継承した会員登録クラスを定義
class MemberRegisterApp(AppBase):
    def __init__(self, master=None):
        '''コンストラクタでDBが存在するか確認し、なければDBとテーブルを作成。
        treeviewに表示可能な文字幅も定数として定義しておく'''
        super().__init__(master)
        self.db_name = "member_register.DB"
        if not SQLites.db_exist_check(self.db_name):
            SQL = "CREATE TABLE members(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, gender STRING, age INTEGER)"
            SQLites.exec_SQL(self.db_name, SQL)
        else:
            pass
        self.NAME_WIDTH = 30
        self.AGE_WIDTH  =  3
    
    def get_str_width(self, string):
        '''半角換算の文字列の幅を取得する
        (lenは文字数の取得なので、マルチバイト文字の幅を考慮できない)
        east_asian_width(文字)で引数のカテゴリを取得し、
        マルチバイト文字(カテゴリはA,F,Wのいずれか)では文字幅は2、
        それ以外の文字では文字幅1として足し合わせ、合計の文字幅を返す
        内部関数を定義し、引数の文字列をリスト化して内包表記で内部関数を噛ませる。
        内包表記で得られたリストはsumすることで、全体の文字幅を得ることができる。
        ※treeviewでは列を横スクロールできないため制御が必要'''
        def counter(string):
            count = 0
            for letter in string:
                if east_asian_width(letter) in "AFW":
                    count += 2
                else:
                    count += 1
                return count
        width = sum([counter(i) for i in list(string)])
        return width

    def get_valid_name_and_age(self):
        '''ウィジェットが正常な値の場合は名前と年齢を取得する。
        不正な値の場合はValueError例外を投げる'''
        # エラーメッセージと判定結果のデフォルト値を定義
        msg = ""
        judge = True
        # 名前は先に前後のスペースを削除するためにstripを噛ませる
        name = self.name.get().strip()
        age = self.age.get()
         # 名前入力内容確認
        if bool(name):
            if self.get_str_width(name) > self.NAME_WIDTH:
                msg += "名前が長すぎます!\n"
                judge = False
        else:
            msg += "名前が入力されていません！\n"
            judge = False

        # 年齢入力内容確認
        if bool(age):
            if age.isdigit(): # 数字確認
                age = int(age)
                '''年齢の0埋めを削除するためにintを噛ませる
                ※str.lstrip("0")では0を全て削除してしまうため使わない
                また、intでは全角数字を半角数字にできる利点もある'''
                if len(str(age)) > self.AGE_WIDTH:
                    msg += "年齢の桁数が多すぎます！\n"
                    judge = False
            else:
                msg += "年齢が数字ではありません！"
                judge = False
        else:
            msg += "年齢が入力されていません！\n"
            judge = False

        if judge == True: # judgeだけでもいいが可読性を考慮して 
                return name, age
        elif judge == False:
            raise ValueError(msg)
        """#以下はエラーメッセージを全て反映できないので不採用
        name = self.name.get()
        age = self.age.get()
        if all((name, age)):      # 入力漏れ確認
            if not age.isdigit(): # 数字確認
                mbox.showerror("エラー", "年齢が不正です！")
                raise ValueError("年齢が不正です！")
            else:
                age = int(age)
                '''年齢の0埋めを削除するためにintを噛ませる
                ※str.lstrip("0")では0を全て削除してしまうため使わない
                また、intでは全角数字を半角数字にできる利点もある'''
                return name, age
        else:
            #mbox.showerror("エラー", "入力漏れがあります！")
            raise ValueError("入力漏れがあります！")"""

    def register_member(self):
        try:
            name, age = self.get_valid_name_and_age()
            gender = self.gender_sv.get()
            SQL = "INSERT INTO members(name, gender, age) VALUES('{0}', '{1}', {2})"
            msg = f"この会員を登録しますか？\n氏名：{name}\n性別：{gender}\n年齢：{age}歳"
            if not mbox.askokcancel("登録確認", msg): # 
                return
            SQLites.exec_SQL(self.db_name, SQL.format(name, gender, age))
            mbox.showinfo("登録完了", "会員情報を登録しました。\n登録情報は会員一覧で確認できます。")
            self.clear_widgets()
        except Exception as e:
            mbox.showerror('エラー', f"登録できませんでした。\n<エラー内容>\n{e}")
            # traceback.print_exc()

    def update_member(self):
        ''' self.reg_btnの修正command用メソッド '''
        try:
            name, age = self.get_valid_name_and_age()
            gender = self.gender_sv.get()
            # header_lblのtextに代入されたIDをcgetメソッドで取得する
            id = self.header_lbl.cget("text").split(" ")[-1]
            SQL = "UPDATE members SET name='{0}', gender='{1}', age={2} WHERE id={3}"
            msg = f"ID：{id} の会員を修正しますか？\n氏名：{name}\n性別：{gender}\n年齢：{age}歳"
            if not mbox.askokcancel("修正確認", msg):
                return
            SQLites.exec_SQL(self.db_name, SQL.format(name, gender, age, id))
            mbox.showinfo("修正完了", "会員情報を修正しました。\n会員情報は会員一覧で確認できます。")
            self.clear_widgets()
        except Exception as e:
            mbox.showerror('エラー', f"登録できませんでした。\n<エラー内容>\n{e}")
            # traceback.print_exc()

    def delete_member(self):
        ''' self.del_btnの修正command用メソッド '''
        # header_lblのtextに代入されたIDをcgetメソッドで取得する
        id = self.header_lbl.cget("text").split(" ")[-1]
        SQL = "DELETE FROM members WHERE id={0}"
        if not mbox.askokcancel("削除確認", f"ID：{id} の会員を削除しますか？"):
            return
        SQLites.exec_SQL(self.db_name, SQL.format(id))
        mbox.showinfo("削除完了", "会員情報を削除しました。\n会員情報は会員一覧で確認できます。")
        self.clear_widgets()
    
    def get_members(self):
    #def exist_member(self):
        '''会員がいればlistを、いなければException例外を投げる
        旧仕様：会員がいればlistを、いなければメッセージを表示しFalseを返す
        ※会員がいる場合も同じbool型のTrueを返すべきである
        　(他言語では返り値の型が異なるのは許されないことが多く可読性も欠くためよろしくない)'''
        members = SQLites.get_table_list(self.db_name, "members")
        if len(members) == 0:
            #mbox.showerror("エラー", "会員は1人も登録されていません！")
            #self.clear_widgets()
            #return False
            raise Exception("会員は1人も登録されていません！")
        return members
        
    def fix_del_widgets(self):
        '''override
        widget生成前に会員がいるか判定し、いなければメニューに戻る'''
        #if not bool(self.exist_member()):#会員がいないとき
            #return # 何も処理しない
        try:
            self.get_members() #会員がいなければ例外になる
            super().fix_del_widgets()
        except Exception as e:
            mbox.showerror('エラー', e)
    
    def set_treeview(self):
        ''' 全ての会員情報を取得しTreeviewにセットする
        会員がいない場合はセットしない'''
        members = self.get_members()
        '''if bool(members):
            for member in members:
                self.tree.insert("", "end", values=member)'''
        for member in members:
            self.tree.insert("", "end", values=member)
                    
    def show_list(self):
        ''' 一覧表示ボタン(self.show_lst_btn)のcommand '''
        try:
            self.show_list_widgets()
            self.set_treeview()
        except Exception as e:
            mbox.showerror('エラー', e)
            self.clear_widgets()
    
    def search_member(self):
        ''' 修正ウィジェットに入力された情報を判定し、SELECT文を実行する
        会員情報があればリストを、ないまたは1人以上ならばfalseを返す '''
        target = self.ID_or_name.get()
        if target == "":
            mbox.showerror("エラー", "何も入力されていません！")
            return False
        table = "members"
        if target.isdigit():  # 数字ならid検索
            table += " WHERE id={0}".format(target)
        else:                 # それ以外ならname(前方一致)検索
            table += " WHERE name LIKE'{0}%'".format(target)
        # name検索では複数一致の可能性がある。mboxで全該当者を表示して再入力を促す
        member = SQLites.get_table_list(self.db_name, table)
        if member == []:      # 検索結果が該当者なしなら
            mbox.showerror("エラー", "条件に該当する会員はいません！")
            return False
        elif len(member) > 1: # 検索結果が1人以上なら
            # 以下はmemberを表示用に加工。ややこしいのでdispとする
            status = ["ID", "氏名", "性別", "年齢"]
            disp = ((i+"："+str(j) for i,j in zip(status, data)) for data in member)
            disp = "歳\n".join("  ".join(person_data) for person_data in disp)+"歳"
            mbox.showerror("エラー", "会員が複数見つかりました\n誰を編集するかIDで指定してください\n" + disp)
            return False
        else: # 会員が一人だけ見つかった場合 
            return member # 該当者1人のリストを返す
    
    def search_cmd(self):
        ''' 検索ボタン(self.search_btn)のcommand用メソッド '''
        member = self.search_member()
        if not member: # 返り値が偽なら中断
            return
        mbox.showinfo("検索完了", "該当する会員を見つけました。")
        self.fix_del_frm.pack_forget()
        self.register_widgets()
        self.disp_header(f"修正・削除する会員のID： {member[0][0]}")
        '''続けて転記処理を記述すること！'''
        self.name.insert(0, member[0][1])
        self.gender_sv.set(member[0][2])
        self.age.insert(0, member[0][3])

    #def set_command(self):
        '''ボタンにcommandをセットするメソッド
        以下の問題から実装を廃止した
        1．ウィジェットがpackされた後しかconfigできない
        2．ウィジェット再生成されると再セットが必要
        　※AppBaseでも再生成してる箇所がないか監視する必要がある
        ->代わりに基底クラスで空のメソッドをcommandに持たせ、実装は派生クラスで行うことにした。
        ''' 
    
root = tk.Tk()
root.title("会員登録フォーム")
app = MemberRegisterApp(root)
app.mainloop()


'''
現行の問題点
・del_btnがパックされない
'''