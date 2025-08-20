import sqlite3
import os
import hashlib
from datetime import datetime

def hash_password(password, secret_key='rank_system_secret_key'):
    """使用MD5哈希密码"""
    return hashlib.md5((secret_key + password).encode('utf-8')).hexdigest()

def migrate_data():
    """将scores_2020.db中的数据迁移到data.db中"""
    # 源数据库和目标数据库的路径
    source_db_path = 'scores/2020/scores_2020.db'
    target_db_path = 'scores/2025/data.db'
    
    # 检查数据库文件是否存在
    if not os.path.exists(source_db_path):
        print(f"源数据库文件不存在: {source_db_path}")
        return
    
    if not os.path.exists(target_db_path):
        print(f"目标数据库文件不存在: {target_db_path}")
        return
    
    try:
        # 连接源数据库
        source_conn = sqlite3.connect(source_db_path)
        source_cursor = source_conn.cursor()
        
        # 连接目标数据库
        target_conn = sqlite3.connect(target_db_path)
        target_cursor = target_conn.cursor()
        
        # 从源数据库获取所有用户数据
        source_cursor.execute("SELECT * FROM user")
        users = source_cursor.fetchall()
        
        print(f"从源数据库中读取了 {len(users)} 条记录")
        
        # 获取源数据库的列名
        source_cursor.execute("PRAGMA table_info(user)")
        source_columns = [col[1] for col in source_cursor.fetchall()]
        
        # 获取目标数据库的列名
        target_cursor.execute("PRAGMA table_info(user)")
        target_columns = [col[1] for col in target_cursor.fetchall()]
        
        # 检查目标数据库中是否已存在相同的记录
        existing_users = set()
        target_cursor.execute("SELECT kaohao FROM user")
        for row in target_cursor.fetchall():
            existing_users.add(row[0])
        
        print(f"目标数据库中已有 {len(existing_users)} 条记录")
        
        # 准备插入语句
        insert_sql = f"""
        INSERT INTO user (
            kaohao, password, college, major, 
            subject1_code, subject1_score, 
            subject2_code, subject2_score, 
            subject3_code, subject3_score, 
            subject4_code, subject4_score, 
            net_score, total_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 开始迁移数据
        migrated_count = 0
        skipped_count = 0
        
        for user in users:
            kaohao = user[0]
            
            # 如果用户已存在于目标数据库，则跳过
            if kaohao in existing_users:
                skipped_count += 1
                continue
            
            # 为用户生成密码（使用准考证号后6位）
            password = hash_password(kaohao[-6:])
            
            # 准备插入的数据
            # 注意：索引1是password，但源数据库没有这一列，所以我们需要插入它
            insert_data = [
                kaohao,          # kaohao
                password,        # password (新增)
                user[1],         # college
                user[2],         # major
                user[3],         # subject1_code
                user[4],         # subject1_score
                user[5],         # subject2_code
                user[6],         # subject2_score
                user[7],         # subject3_code
                user[8],         # subject3_score
                user[9],         # subject4_code
                user[10],        # subject4_score
                user[11],        # net_score
                user[12]         # total_score
            ]
            
            # 执行插入
            target_cursor.execute(insert_sql, insert_data)
            migrated_count += 1
            
            # 每100条记录提交一次，以避免事务过大
            if migrated_count % 100 == 0:
                target_conn.commit()
                print(f"已迁移 {migrated_count} 条记录...")
        
        # 提交剩余的事务
        target_conn.commit()
        
        print(f"\n迁移完成!")
        print(f"总记录数: {len(users)}")
        print(f"成功迁移: {migrated_count}")
        print(f"已跳过(已存在): {skipped_count}")
        
        # 关闭连接
        source_conn.close()
        target_conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    print(f"开始数据迁移 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    migrate_data()
    print(f"迁移结束 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")