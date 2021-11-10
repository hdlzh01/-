import matplotlib.pyplot as plt
import numpy as np
import random
import easygui as g
from flask import Flask
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D


# encoding:utf-8
import pymysql
from matplotlib.pyplot import MultipleLocator
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.dates as mdate
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import requests, re
import json
plt.rcParams['font.sans-serif']=['SimHei'] 
plt.rcParams['axes.unicode_minus']=False  






def query_data():
    while(1):
        msg = '请选择查询方式'
        title = '历史天气查询'
        query_method = g.choicebox(msg, title=title, choices=['1.选项查询', '2.自定义查询'])
        if query_method is None:
            return
        try:
            conn = pymysql.connect(
                host='localhost', 
                user='root',password='38324hhh',
                database='test1',
                charset='utf8')
        except Exception as e:
            g.msgbox(msg="connect mysql error.",title="提示",ok_button="返回")
            return


        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        if query_method == '2.自定义查询':
            while(1):
                sql = g.enterbox(msg="请输入查询语句",title="历史天气查询")
                if sql is None:
                    cursor.close()
                    break
                try:
                    cursor.execute(sql)
                    ret1 = cursor.fetchall()
                    df = pd.DataFrame(ret1)
                    print(df)
                except Exception as e:
                    g.msgbox(msg=e,title=sql,ok_button="返回")
            
            cursor.close()
            

        else:
            sql = 'select province from weather group by province'
            cursor.execute(sql)
            ret1 = cursor.fetchall()  
            cursor.close ()
            pro_list = []
            for i in range(len(ret1)):
                pro_list.append(ret1[i]['province'])

            province_query, city_query = '1', '1'
            while(1):
                msg = "请选择查询的省份"
                title1 = "历史天气查询"
                choicess_list = pro_list
                province_query = g.choicebox(msg, title=title1, choices=choicess_list)

                if province_query is None:
                    break
                cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
                sql = 'select city from weather where province=%s group by city'
                cursor.execute(sql, [province_query])
                ret1 = cursor.fetchall()  
                c_list = []
                for i in range(len(ret1)):
                    c_list.append(ret1[i]['city'])
                cursor.close ()

                while (1):
                    msg = "请选择查询的城市"
                    title = province_query + "历史天气查询"
                    choicess_list = c_list
                    city_query = g.choicebox(msg, title=title, choices=choicess_list)
                    if city_query is None:
                        break
            
                    while(1):
                        msg = "请选择查询的年份"
                        title = city_query + "历史天气查询"
                        choicess_list = [2016,2017,2018,2019]
                        year_query = g.choicebox(msg, title = title, choices=choicess_list)
                        if year_query is None:
                            break
            
                        msg = "请选择查询的月份"
                        title = city_query + "历史天气查询"
                        choicess_list = list(range(1,13))
                        month_query = g.choicebox(msg, title= title, choices=choicess_list)
                        if month_query is not None:
                            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
                            sql = 'select * from weather where city=%s and year(day_)=%s and month(day_)=%s'
                            cursor.execute(sql, [city_query,year_query,month_query])
                            ret1 = cursor.fetchall()
                            res = pd.DataFrame(ret1) 
                            cursor.close()
                            print(res)
                            break


        


def get_insert_data(year_, month_):
    dataset = []
    url_ = 'https://www.tianqi.com/'
    cbooo_api = url_                       
    headers = {"User-Agent": UserAgent(verify_ssl=False).random}
    response_comment = requests.get(cbooo_api, headers=headers)
    response_comment.encoding = response_comment.apparent_encoding

    rows = response_comment.text
    province_list = re.findall(r'<a href="https://www.tianqi.com/(.*?)" target="_blank" title="', rows)[2:-3]


    for k in range(len(province_list)):
        cbooo_api = url_ + province_list[k]
        headers = {"User-Agent": UserAgent(verify_ssl=False).random}
        response_comment = requests.get(cbooo_api, headers=headers)
        response_comment.encoding = response_comment.apparent_encoding
        row = response_comment.text

        province_ = re.findall(r'<div class="tit02"><h2>(.*?)主要', row)
        if k <= 3:
            city_list = ['/' + province_list[k]]
        else:
            city_list = re.findall(r'li><b><a href="(.*?)" title="', row)
            town_list = re.findall(r'<a href="(.*?)天气预报" target="', row)

            for p in range(len(town_list)):
                town_list[p] = re.findall(r'(.*?)" title=', town_list[p])[0]

            for p in range(0, len(town_list), 4):
                if town_list[p] not in city_list:
                    city_list.append(town_list[p])

   
        for i in range(len(city_list)):
            cbooo_api = 'http://lishi.tianqi.com' + city_list[i] + year_ + month_ +'.html'
            headers = {"User-Agent": UserAgent(verify_ssl=False).random}
            response_comment = requests.get(cbooo_api, headers=headers)
            response_comment.encoding = response_comment.apparent_encoding
            rows = response_comment.text
    
            city_ = re.findall(r'<title>(.*?)月份天气', rows)
            date_ = re.findall(r'<div class="th150">(.*?) </div>', rows)
            weather_ = re.findall(r'<div class="th120">(.*?)</div>', rows)
            wind_ = re.findall(r'<div class="th100">(.*?)</div>', rows)[1:]
            polution_ = re.findall(r'<span style="color:(.*?)</span></div>', rows)
            for t in range(len(polution_)):
                polution_[t] = polution_[t][10:]

            for t in range(len(weather_)):
                if weather_[t] == '':
                    weather_[t] = 'null'

            day_, week_ = [], []
            wind1_, wind2_ = [], []
            high_tem, low_tem, desc_ = [], [], []
            for t in range(3, len(weather_), 3):
                high_tem.append(weather_[t][0:-1])
                low_tem.append(weather_[t+1][0:-1])
                desc_.append(weather_[t+2])
    

            if len(date_) == 0:
                date_ = re.findall(r'<div class="th200">(.*?) </div>', rows)
                weather_ = re.findall(r'<div class="th140">(.*?)</div>', rows)
                for j in range(len(weather_)):
                    if weather_[j] == '':
                        weather_[j] = 'null'

                for j in range(4, len(weather_), 4):
                    high_tem.append(weather_[j][0:-1])
                    low_tem.append(weather_[j+1][0:-1])
                    desc_.append(weather_[j+2])
                    wind_.append(weather_[j+3])

            for t in range(len(date_)):
                day_.append(date_[t][0:-4])
                week_.append(date_[t][-3:])
                if wind_[t] == 'null':
                    wind1_.append('null')
                    wind2_.append('null')
                else:
                    wind1_.append(wind_[t][0:-3])
                    wind2_.append(wind_[t][-2:])

            for t in range(len(day_)):
                if len(polution_) > 0:
                    tup = (province_[0], city_[0][0:-1], day_[t], week_[t], high_tem[t], low_tem[t], desc_[t], wind1_[t], wind2_[t], polution_[t])
                else:
                    tup = (province_[0], city_[0][0:-1], day_[t], week_[t], high_tem[t], low_tem[t], desc_[t], wind1_[t], wind2_[t], 'null')
                dataset.append(tup) 

    try:
        conn = pymysql.connect(
            host='localhost', 
            user='root',password='38324hhh',
            database='test1',
            charset='utf8')
    except Exception as e:
        g.msgbox(msg="connect mysql error.",title="提示",ok_button="返回")
        return       

    cursor = conn.cursor()
    sql = 'insert into weather(province, city, day_, week_, high_tem, low_tem, weather_, wind_direction, wind_, air_polution)\
         values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
    try:
        cursor.executemany(sql, dataset)
        conn.commit()
    except Exception as e:
        cursor.rollback()
        print(e)
        print(sql)
    
    cursor.close()
    conn.close()






def post_data():
    try:
        conn = pymysql.connect(
            host='localhost', 
            user='root',password='38324hhh',
            database='test1',
            charset='utf8')
    except Exception as e:
        g.msgbox(msg="connect mysql error.",title="提示",ok_button="返回")
        return

    year_, month_ = '00', '00'
    while (1):
        msg1 = "请选择要抓取的年份"
        title1 = "抓取历史天气数据"
        choicess_list = ['2016', '2017', '2018', '2019']
        year_ = g.choicebox(msg1, title=title1, choices=choicess_list)
        if year_ is None:
            break

        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = 'select distinct month(day_) from weather where year(day_)=%s'
        cursor.execute(sql,[year_])
        ret1 = cursor.fetchall()
        cur_month = pd.DataFrame(ret1).values
        choicess_list, tmp = [], []
        cursor.close()
        conn.close()
        for i in range(len(cur_month)):
            tmp.append(cur_month[i][0])

        L = ['01','02','03','04','05','06','07','08','09','10','11','12']
        for i in range(len(L)):
            if int(L[i]) not in tmp:
                choicess_list.append(L[i])

        if len(choicess_list) == 0:
            g.msgbox(msg="该年所有月份均已经抓取，请选择其他年份！",title="提示",ok_button="返回")
    
        else:
            msg2 = "请选择要抓取的月份"
            month_ = g.choicebox(msg2, title=title1, choices=choicess_list)
            if month_ is not None:
                get_insert_data(year_, month_)






def show():
    while(1):
        msg = "请填写一下需要查询的城市(其中带*号的项为必填项)"
        title = "城市天气绘图"
        fieldNames = ["*年份","*月份","*城市1","城市2","城市3","城市4"]
        fieldValues = []
        fieldValues = g.multenterbox(msg,title,fieldNames)

        while True:
            if fieldValues == None :
                break
            errmsg = ""
            for i in range(len(fieldNames)):
                option = fieldNames[i].strip()
                if fieldValues[i].strip() == "" and option[0] == "*":
                    errmsg += ("【%s】为必填项   " %fieldNames[i])
            if errmsg == "":
                break
            fieldValues = g.multenterbox(errmsg,title,fieldNames,fieldValues)
        if fieldValues is None:
            break
        if fieldValues[0] not in ['2016','2017','2018','2019']:
            g.msgbox(msg="年份输入错误",title="提示",ok_button="返回")
            continue
        elif fieldValues[1] not in ['1','2','3','4','5','6','7','8','9','10','11','12']:
            g.msgbox(msg="月份输入错误",title="提示",ok_button="返回")
            continue
    
        while '' in fieldValues:
            fieldValues.remove('')
        
        n = len(fieldValues) - 2
        try:
            conn = pymysql.connect(
                host='localhost', 
                user='root',password='38324hhh',
                database='test1',
                charset='utf8')
        except Exception as e:
            g.msgbox(msg="connect mysql error.",title="提示",ok_button="返回")
            continue
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)


        name_list, num1_list, num2_list = [], [], []
        rain_list, sun_list, cloud_list, other_list = [],[],[],[]
        for i in range(n):
            city_ = fieldValues[i+2]
            year_ = int(fieldValues[0])
            month_ = int(fieldValues[1])
            sql = 'select * from weather where city =%s and year(day_)=%s and month(day_) = %s'

            cursor.execute(sql, [city_, year_, month_])
            ret1 = cursor.fetchall()  
            df = pd.DataFrame(ret1)
            if len(df) == 0:
                g.msgbox(msg="暂无该时段该城市数据",title="提示",ok_button="返回")
                continue

            t = pic(df, cursor, city_, year_, month_)

            name_list.append(city_)
            num1_list.append(t[0][0])
            num2_list.append(t[0][1])
            tmp = t[1]
            
            rain_list.append(0)
            cloud_list.append(0)
            sun_list.append(0)
            other_list.append(0)
            for j in range(len(tmp)):
                if '雨' in tmp[j]['weather_']:
                    rain_list[i] = rain_list[i]+tmp[j]['sum_day']
                elif tmp[j]['weather_'] == '晴':
                    sun_list[i] = sun_list[i]+tmp[j]['sum_day']
                elif tmp[j]['weather_'] == '多云':
                    cloud_list[i] = cloud_list[i]+tmp[j]['sum_day']
                elif tmp[j]['weather_'] == '阴':
                    other_list[i] = other_list[i]+tmp[j]['sum_day']

        total_width, n = 0.8, 2      
        x = list(range(len(num1_list)))
        width = total_width / n
        plt.bar(x, num1_list, width=width, label='平均低温', fc='SkyBlue')
        for a, b in zip(range(len(num1_list)), num1_list):
            plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=11)

        for i in range(len(x)):
            x[i] += width
        plt.bar(x, num2_list, width=width, label='平均高温', tick_label=name_list, fc='IndianRed')
        for a, b in zip(range(len(num1_list)), num2_list):
            plt.text(a+width, b, '%.2f' % b, ha='center', va='bottom', fontsize=11)

        plt.legend()
        plt.title(str(year_)+u'年'+str(month_)+u'月'+u'平均气温比较图')
        plt.show()
        
        t1_list, t2_list, t3_list, s_ = [], [], [], []
        for i in range(len(name_list)):
            d = sun_list[i] + cloud_list[i]
            t1_list.append(d)
            d = d + other_list[i]
            t2_list.append(d)
            d = d+rain_list[i]
            t3_list.append(d)
            s_.append(0)

        L1 = [sun_list, cloud_list, other_list, rain_list]
        L2 = [sun_list, t1_list, t2_list, t3_list]
        L3 = [s_, sun_list, t1_list, t2_list]
        desc = ['晴', '多云', '阴', '雨']
        color_list = ['IndianRed', 'lightyellow', 'lightblue', 'b']
        for i in range(4):
            plt.bar(range(len(name_list)), L1[i], bottom =L3[i], label=desc[i], tick_label=name_list, fc=color_list[i])
            for a in range(len(name_list)):
                plt.text(a, L2[i][a], desc[i]+'%d天' % L1[i][a], ha='center', va='bottom', fontsize=11)

        plt.title(str(year_)+u'年'+str(month_)+u'月'+u'各城市天气状况对比图')
        plt.legend()
        plt.show()

        cursor.close()
        conn.close()




def pic(df, cursor, city_, year_, month_):
    X = df[['low_tem', 'high_tem', 'day_']].values
    x1, y1, y2 = [],[],[]
    y3, y4 = [], []
    for i in range(len(X)):
        y1.append(X[i][0])
        y2.append(X[i][1])
        x1.append(X[i][2])

    avg_low = sum(y1) / 30
    avg_high = sum(y2) / 30
    for i in range(len(X)):
        y3.append(avg_low)
        y4.append(avg_high)

    rect1 = [0.04, 0.32, 0.47, 0.5]
    ax = plt.axes(rect1)

    ax.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    x_major_locator=MultipleLocator(3)
    y_major_locator=MultipleLocator(2)

    ax.xaxis.set_major_locator(x_major_locator)
    ax.yaxis.set_major_locator(y_major_locator)

    ax.plot(x1, y1, color='b', label='最低气温')
    ax.plot(x1,y2,color='r', label='最高气温')
    ax.plot(x1,y3, color='b', linestyle= '--',label='平均低温')
    ax.plot(x1,y4,color='r', linestyle='--',label='平均高温')

    ax.set_title(str(year_)+u'年'+str(month_)+u'月'+city_+u'气温走势图')
    ax.set_xlabel(u'日期',fontsize=10)
    ax.set_ylabel(u'气温（摄氏度）',fontsize=10)
    ax.legend(loc=2, prop={'size':6})
    ax.grid()


    sql1 = 'select count(*) sum_day, air_polution from weather where city=%s and year(day_)=%s and month(day_)=%s group by air_polution'
    sql2 = 'select count(*) sum_day, weather_ from weather where city=%s and year(day_)=%s and month(day_)=%s group by weather_'
    cursor.execute(sql1, [city_, year_, month_])
    ret1 = cursor.fetchall()
    cursor.execute(sql2, [ city_, year_, month_])
    ret2 = cursor.fetchall()  
    num1_, name1_ = [],[]
    num2_, name2_ = [],[]
    for i in range(len(ret1)):
        num1_.append(ret1[i]['sum_day'])
        name1_.append(ret1[i]['air_polution']+' '+str(ret1[i]['sum_day'])+u'天')
    for i in range(len(ret2)):
        num2_.append(ret2[i]['sum_day'])
        name2_.append(ret2[i]['weather_']+' '+str(ret2[i]['sum_day'])+u'天')

    plt.axes([0.57, 0.5, 0.4, 0.4])
    plt.pie(x=num1_, labels=name1_, autopct='%3.1f %%')
    plt.title(str(year_)+u'年'+str(month_)+u'月'+city_+u'空气质量统计图')
    plt.axes([0.57, 0.05, 0.4, 0.4])
    plt.pie(x=num2_, labels=name2_, autopct='%3.1f %%')
    plt.title(str(year_)+u'年'+str(month_)+u'月'+city_+u'天气状况统计图')
    plt.show()


    X = df[['low_tem', 'high_tem']]
    X.plot(kind = 'box')
    plt.title(str(year_)+u'年'+str(month_)+u'月'+city_+u'气温分布')
    plt.show()
    tmp = [[avg_low, avg_high], ret2]
    return tmp




def nation_show(option_):
    try:
        conn = pymysql.connect(
        host='localhost', 
        user='root',password='38324hhh',
        database='test1',
        charset='utf8')
    except Exception as e:
        g.msgbox(msg="connect mysql error.",title="提示",ok_button="返回")
        return

    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    if option_ == '气温':
        sql = 'select avg(T.high_) H, avg(T.low_) L, T.province from \
        (select avg(high_tem) high_, avg(low_tem) low_, city, province from weather where year(day_)=2019 and month(day_)=6 group by city, province)\
        T group by T.province order by H'
        cursor.execute(sql)
        ret1 = cursor.fetchall()  
        X = pd.DataFrame(ret1).values
        num1_, num2_, name_ = [], [], []
        for i in range(len(X)):
            num1_.append(float(X[i][0]))
            num2_.append(float(X[i][1]))
            name_.append(X[i][2])
        
        num2_.sort()
        L = [num1_, num2_, '最高', '最低']
        color_list = ['IndianRed', 'SkyBlue']
        sql = 'select avg(high_tem) H, avg(low_tem) L from weather'
        cursor.execute(sql)
        ret1 = cursor.fetchall()
        t = ['H', 'L']
        for i in range(2):
            y = []
            plt.bar(range(len(L[i])), L[i], color=color_list[i], tick_label=name_)
            plt.title('2019年6月各省平均'+L[i+2] +'气温')
            for a, b in zip(range(len(L[i])), L[i]):
                plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=11)
                y.append(float(ret1[0][t[i]]))
            plt.plot(range(len(L[i])), y, linestyle = '--')
            plt.text(1, y[0], '全国平均%.2f度' % y[0], fontsize=11)
            plt.show()


        sql = 'select avg(high_tem), avg(low_tem), city, province from weather group by city, province'
        cursor.execute(sql)
        ret1 = cursor.fetchall()  
        X = pd.DataFrame(ret1).values
        l1, l2, h1, h2=[],[],[],[]
        south_list = ['海南','广东','广西','福建','湖南','江西','湖北','浙江','重庆','贵州','四川','云南','江苏','安徽']
        for i in range(len(X)):
            if X[i][3] in south_list:
                h1.append(float(X[i][0]))
                l1.append(float(X[i][1]))
            else:
                h2.append(float(X[i][0]))
                l2.append(float(X[i][1]))
               

        plt.scatter(l1, h1, color='IndianRed', label=u'南方城市')
        plt.scatter(l2, h2, color='SkyBlue', label=u'北方城市')
        plt.xlabel(u'平均最低气温')
        plt.ylabel(u'平均最高气温')
        plt.legend()
        plt.title(u'2019年6月各城市平均最高和最低气温分布图')
        plt.show()



    elif option_ == '空气质量':
        msg = "请选择空气质量水平"
        title = "历史天气查询"
        choicess_list = ['1.优', '2.良', '3.轻度以上污染']
        air_polution = g.choicebox(msg, title=title, choices=choicess_list)
        if air_polution is None:
            return
        air_polution=air_polution[2:]
        if air_polution == '优' or air_polution == '良':
            sql = 'select avg(T.sum_day_) sum_day, T.province from\
            (select count(*) sum_day_, province, city, air_polution from weather where air_polution=%s and year(day_)=2019 and month(day_)=6\
            group by province, city, air_polution) T group by T.province order by sum_day '           
            cursor.execute(sql, [air_polution])
        else:
            sql = 'select avg(T.sum_day_) sum_day, T.province from\
            (select count(*) sum_day_, province, city, air_polution from weather where air_polution like "%污染" and year(day_)=2019 and month(day_)=6\
            group by province, city, air_polution) T group by T.province order by sum_day '           
            cursor.execute(sql)

        ret1 = cursor.fetchall()  
        X = pd.DataFrame(ret1).values
        num_, name_ = [], []
        for i in range(len(X)):
            num_.append(float(X[i][0]))
            name_.append(X[i][1])

        plt.bar(range(len(num_)), num_, color='SkyBlue', tick_label=name_)
        plt.title('2019年6月各省空气为'+air_polution+'的平均天数')
        for a, b in zip(range(len(num_)), num_):
            plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=11)
        plt.show()


    elif option_ == '天空状况':
        msg = "请选择天气类型"
        title = "历史天气查询"
        choicess_list = ['1.晴', '2.多云', '3.阴', '4.雨']
        class_ = g.choicebox(msg, title=title, choices=choicess_list)
        if class_ is None:
            return
        class_ = class_[2:]
        sql = 'select avg(T.sum_day) sum_, province from\
        (select count(*) sum_day, city, province from weather where weather_ like "%' + class_ + '"\
        and year(day_)=2019 and month(day_)=6 group by city, province)\
        T group by T.province order by sum_'

        cursor.execute(sql)
        ret1 = cursor.fetchall()  
        X = pd.DataFrame(ret1).values
        num_, name_ = [], []
        for i in range(len(X)):
            num_.append(float(X[i][0]))
            name_.append(X[i][1])
        
        sql = 'select avg(T.sum_day) avg_day from (select count(*) sum_day, city from weather where weather_ like "%' + class_ + '" group by city) T'
        cursor.execute(sql)
        ret1 = cursor.fetchall()
        avg_day = float(ret1[0]['avg_day'])
        y = []
        plt.bar(range(len(num_)), num_, tick_label=name_, color='SkyBlue')
        plt.title('2019年6月各省平均'+class_+'天日数')
        for a, b in zip(range(len(num_)), num_):
             plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=11)
             y.append(avg_day)

        plt.plot(range(len(X)), y, linestyle='--')
        plt.text(1, y[0], '全国平均%.2f天' % y[0], fontsize=11)
        plt.show()

        

    else:
        sql = 'select T1.province, T1.sum_ rain_day, T2.sum_wind wind_day from\
        (select avg(T.sum_day) sum_, province from\
        (select count(*) sum_day, city, province from weather where weather_ like "%雨"\
        and year(day_)=2019 and month(day_)=6 group by city, province) T group by T.province order by sum_) T1,\
        (select avg(T.wind_day) sum_wind, T.province from(select count(*) wind_day, city, province from weather\
        where wind_ > \'3级\' group by city, province) T group by T.province) T2\
        where T1.province = T2.province'

        cursor.execute(sql)
        ret1 = cursor.fetchall()  
        X = pd.DataFrame(ret1).values
        

        rain1, rain2, wind1, wind2=[],[],[],[]
        south_list = ['海南','广东','广西','福建','湖南','江西','湖北','浙江','重庆','贵州','四川','云南','江苏','安徽']
        for i in range(len(X)):
            if X[i][0] in south_list:
                rain1.append(float(X[i][1]))
                wind1.append(float(X[i][2]))
            else:
                rain2.append(float(X[i][1]))
                wind2.append(float(X[i][2]))


        plt.scatter(rain1, wind1, color='IndianRed', label ='南方省份')
        plt.scatter(rain2, wind2, color='SkyBlue', label='北方省份')
        plt.title('各省平均大风日数和雨日关系')
        plt.xlabel('全省平均雨日')
        plt.ylabel('全省平均大风日数')
        plt.legend()
        plt.show()

    cursor.close()
    conn.close()






if __name__ == '__main__':
    choice = '1'
    while choice != '3.退出系统' and choice is not None:
        msg = "请选择需要的功能"
        title = "历史天气查询系统"
        choicess_list = ['1.抓取天气数据', '2.查询天气数据', '3.退出系统', '4.城市天气数据绘图', '5.全国天气数据绘图']
        choice= g.choicebox(msg, title=title, choices=choicess_list)

        if choice == '1.抓取天气数据':
            post_data()
        elif choice == '2.查询天气数据':
            query_data()
        elif choice == '4.城市天气数据绘图':
            show()
        elif choice == '5.全国天气数据绘图':
            msg = "请选择查询选项"
            title = "历史天气查询"
            choicess_list = ['1.气温', '2.空气质量', '3.天空状况', '4.风力']
            query_ = g.choicebox(msg, title=title, choices=choicess_list)
            if query_ is not None:
                nation_show(query_[2:])