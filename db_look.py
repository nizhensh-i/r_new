import sqlite3
import os

def print_db_structure(db_path):
    """打印SQLite数据库的结构"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n数据库 {db_path} 的结构:")
        print("=" * 50)
        
        for table in tables:
            table_name = table[0]
            print(f"\n表名: {table_name}")
            print("-" * 30)
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("列名\t\t类型\t\t可空\t\t主键")
            print("-" * 50)
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"{col_name}\t\t{col_type}\t\t{'否' if not_null else '是'}\t\t{'是' if pk else '否'}")
            
            # 获取表中的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n表 {table_name} 中有 {count} 条记录")
            
            # 如果记录数不为0，显示一条示例记录
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
                print(f"示例记录: {sample}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite错误: {e}")

if __name__ == "__main__":
    # 查看源数据库结构
    print_db_structure("scores/2020/scores_2020.db")
    
    # 查看目标数据库结构
    print_db_structure("scores/2025/data.db")