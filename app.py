from flask import Flask, render_template, request,Response
import pymysql
import csv
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # 获取用户填写的数据
    year = request.form['year']
    education = request.form['education']
    politics = request.form['politics']
    level = request.form['level']
    work_years = request.form['work_years']
    location = request.form['location']
    major = request.form['major']

    # 构建查询条件.如果条件不为空，就将其添加到查询条件中
    filters = {}
    # if year:
    #     filters['年份'] = year
    if education:
        filters['学历'] = education
    if politics:
        filters['政治面貌'] = politics
    if level:
        filters['机构层级'] = level
    if work_years:
        filters['基层工作最低年限'] = work_years
    # if location:
    #     filters['location'] = location
    # if major:
    #     filters['major'] = major
    print(filters)
    results=query_databases(filters,year,location,major)

    # 将结果传递给 result.html 文件并以表格形式显示
    return render_template('result.html', results=results)

def query_databases(filters,year,location,major):
    # 连接数据库
    conn = pymysql.connect(host="localhost", user="root", password="root", database="gkzw")
    cursor = conn.cursor()
    # 构建 SQL 查询语句
    table_name='sheets'+year

    # 构建基本的查询语句
    sql = "SELECT * FROM "+table_name+" WHERE 1=1"

    # 添加条件到查询语句
    for key, value in filters.items():
        sql += f" AND {key} = '{value}' "
    if location:
        location=location[:2]
        sql += f" AND 工作地点 like '%{location}%' "
    if major:
        sql += f" AND 专业 like '%{major}%' "
    print(sql)

    # 执行查询
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.commit()
    cursor.close()
    # 关闭数据库连接
    conn.close()
    return results


@app.route('/download', methods=['POST'])
def download():
    results = request.form.getlist('results')

    # 生成CSV数据
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    csv_writer.writerow(['序号','部门代码','部门名称','用人司局','机构性质','招考职位','职位属性','职位分布','职位简介','职位代码','机构层级','考试类别','招考人数','专业','学历',
     '学位','政治面貌','基层工作最低年限','服务基层项目工作经历','是否在面试阶段组织专业能力','面试人员比例','工作地点','落户地点'])  # 列名
    for result in results:
        csv_writer.writerow(result.split(','))  # 假设结果是以逗号分隔的字符串

    # 返回CSV文件供用户下载
    response = Response(
        csv_data.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=results.csv'}
    )

    return response
if __name__ == '__main__':
    app.run(debug=True)
