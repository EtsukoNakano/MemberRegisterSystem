import sqlite3
import os

def db_exist_check(str_db_name):
    """ paramで指定したDBが存在するかチェックし、
    DBがあればTrue、なければFalseを返す """
    if os.path.exists(str_db_name):
        return True
    else:
        return False


def exec_SQL(str_db_name, SQL):
    """ paramのSQLを実行し指定したDBを編集する """    
    con = sqlite3.connect(str_db_name)
    cur = con.cursor()
    cur.execute(SQL)
    con.commit()
    cur.close()
    con.close()

def get_table_list(str_db_name, str_table_name):
    """ SELECT文を実行しテーブルの全列、全行分のlistを返す(行情報がtupleで括られる)
    paramのテーブル名に続けてWHERE句を記述し、検索条件を付与することもできる """
    con = sqlite3.connect(str_db_name)
    cur = con.cursor()
    cur.execute("SELECT * FROM {0}".format(str_table_name))
    lst = cur.fetchall() 
    # WHERE句を付けて実行した場合、該当なしなら[]が返る 
    # ※1行分のデータのみ取得するfetchoneならNoneが返る
    cur.close()
    con.close()
    return lst

#def count_record(str_db_name, str_table_name):
    '''SELECT文を実行し、テーブルのレコード数を返す
    paramのテーブル名に続けてWHERE句を記述し、検索条件を付与することもできる'''
    '''con = sqlite3.connect(str_db_name)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM {0}".format(str_table_name))
    cnt = cur.fetchone()
    cur.close()
    con.close()
    mbox.showinfo("", cnt)
    return sum(cnt)
    # 返り値がおかしいのと、先にリストを取得してlenすれば済むので廃止
    # =>DBへのアクセス回数が減って処理高速化＆安全
    '''