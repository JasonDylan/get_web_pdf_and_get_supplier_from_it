import mysql.connector
import pandas as pd
import random
# 连接到MySQL数据库
import math 
 
# 执行查询语句
for i in range(2, 11):
    conn = mysql.connector.connect(
        host="192.168.2.108",
        user="tingsen",
        password="tingsen_1017",
        database="visualization"
    )
    date = '2023-'+str(i).zfill(2)

    sql = f"SELECT date, count, category FROM tb_chart_category_product_count_us where date = '{date}'"
    cursor = conn.cursor()
    cursor.execute(sql)
    
    # 获取查询结果
    result = cursor.fetchall()
    
    # 关闭游标和连接
    cursor.close()
    conn.close()



    conn = mysql.connector.connect(
        host="192.168.2.108",
        user="tingsen",
        password="tingsen_1017",
        database="visualization"
    )
    # 遍历查询结果
    for row in result:
        date = row[0]
        count = row[1]
        category = row[2]
        
        # 计算新的Count值
        # 计算波动范围
        # fluctuation = count * random.uniform(-0.01, 0.01)
        # print(fluctuation)
        
        # 计算新的Count值
        new_count = int(math.log(count))

        print(f"{new_count=}")
        # 更新数据表
        date = '2023-'+str(i).zfill(2)
        update_sql = f"UPDATE tb_chart_category_product_count_us SET count = {new_count} WHERE date = '{date}' AND category = '{category}'"
        cursor = conn.cursor()
        cursor.execute(update_sql)
        conn.commit()
        cursor.close()

    # 关闭连接
    conn.close()

