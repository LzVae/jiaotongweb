from django.shortcuts import render
import numpy as np
import matplotlib.pyplot as plt
import os
import pymysql
import pymysql.cursors
from datetime import datetime
import shutil
from chart.models import chartdate,I023,I024,I055,I056,I057,I058,I075,I077,I089,Tsclane,sectordiagram,datacheck,phasecheck
from chart.forms import ChartForm,SectordiagramForm,datacheckForm,phasecheckFrom
from time import sleep, ctime
import numpy as np
import matplotlib.pyplot as plt
import pymysql.cursors
from time import sleep, ctime
import shutil
import time
from matplotlib.path import Path
import matplotlib.patches as patches
from pylab import mpl
import math
import numpy
import pymysql.cursors
import random
mpl.rcParams['font.sans-serif']=['SimHei']
# import global_x.py

global glo_direction

PictureData=[]

def start(request):
    connect = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='8200506',
        db='test',
        charset='utf8'
    )
    cursor = connect.cursor()

    sqlm = "select * from %s"

    tsclane = []

    def gettsclanelist(a, b):
        t = []
        cursor.execute(a % (b))
        results = cursor.fetchall()
        for row in results:
            if row[1] != 0:
                sid = row[1]
                movement = row[4]
                dircetion = row[6]
                intersectionld = row[7]
                t.append([sid, movement, dircetion, intersectionld])
        return t

    tsclane = gettsclanelist(sqlm, "tsclane")

    # 选择路口并读取数据库


    def periodreadlist(a, b):  # 读取路口数据存入列表

        car = []
        cursor.execute(a % (b))
        results = cursor.fetchall()
        for rowa in results:
            id = rowa[0]
            inteid = rowa[1]
            direction = rowa[2]
            lane = rowa[3]
            carplate = rowa[4]
            passtime = rowa[5]
            traveltime = rowa[6]
            upinteid = rowa[7]
            updirection = rowa[8]
            uplane = rowa[9]
            car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection, uplane])
        return car

    carlist = periodreadlist(sqlm, "i056")

    # 选择路口并读取数据库结束

    # 选择时间
    # 返回datetime元素信息函数，暂时无用
    def periodtimecalculatne(a):  # a对应passtime row[5]
        x = [0, 0, 0, 0, 0, 0]
        x[0] = a.year
        x[1] = a.month
        x[2] = a.day
        x[3] = a.hour
        x[4] = a.minute
        x[5] = a.second
        return x
        print(a)

    def dayperiodreadlist(a, b, c, d):  # f为当前路口总列表，此函数为提取指定日期列表并返回,abc年月日,d为diection
        day = []
        for row in d:
            if row[5].year == a and row[5].month == b and row[5].day == c:
                day.append(row)

        return day

    daycarlist = []
    daycarlist = dayperiodreadlist(2017, 5, 24, carlist)
    print(" 读取路口当前日期数据库完成 %s" % ctime())

    # 选择时间结束，得到指定日期list：daycarlist

    # 将该时间点按方向和转向分类

    def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
        t = []
        for row in a:
            if row[3] == b:
                t.append(row)
        return t

    idtsclane = []
    idtsclane = getidtsclane(tsclane, 56)
    print(" 读取选择路口渠化信息完成 %s" % ctime())

    def getlanesid(a, b):  # 得到对应sid的direction和lane   a:渠化列表 b 路口sid
        k = [0, 0]
        d0 = []
        d2 = []
        d4 = []
        d6 = []
        for row in a:  # 得到各个direcition lane的个数
            if row[2] == 0:
                d0.append(row)
            elif row[2] == 2:
                d2.append(row)
            elif row[2] == 4:
                d4.append(row)
            elif row[2] == 6:
                d6.append(row)
        for row in a:
            if row[0] == b:  # sid相等采匹配k[0]和k[1]
                k[0] = row[2]  # direction
                if k[0] == 6:
                    k[1] = row[0]  # lane
                elif k[0] == 4:
                    k[1] = row[0] - len(d6)
                elif k[0] == 2:
                    k[1] = row[0] - len(d6) - len(d4)
                elif k[0] == 0:
                    k[1] = row[0] - len(d6) - len(d4) - len(d2)
        return k

    # 输出sid对应的direction和lane

    def laneclass(a, b, c):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
        p = []
        p = getlanesid(b, c)
        c = p[0]  # direction
        d = p[1]  # lane
        t = []
        for row in a:
            if row[2] == c and row[3] == d:
                t.append(row)
        return t

    # print(len(idtsclane))
    def automakesidlist(a, b):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
        sidlen = len(b)
        f = []
        for i in range(sidlen):
            v = []
            v = laneclass(a, b, i + 1)
            f.append(v)
        return f

    sidlanelist = []
    sidlanelist = automakesidlist(daycarlist, idtsclane)  # sidlanelist是一个列表，长度是路口总id长度，里面包含了对应sid的列表

    # sidlanelist有sid个数的列表，里面是按日期和sid分开的子列表

    # 一个数据一个点
    def pointmaker(a, b):  # a为一个数据,b为周期
        x = [0, 0]
        x[0] = a[5].hour + a[5].minute / 60 + a[5].second / 3600  # 横坐标
        x[1] = (a[5].hour * 3600 + a[5].minute * 60 + a[5].second) % b
        return x

    # 一个列表数据一个列表点
    def pointlistmaker(a, b):  # a为指定列表 b为周期
        t = [[], []]
        for row in a:
            x = row[5].hour + row[5].minute / 60 + row[5].second / 3600  # 横坐标
            y = (row[5].hour * 3600 + row[5].minute * 60 + row[5].second) % b
            t[0].append(x)
            t[1].append(y)
        return t

    def autopointlistmaker(a, b):  # a sidlanelist b 周期
        t = []
        for row in a:  # 每一个row都是一个列表
            u = []
            u = pointlistmaker(row, b)
            t.append(u)
        return t

    pointlist = []
    pointlist = autopointlistmaker(sidlanelist, 120)
    print(" 点阵完成 %s" % ctime())

    # 点阵生成完毕 按sid编号



    def picturemaker(a, e, f):  # a sid编号 b周期 c d时间区间 e为点阵 f：点的颜色
        if a != -999:  # plt.plot(pointlist[0][i][0],pointlist[0][i][1],color='red',marker='.')
            plt.scatter(e[a - 1][0], e[a - 1][1], s=0.2 * 10, c=f);
            # plt.xlabel('周期')
            # plt.ylabel('时间')
            # plt.xlim(0,24)

    def autopicturemaker(a, b, c, d, e, f, g, h):  # avcd 4路编号 e周期 f,g时间区间，h点阵
        plt.figure(figsize=(12, 6))
        picturemaker(a, h, "red")
        picturemaker(b, h, "b")
        picturemaker(c, h, "g")
        picturemaker(d, h, 'y')
        plt.ylim(0, e)
        plt.xticks(np.linspace(f, g, g - f + 1, endpoint=True))

        plt.savefig("example.jpg",dpi=300)
        print(" 图片生成完成 %s" % ctime())
        shutil.copy("D:\pythonwork\jiaotongweb\example.jpg","D:\pythonwork\jiaotongweb\chart\static")

        #plt.show()

    autopicturemaker(6, 7, 8, 9, 120, 15, 24, pointlist)  # 红 蓝 绿 黄
    return render(request,"home.html",{})

def testhtml(resquest):
    return render(resquest,'flowchart.html',{})

def homehtml(resquest):
    context={}
    context['t']='/' + 'flowchart9527'+'/'+str(random.randint(1,999))

    return render(resquest,'home.html',context)

def page_not_found(resquest):
    return render(resquest,'404.html')

# def get_year(resquest):
#
#     if resquest.method=="POST":
#         form=PictureForm(resquest.POST)
#
#         if  form.is_valid():
#             t=chartdate.objects.create(
#             year=form.cleaned_data['year'],
#             month = form.cleaned_data['month'],
#             day = form.cleaned_data['day'],
#            # direction = form.cleaned_data['direction'],
#             #Xaxisa = form.cleaned_data['Xaxisa '],
#             #Xaxisb = form.cleaned_data['Xaxisb'],
#             #Yaxis = form.cleaned_data['Yaxis'],
#             #Alane = form.cleaned_data['Alane'],
#             #Blane = form.cleaned_data['Blane'],
#            # Clane = form.cleaned_data['Clane'],
#             )
#             t.save()
#             return render(resquest, 'flowchart.html', {'form': form})
#
#     return render(resquest,'flowchart.html',{})
def maphtml(resquest):
    return render(resquest,'mapbase.html',{})

def sectorGetDate(resquest):
    context = {}
    ran=random.randint(0,50)
    if resquest.method == "POST":

        sectorpicture_form = SectordiagramForm(data=resquest.POST, auto_id="%s")
        context['sectorpicture_form'] = sectorpicture_form
        print(sectorpicture_form.is_valid())
        if sectorpicture_form.is_valid():
            originyear = sectorpicture_form.cleaned_data['originyear']
            originmonth = sectorpicture_form.cleaned_data['originmonth']
            originday = sectorpicture_form.cleaned_data['originday']
            originhour=sectorpicture_form.cleaned_data['originhour']
            originmin = sectorpicture_form.cleaned_data['originmin']
            endyear = sectorpicture_form.cleaned_data['endyear']
            endmonth = sectorpicture_form.cleaned_data['endmonth']
            endday = sectorpicture_form.cleaned_data['endday']
            endhour = sectorpicture_form.cleaned_data['endhour']
            endmin = sectorpicture_form.cleaned_data['endmin']



            t = sectordiagram.objects.get(id=1)
            t.originyear=originyear
            t.originmonth=originmonth
            t.originday=originday
            t.originhour=originhour
            t.originmin=originmin

            t.endyear=endyear
            t.endmonth=endmonth
            t.endday=endday
            t.endhour=endhour
            t.endmin=endmin

            t.save()
            n = sectordiagram.objects.get(id=1)
            date1 = str(n.originyear) + '-' + str(n.originmonth) + '-' + str(n.originday) + ' ' + str(
                n.originhour) + ':' + str(
                n.originmin) + ':0'
            date2 = str(n.endyear) + '-' + str(n.endmonth) + '-' + str(n.endday) + ' ' + str(n.endhour) + ':' + str(
                n.endmin) + ':59'

            context['date1'] = date1
            context['date2'] = date2

            PictureData = [date1, date2]
            print(PictureData)

            def gettsclanelist():  # 读取渠化信息
                p = []
                results = Tsclane.objects.all()
                for row in results:
                    if row.sid != 0:
                        sid = row.sid
                        movement = row.movement
                        dircetion = row.direction
                        intersectionld = row.intersectionid
                        p.append([sid, movement, dircetion, intersectionld])
                return p

            tsclane = gettsclanelist()
            print("初始化完成 %s" % ctime())

            def newdayperiodreadlist(a):  # 读取路口数据存入列表 a b c年月日
                # y = str(y)
                # m = str(m)
                # d = str(d)
                # h = str(h)
                # min = str(min)
                # y1 = str(y1)
                # m1 = str(m1)
                # d1 = str(d1)
                # h1 = str(h1)
                # min1 = str(min1 - 1)
                #
                # t5 = y + '-' + m + '-' + d + ' ' + h + ':' + min + ':0'
                # t6 = y1 + '-' + m1 + '-' + d1 + ' ' + h1 + ':' + min1 + ':59'

                car = []
                results = []

                if a == 23:
                    results = I023.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 24:
                    results = I024.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 55:
                    results = I055.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 56:
                    results = I056.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 57:
                    results = I057.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 58:
                    results = I058.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 75:
                    results = I075.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 77:
                    results = I077.objects.filter(passtime__lte=date2, passtime__gte=date1)
                elif a == 89:
                    results = I089.objects.filter(passtime__lte=date2, passtime__gte=date1)
                else:
                    results = []

                # print(len(results))
                # print(results)

                for rowa in results:
                    id = rowa.id
                    inteid = rowa.inteid
                    direction = rowa.direction
                    lane = rowa.lane
                    carplate = rowa.carplate
                    passtime = rowa.passtime
                    traveltime = rowa.traveltime
                    upinteid = rowa.upinteid
                    updirection = rowa.updirection
                    uplane = rowa.uplane
                    car.append(
                        [id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection, uplane])
                return car

            # daycarlist_23=newdayperiodreadlist(23)
            # daycarlist_24 = newdayperiodreadlist(24)
            # daycarlist_55 = newdayperiodreadlist(55)
            # daycarlist_56 = newdayperiodreadlist(56)
            # daycarlist_57 = newdayperiodreadlist(57)
            # daycarlist_58 = newdayperiodreadlist(58)
            # daycarlist_75 = newdayperiodreadlist(75)
            # daycarlist_77 = newdayperiodreadlist(77)
            # daycarlist_89 = newdayperiodreadlist(89)
            # print(" 读取路口当前时间段数据库完成 %s" % ctime())

            def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
                t = []
                for row in a:
                    if row[3] == b:
                        t.append(row)
                return t

            # idtsclane_23 = getidtsclane(tsclane, 23)
            # idtsclane_24 = getidtsclane(tsclane, 24)
            # idtsclane_55 = getidtsclane(tsclane, 55)
            # idtsclane_56 = getidtsclane(tsclane, 56)
            # idtsclane_57 = getidtsclane(tsclane, 57)
            # idtsclane_58 = getidtsclane(tsclane, 58)
            # idtsclane_75 = getidtsclane(tsclane, 75)
            # idtsclane_77 = getidtsclane(tsclane, 77)
            # idtsclane_89 = getidtsclane(tsclane, 89)

            # print(" 读取选择路口渠化信息完成 %s" % ctime())

            def sidnumcalculate(a):  # 根据渠化信息得到车辆转向的路口,a渠化信息
                sid = 0
                d0 = []
                d2 = []
                d4 = []
                d6 = []
                for row in a:  # 得到各个direcition lane的个数
                    if row[2] == 0:
                        d0.append(row)
                    elif row[2] == 2:
                        d2.append(row)
                    elif row[2] == 4:
                        d4.append(row)
                    elif row[2] == 6:
                        d6.append(row)
                return len(d0), len(d2), len(d4), len(d6)

            # lend0_23, lend2_23, lend4_23, lend6_23 = sidnumcalculate(idtsclane_23)
            # lend0_24, lend2_24, lend4_24, lend6_24 = sidnumcalculate(idtsclane_24)
            # lend0_55, lend2_55, lend4_55, lend6_55 = sidnumcalculate(idtsclane_55)
            # lend0_56, lend2_56, lend4_56, lend6_56 = sidnumcalculate(idtsclane_56)
            # lend0_57, lend2_57, lend4_57, lend6_57 = sidnumcalculate(idtsclane_57)
            # lend0_58, lend2_58, lend4_58, lend6_58 = sidnumcalculate(idtsclane_58)
            # lend0_75, lend2_75, lend4_75, lend6_75 = sidnumcalculate(idtsclane_75)
            # lend0_77, lend2_77, lend4_77, lend6_77 = sidnumcalculate(idtsclane_77)
            # lend0_89, lend2_89, lend4_89, lend6_89 = sidnumcalculate(idtsclane_89)


            def movementdirectioncalculate(a, lend0, lend2, lend4, lend6, d, l):
                sid = 0
                movement = 0
                if d == 0:
                    sid = l + lend6 + lend4 + lend2
                elif d == 2:
                    sid = l + lend6 + lend4
                elif d == 4:
                    sid = l + lend6
                elif d == 6:
                    sid = l
                for row in a:
                    if row[0] == sid:
                        movement = row[1]
                return movement

            def turndirectioncalculate(a, b):  # a路口id b：movement
                k = 0
                if a == 0:
                    if b == 1:
                        k = 6
                    elif b == 2:
                        k = 4
                    elif b == 3:
                        k = 2
                    elif b == 4:  # 直-右→右
                        k = 6
                    elif b == 5:  # 直-右-右→直
                        k = 4
                    elif b == 6:  # 直-左→左
                        k = 2
                    elif b == 7:  # 左-掉头→掉头
                        k = -999  # 掉头
                    elif b == 8:  # 右-左→右
                        k = 6
                    elif b == 9:
                        k = -999
                elif a == 2:
                    if b == 1:  # 右
                        k = 0
                    elif b == 2:  # 直
                        k = 6
                    elif b == 3:  # 左
                        k = 4
                    elif b == 4:  # 直-右→右
                        k = 0
                    elif b == 5:  # 直-右-右→直
                        k = 6
                    elif b == 6:  # 直-左→左
                        k = 4
                    elif b == 7:  # 左-掉头→掉头
                        k = -999  # 掉头
                    elif b == 8:  # 右-左→右
                        k = 0
                    elif b == 9:
                        k = -999
                elif a == 4:
                    if b == 1:  # 右
                        k = 2
                    elif b == 2:  # 直
                        k = 0
                    elif b == 3:  # 左
                        k = 6
                    elif b == 4:  # 直-右→右
                        k = 2
                    elif b == 5:  # 直-右-右→直
                        k = 0
                    elif b == 6:  # 直-左→左
                        k = 6
                    elif b == 7:  # 左-掉头→掉头
                        k = -999  # 掉头
                    elif b == 8:  # 右-左→右
                        k = 2
                    elif b == 9:
                        k = -999
                elif a == 6:
                    if b == 1:  # 右
                        k = 4
                    elif b == 2:  # 直
                        k = 2
                    elif b == 3:  # 左
                        k = 0
                    elif b == 4:  # 直-右→右
                        k = 4
                    elif b == 5:  # 直-右-右→直
                        k = 2
                    elif b == 6:  # 直-左→左
                        k = 0
                    elif b == 7:  # 左-掉头→掉头
                        k = -999  # 掉头
                    elif b == 8:  # 右-左→右
                        k = 4
                    elif b == 9:
                        k = -999
                return k

            def flowcalculate(a):
                if len(a) != 0:
                    num = len(a)
                    timeArray1 = time.strptime(str(a[0][5]), "%Y-%m-%d %H:%M:%S")
                    utctime1 = int(time.mktime(timeArray1))
                    timeArray2 = time.strptime(str(a[len(a) - 1][5]), "%Y-%m-%d %H:%M:%S")
                    utctime2 = int(time.mktime(timeArray2))
                    utctime = utctime2 - utctime1
                    inttime = utctime / 3600
                    flow = round(num / inttime, 2)
                else:
                    flow = 0
                return flow

            def inflowcalculate(a, b, lend0, lend2, lend4, lend6):

                daycarlist_0 = []
                daycarlist_0to2 = []
                daycarlist_0to4 = []
                daycarlist_0to6 = []
                daycarlist_2 = []
                daycarlist_2to0 = []
                daycarlist_2to4 = []
                daycarlist_2to6 = []
                daycarlist_4 = []
                daycarlist_4to0 = []
                daycarlist_4to2 = []
                daycarlist_4to6 = []
                daycarlist_6 = []
                daycarlist_6to0 = []
                daycarlist_6to2 = []
                daycarlist_6to4 = []
                for row in a:
                    if row[2] == 0:
                        daycarlist_0.append(row)
                    elif row[2] == 2:
                        daycarlist_2.append(row)
                    elif row[2] == 4:
                        daycarlist_4.append(row)
                    elif row[2] == 6:
                        daycarlist_6.append(row)

                if len(daycarlist_0) != 0:
                    for row in daycarlist_0:
                        movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                        k = turndirectioncalculate(0, movement)
                        if k == 2:
                            daycarlist_0to2.append(row)
                        elif k == 4:
                            daycarlist_0to4.append(row)
                        elif k == 6:
                            daycarlist_0to6.append(row)
                    flow_0 = flowcalculate(daycarlist_0)
                    flow_0to2 = flowcalculate(daycarlist_0to2)
                    flow_0to4 = flowcalculate(daycarlist_0to4)
                    flow_0to6 = flowcalculate(daycarlist_0to6)
                else:
                    flow_0, flow_0to2, flow_0to4, flow_0to6 = 1, 0, 0, 0

                if len(daycarlist_2) != 0:
                    for row in daycarlist_2:
                        movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                        k = turndirectioncalculate(2, movement)
                        if k == 0:
                            daycarlist_2to0.append(row)
                        elif k == 4:
                            daycarlist_2to4.append(row)
                        elif k == 6:
                            daycarlist_2to6.append(row)
                    flow_2 = flowcalculate(daycarlist_2)
                    flow_2to0 = flowcalculate(daycarlist_2to0)
                    flow_2to4 = flowcalculate(daycarlist_2to4)
                    flow_2to6 = flowcalculate(daycarlist_2to6)
                else:
                    flow_2, flow_2to0, flow_2to4, flow_2to6 = 1, 0, 0, 0
                if len(daycarlist_4) != 0:
                    for row in daycarlist_4:
                        movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                        k = turndirectioncalculate(4, movement)
                        if k == 0:
                            daycarlist_4to0.append(row)
                        elif k == 2:
                            daycarlist_4to2.append(row)
                        elif k == 6:
                            daycarlist_4to6.append(row)
                    flow_4 = flowcalculate(daycarlist_4)
                    flow_4to0 = flowcalculate(daycarlist_4to0)
                    flow_4to2 = flowcalculate(daycarlist_4to2)
                    flow_4to6 = flowcalculate(daycarlist_4to6)
                else:
                    flow_4, flow_4to0, flow_4to2, flow_4to6 = 1, 0, 0, 0

                if len(daycarlist_6) != 0:
                    for row in daycarlist_6:
                        movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                        k = turndirectioncalculate(6, movement)
                        if k == 0:
                            daycarlist_6to0.append(row)
                        elif k == 2:
                            daycarlist_6to2.append(row)
                        elif k == 4:
                            daycarlist_6to4.append(row)
                    flow_6 = flowcalculate(daycarlist_6)
                    flow_6to0 = flowcalculate(daycarlist_6to0)
                    flow_6to2 = flowcalculate(daycarlist_6to2)
                    flow_6to4 = flowcalculate(daycarlist_6to4)
                else:
                    flow_6, flow_6to0, flow_6to2, flow_6to4 = 1, 0, 0, 0

                return [flow_0, flow_0to2, flow_4, flow_0to6], [flow_2, flow_2to0, flow_2to4, flow_2to6], [flow_4,
                                                                                                           flow_4to0,
                                                                                                           flow_4to2,
                                                                                                           flow_4to6], [
                           flow_6,
                           flow_6to0,
                           flow_6to2,
                           flow_6to4]

            # flowgroup_23 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_23, idtsclane_23,lend0_23,lend2_23,lend4_23,lend6_23)
            # flowgroup_24 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_24, idtsclane_24,
            #                                                                                   lend0_24, lend2_24, lend4_24,
            #                                                                                   lend6_24)
            # flowgroup_55 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_55, idtsclane_55,
            #                                                                                   lend0_55, lend2_55, lend4_55,
            #                                                                                   lend6_55)
            # flowgroup_56 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_56, idtsclane_56,
            #                                                                                   lend0_56, lend2_56, lend4_56,
            #                                                                                   lend6_56)
            # flowgroup_57 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_57, idtsclane_57,
            #                                                                                   lend0_57, lend2_57, lend4_57,
            #                                                                                   lend6_57)
            # flowgroup_58 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_58, idtsclane_58,
            #                                                                                   lend0_58, lend2_58, lend4_58,
            #                                                                                   lend6_58)
            # flowgroup_75 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_75, idtsclane_75,
            #                                                                                   lend0_75, lend2_75, lend4_75,
            #                                                                                   lend6_75)
            # flowgroup_77 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_77, idtsclane_77,
            #                                                                                   lend0_77, lend2_77, lend4_77,
            #                                                                                   lend6_77)
            # flowgroup_89 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_89, idtsclane_89,
            #                                                                                   lend0_89, lend2_89, lend4_89,
            #                                                                                   lend6_89)

            mpl.rcParams['font.sans-serif'] = ['SimHei']

            # fig_23 = plt.figure()
            # fig_24 = plt.figure()
            # fig_55 = plt.figure()
            # fig_56 = plt.figure()
            # fig_57 = plt.figure()
            # fig_58 = plt.figure()
            # fig_75 = plt.figure()
            # fig_77 = plt.figure()
            # fig_89 = plt.figure()
            #
            # ax_23 = fig_23.add_subplot(111)
            # ax_24 = fig_24.add_subplot(111)
            # ax_55 = fig_55.add_subplot(111)
            # ax_56 = fig_56.add_subplot(111)
            # ax_57 = fig_57.add_subplot(111)
            # ax_58 = fig_58.add_subplot(111)
            # ax_75 = fig_75.add_subplot(111)
            # ax_77 = fig_77.add_subplot(111)
            # ax_89 = fig_89.add_subplot(111)
            #
            #
            # date_23 = flowgroup_23
            # date_24 = flowgroup_24
            # date_55 = flowgroup_55
            # date_56 = flowgroup_56
            # date_57 = flowgroup_57
            # date_58 = flowgroup_58
            # date_75 = flowgroup_75
            # date_77 = flowgroup_77
            # date_89 = flowgroup_89


            def pointcalculate_clockwisetest(c1, d1, c2, d2, r, p, t1, t2, date, type, tb1,
                                             tb2,
                                             flowsize):  # c1 ,d1,c2,d2:两条贝塞尔曲线的中间点，r：半径，p：补偿角，t1:：起点相位，t2：终点相位，date：数据，type：类型，tb1，tb2：bellse的参数t
                pointgroup = []
                codegroup = []
                h1 = 0
                h2 = 0
                h3 = 0
                if type == 1:

                    if date[0] != -999:
                        pointgroup = []
                        pointgroup1 = []
                        pointgroup2 = []
                        pointgroup3 = []
                        pointgroup4 = []
                        codegroup = []
                        codegroup1 = []
                        codegroup2 = []
                        codegroup3 = []
                        codegroup4 = []

                        h1 = int(round((date[1] / date[0]), 2) * int(date[0] / flowsize * 40))
                        # h2=int(date[0]/1000*30)-h1
                        h2 = int(round((date[2] / date[0]), 2) * int(date[0] / flowsize * 40))
                        h3 = int(round((date[3] / date[0]), 2) * int(date[0] / flowsize * 40))
                        # pointgroup.append(origin)
                        # codegroup.append(Path.MOVETO)
                        if t1 == 1:
                            if t2 == 1:
                                if h1 != 0:
                                    originx = (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h1 + h2 + h3 - 1):
                                        x = (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h2 + h3:len(pointgroup1)]
                                    for i in range(h1 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h1):
                                        x = 0.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h1):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 2:
                                if h3 != 0:
                                    originx = (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h2 + h3 - 1):
                                        x = (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h2:len(pointgroup1)]
                                    for i in range(h3 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h3):
                                        x = math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h3):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 3:
                                if h2 != 0:
                                    originx = (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h2 - 1):
                                        x = (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    # pointgroup1=pointgroup1[h1:len(pointgroup1)]
                                    for i in range(h2 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h2):
                                        x = 1.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h2):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 4:
                                123
                        elif t1 == 2:
                            if t2 == 1:
                                123
                            elif t2 == 2:
                                if h3 != 0:
                                    originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup.append(Path.MOVETO)
                                    for i in range(h1 + h2 + h3 - 1):
                                        x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h1 + h2:len(pointgroup1)]
                                    for i in range(h3 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h3):
                                        x = math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h3):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 3:
                                if h2 != 0:
                                    originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup.append(Path.MOVETO)
                                    for i in range(h1 + h2 - 1):
                                        x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h1:len(pointgroup1)]
                                    for i in range(h2 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h2):
                                        x = 1.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h2):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 4:
                                if h1 != 0:
                                    originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup.append(Path.MOVETO)
                                    for i in range(h1 - 1):
                                        x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    for i in range(h1 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h1):
                                        x = 2 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h1):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (c1 - numpy.square(1 - tb1) * pointgroup1[h1 - 1][0] - numpy.square(tb1) *
                                          pointgroup3[h1 - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (d1 - numpy.square(1 - tb1) * pointgroup1[h1 - 1][1] - numpy.square(tb1) *
                                          pointgroup3[h1 - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[h1 - 1], (x1, y1), pointgroup3[h1 - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)

                        elif t1 == 3:
                            if t2 == 1:
                                if h1 != 0:
                                    originx = math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h1 - 1):
                                        x = math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                        # pointgroup1 = pointgroup1[h3:len(pointgroup1)]
                                    for i in range(h1 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h1):
                                        x = 0.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h1):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 2:
                                123
                            elif t2 == 3:
                                if h3 != 0:
                                    originx = math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h1 + h2 + h3 - 1):
                                        x = math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h2 + h1:len(pointgroup1)]
                                    for i in range(h3 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h3):
                                        x = 1.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h3):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 4:
                                if h2 != 0:
                                    originx = math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h2 + h1 - 1):
                                        x = math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h1:len(pointgroup1)]
                                    for i in range(h2 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h2):
                                        x = 2 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h2):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                        elif t1 == 4:
                            if t2 == 1:
                                if h1 != 0:
                                    originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h1 + h3 - 1):
                                        x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h3:len(pointgroup1)]
                                    for i in range(h1 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h1):
                                        x = 0.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h1):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 2:
                                if h3 != 0:
                                    originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h3 - 1):
                                        x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                        # pointgroup1 = pointgroup1[h2:len(pointgroup1)]
                                    for i in range(h3 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h3):
                                        x = math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h3):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                            elif t2 == 3:
                                123
                            elif t2 == 4:
                                if h2 != 0:
                                    originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                                    originx1 = r * math.cos(originx)
                                    originy1 = r * math.sin(originx)
                                    pointgroup1.append((originx1, originy1))
                                    codegroup1.append(Path.MOVETO)
                                    for i in range(h2 + h1 + h3 - 1):
                                        x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup1.append((x1, y1))
                                    pointgroup1 = pointgroup1[h1 + h3:len(pointgroup1)]
                                    for i in range(h2 - 1):
                                        codegroup1.append(Path.LINETO)

                                    for i in range(h2):
                                        x = 2 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                        x1 = r * math.cos(x)
                                        y1 = r * math.sin(x)
                                        pointgroup3.append((x1, y1))
                                    for i in range(h2):
                                        codegroup3.append(Path.LINETO)
                                    x1 = (
                                             c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 0] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][0]) / (
                                             2 * tb1 * (1 - tb1))
                                    y1 = (
                                             d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][
                                                 1] - numpy.square(tb1) *
                                             pointgroup3[len(pointgroup3) - 1][1]) / (
                                             2 * tb1 * (1 - tb1))
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                                   pointgroup3[len(pointgroup3) - 1]]
                                    codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                                    x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              0]) / (
                                             2 * tb2 * (1 - tb2))
                                    y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) *
                                          pointgroup1[0][
                                              1]) / (
                                             2 * tb2 * (1 - tb2))
                                    pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                                    pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                                    pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                                    codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                                    pointgroup.extend(pointgroup1)
                                    pointgroup.extend(pointgroup2)
                                    pointgroup.extend(pointgroup3)
                                    pointgroup.extend(pointgroup4)
                                    codegroup.extend(codegroup1)
                                    codegroup.extend(codegroup2)
                                    codegroup.extend(codegroup3)
                                    codegroup.extend(codegroup4)
                return pointgroup, codegroup, h1, h2, h3

            # h1_p_23 = int(round((date_23[3][1] / date_23[3][0]), 2) * int(date_23[3][0] / 1000 * 30))
            # h3_p_23 = int(round((date_23[3][3] / date_23[3][0]), 2) * int(date_23[3][0] / 1000 * 30))
            # h2_p_23 = int(round((date_23[1][2] / date_23[1][0]), 2) * int(date_23[1][0] / 1000 * 30))
            # h2_p1_23 = int(round((date_23[3][2] / date_23[3][0]), 2) * int(date_23[3][0] / 1000 * 30))
            # h1_p1_23 = int(round((date_23[2][1] / date_23[2][0]), 2) * int(date_23[2][0] / 1000 * 30))
            # h3_p1_23 = int(round((date_23[1][3] / date_23[1][0]), 2) * int(date_23[1][0] / 1000 * 30))
            # h3_p2_23 = int(round((date_23[2][3] / date_23[2][0]), 2) * int(date_23[2][0] / 1000 * 30))
            #
            # h1_p_24 = int(round((date_24[3][1] / date_24[3][0]), 2) * int(date_24[3][0] / 1000 * 30))
            # h3_p_24 = int(round((date_24[3][3] / date_24[3][0]), 2) * int(date_24[3][0] / 1000 * 30))
            # h2_p_24 = int(round((date_24[1][2] / date_24[1][0]), 2) * int(date_24[1][0] / 1000 * 30))
            # h2_p1_24 = int(round((date_24[3][2] / date_24[3][0]), 2) * int(date_24[3][0] / 1000 * 30))
            # h1_p1_24 = int(round((date_24[2][1] / date_24[2][0]), 2) * int(date_24[2][0] / 1000 * 30))
            # h3_p1_24 = int(round((date_24[1][3] / date_24[1][0]), 2) * int(date_24[1][0] / 1000 * 30))
            # h3_p2_24 = int(round((date_24[2][3] / date_24[2][0]), 2) * int(date_24[2][0] / 1000 * 30))
            #
            # h1_p_55 = int(round((date_55[3][1] / date_55[3][0]), 2) * int(date_55[3][0] / 1000 * 30))
            # h3_p_55 = int(round((date_55[3][3] / date_55[3][0]), 2) * int(date_55[3][0] / 1000 * 30))
            # h2_p_55 = int(round((date_55[1][2] / date_55[1][0]), 2) * int(date_55[1][0] / 1000 * 30))
            # h2_p1_55 = int(round((date_55[3][2] / date_55[3][0]), 2) * int(date_55[3][0] / 1000 * 30))
            # h1_p1_55 = int(round((date_55[2][1] / date_55[2][0]), 2) * int(date_55[2][0] / 1000 * 30))
            # h3_p1_55 = int(round((date_55[1][3] / date_55[1][0]), 2) * int(date_55[1][0] / 1000 * 30))
            # h3_p2_55 = int(round((date_55[2][3] / date_55[2][0]), 2) * int(date_55[2][0] / 1000 * 30))
            #
            # h1_p_56 = int(round((date_56[3][1] / date_56[3][0]), 2) * int(date_56[3][0] / 1000 * 30))
            # h3_p_56 = int(round((date_56[3][3] / date_56[3][0]), 2) * int(date_56[3][0] / 1000 * 30))
            # h2_p_56 = int(round((date_56[1][2] / date_56[1][0]), 2) * int(date_56[1][0] / 1000 * 30))
            # h2_p1_56 = int(round((date_56[3][2] / date_56[3][0]), 2) * int(date_56[3][0] / 1000 * 30))
            # h1_p1_56 = int(round((date_56[2][1] / date_56[2][0]), 2) * int(date_56[2][0] / 1000 * 30))
            # h3_p1_56 = int(round((date_56[1][3] / date_56[1][0]), 2) * int(date_56[1][0] / 1000 * 30))
            # h3_p2_56 = int(round((date_56[2][3] / date_56[2][0]), 2) * int(date_56[2][0] / 1000 * 30))
            #
            # h1_p_57 = int(round((date_57[3][1] / date_57[3][0]), 2) * int(date_57[3][0] / 1000 * 30))
            # h3_p_57 = int(round((date_57[3][3] / date_57[3][0]), 2) * int(date_57[3][0] / 1000 * 30))
            # h2_p_57 = int(round((date_57[1][2] / date_57[1][0]), 2) * int(date_57[1][0] / 1000 * 30))
            # h2_p1_57 = int(round((date_57[3][2] / date_57[3][0]), 2) * int(date_57[3][0] / 1000 * 30))
            # h1_p1_57 = int(round((date_57[2][1] / date_57[2][0]), 2) * int(date_57[2][0] / 1000 * 30))
            # h3_p1_57 = int(round((date_57[1][3] / date_57[1][0]), 2) * int(date_57[1][0] / 1000 * 30))
            # h3_p2_57 = int(round((date_57[2][3] / date_57[2][0]), 2) * int(date_57[2][0] / 1000 * 30))
            #
            # h1_p_58 = int(round((date_58[3][1] / date_58[3][0]), 2) * int(date_58[3][0] / 1000 * 30))
            # h3_p_58 = int(round((date_58[3][3] / date_58[3][0]), 2) * int(date_58[3][0] / 1000 * 30))
            # h2_p_58 = int(round((date_58[1][2] / date_58[1][0]), 2) * int(date_58[1][0] / 1000 * 30))
            # h2_p1_58 = int(round((date_58[3][2] / date_58[3][0]), 2) * int(date_58[3][0] / 1000 * 30))
            # h1_p1_58 = int(round((date_58[2][1] / date_58[2][0]), 2) * int(date_58[2][0] / 1000 * 30))
            # h3_p1_58 = int(round((date_58[1][3] / date_58[1][0]), 2) * int(date_58[1][0] / 1000 * 30))
            # h3_p2_58 = int(round((date_58[2][3] / date_58[2][0]), 2) * int(date_58[2][0] / 1000 * 30))
            #
            # h1_p_75 = int(round((date_75[3][1] / date_75[3][0]), 2) * int(date_75[3][0] / 1000 * 30))
            # h3_p_75 = int(round((date_75[3][3] / date_75[3][0]), 2) * int(date_75[3][0] / 1000 * 30))
            # h2_p_75 = int(round((date_75[1][2] / date_75[1][0]), 2) * int(date_75[1][0] / 1000 * 30))
            # h2_p1_75 = int(round((date_75[3][2] / date_75[3][0]), 2) * int(date_75[3][0] / 1000 * 30))
            # h1_p1_75 = int(round((date_75[2][1] / date_75[2][0]), 2) * int(date_75[2][0] / 1000 * 30))
            # h3_p1_75 = int(round((date_75[1][3] / date_75[1][0]), 2) * int(date_75[1][0] / 1000 * 30))
            # h3_p2_75 = int(round((date_75[2][3] / date_75[2][0]), 2) * int(date_75[2][0] / 1000 * 30))
            #
            # h1_p_77 = int(round((date_77[3][1] / date_77[3][0]), 2) * int(date_77[3][0] / 1000 * 30))
            # h3_p_77= int(round((date_77[3][3] / date_77[3][0]), 2) * int(date_77[3][0] / 1000 * 30))
            # h2_p_77 = int(round((date_77[1][2] / date_77[1][0]), 2) * int(date_77[1][0] / 1000 * 30))
            # h2_p1_77 = int(round((date_77[3][2] / date_77[3][0]), 2) * int(date_77[3][0] / 1000 * 30))
            # h1_p1_77 = int(round((date_77[2][1] / date_77[2][0]), 2) * int(date_77[2][0] / 1000 * 30))
            # h3_p1_77 = int(round((date_77[1][3] / date_77[1][0]), 2) * int(date_77[1][0] / 1000 * 30))
            # h3_p2_77 = int(round((date_77[2][3] / date_77[2][0]), 2) * int(date_77[2][0] / 1000 * 30))
            #
            # h1_p_89 = int(round((date_89 [3][1] / date_77[3][0]), 2) * int(date_89 [3][0] / 1000 * 30))
            # h3_p_89  = int(round((date_89 [3][3] / date_77[3][0]), 2) * int(date_89 [3][0] / 1000 * 30))
            # h2_p_89  = int(round((date_89 [1][2] / date_77[1][0]), 2) * int(date_89 [1][0] / 1000 * 30))
            # h2_p1_89  = int(round((date_89 [3][2] / date_77[3][0]), 2) * int(date_89 [3][0] / 1000 * 30))
            # h1_p1_89  = int(round((date_89 [2][1] / date_77[2][0]), 2) * int(date_89 [2][0] / 1000 * 30))
            # h3_p1_89  = int(round((date_89 [1][3] / date_77[1][0]), 2) * int(date_89 [1][0] / 1000 * 30))
            # h3_p2_89  = int(round((date_89 [2][3] / date_77[2][0]), 2) * int(date_89 [2][0] / 1000 * 30))
            #
            # r = 1
            # test1_23, test2_23, h1_1_23, h2_1_23, h3_1_23 = pointcalculate_clockwisetest(0.15, 0.15, 0.15 + round(date_23[0][1] / size, 2) * 0.05,
            #                                                           0.15 + round(date_23[0][1] // size, 2) * 0.05, r, 0, 2, 4,
            #                                                           date_23[0], 1, 0.5, 0.5)
            # test3_23, test4_23, h1_2_23, h2_2_23, h3_2_23 = pointcalculate_clockwisetest(-0.03 - round(date_23[0][2] // size, 2) * 0.05, 0, -0.03, 0,
            #                                                               r, h2_p_23, 2, 3, date_23[0], 1, 0.5, 0.5)
            # test5_23, test6_23, h1_3_23, h2_3_23, h3_3_23 = pointcalculate_clockwisetest(-0.2 - round(date_23[0][3] // size, 2) * 0.05,
            #                                                               0.2 + round(date_23[0][3] // size, 2) * 0.05, -0.2, 0.2, r,
            #                                                               h3_p1_23 + h3_p2_23, 2, 2, date_23[0], 1, 0.5, 0.5)
            #
            # test7_23, test8_23, h1_4_23, h2_4_23, h3_4_23 = pointcalculate_clockwisetest(0.15 - round(date_23[1][2] // size, 2) * 0.05,
            #                                                               -0.15 + round(date_23[1][2] // size, 2) * 0.05, 0.15, -0.15,
            #                                                               r, 0, 1, 3, date_23[1], 1, 0.5, 0.5)
            # test9_23, test10_23, h1_5_23, h2_5_23, h3_5_23 = pointcalculate_clockwisetest(0, 0.03 + round(date_23[1][3] // size, 2) * 0.05, 0, 0.03,
            #                                                                r, h3_p2_23, 1, 2, date_23[1], 1, 0.5, 0.5)
            # test11_23, test12_23, h1_6_23, h2_6_23, h3_6_23 = pointcalculate_clockwisetest(0.2 + round(date_23[1][1] // size, 2) * 0.05,
            #                                                                 0.2 + round(date_23[1][1] // size, 2) * 0.05, 0.2, 0.2, r,
            #                                                                 h1_p_23 + h1_p1_23, 1, 1, date_23[1], 1, 0.5, 0.5)
            #
            # test13, test14, h1_7, h2_7, h3_7 = pointcalculate_clockwisetest(-0.15, -0.15,
            #                                                                 -0.15 - round(date_23[2][3] // size, 2) * 0.05,
            #                                                                 -0.15 - round(date_23[2][3] // size, 2) * 0.05, r, 0, 4, 2,
            #                                                                 date_23[2], 1, 0.5, 0.5)
            # test15, test16, h1_8, h2_8, h3_8 = pointcalculate_clockwisetest(0.03 + round(date_23[2][1] // size, 2) * 0.05, 0, 0.03, 0,
            #                                                                 r, h1_p_23, 4, 1, date_23[2], 1, 0.5, 0.5)
            # test17, test18, h1_9, h2_9, h3_9 = pointcalculate_clockwisetest(0.2 + round(date_23[2][2] // size, 2) * 0.05,
            #                                                                 -0.2 - round(date_23[2][2] // size, 2) * 0.05, 0.2, -0.2,
            #                                                                 r, h1_1_23 + h2_p1_23, 4, 4, date_23[2], 1, 0.5, 0.5)
            #
            # test19, test20, h1_10, h2_10, h3_10 = pointcalculate_clockwisetest(-0.15, 0.15,
            #                                                                    -0.15 - round(date_23[3][1] // size, 2) * 0.05,
            #                                                                    0.15 + round(date_23[3][1] // size, 2) * 0.05, r, 0, 3,
            #                                                                    1, date_23[3], 1, 0.5, 0.5)
            # test21, test22, h1_11, h2_11, h3_11 = pointcalculate_clockwisetest(0, -0.03 - round(date_23[3][2] // size, 2) * 0.05, 0,
            #                                                                    -0.03, r, h1_1_23, 3, 4, date_23[3], 1, 0.5, 0.5)
            # # test23,test24,h1_12,h2_12,h3_12=pointcalculate_clockwisetest(-0.4,-0.4,-0.3,-0.3,r,h2_2+h2_4,3,3,date[3],1,0.5,0.5)
            # test23, test24, h1_12, h2_12, h3_12 = pointcalculate_clockwisetest(-0.2 - round(date_23[3][3] // size, 2) * 0.05,
            #                                                                    -0.2 - round(date_23[3][3] // size, 2) * 0.05, -0.2,
            #                                                                    -0.2, r, h2_4_23 + h2_1_23, 3, 3, date[3]_23, 1, 0.5, 0.5)

            def pathmaker(a, b, c, d, ax):  # a:点组，b：路劲组，c：颜色参数
                if len(a) != 0:
                    path = Path(a, b)
                    patch = patches.PathPatch(path, facecolor=c, alpha=0.8, edgecolor=d)
                    ax.add_patch(patch)

            def outcyclemakerblack(a, t, r1, r2):  # a：总的弧长，t：相位 r:半径,point:点阵
                pointgroup = []
                codegroup = []
                pointgroup1 = []
                codegroup1 = []
                pointgroup2 = []
                codegroup2 = []
                if a != 0:

                    if t == 1:
                        originx = (math.pi / (180 / (1)))
                        originx1 = r1 * math.cos(originx)
                        originy1 = r1 * math.sin(originx)
                        pointgroup1.append((originx1, originy1))
                        codegroup1.append(Path.MOVETO)
                        for i in range(a - 1):
                            x = (math.pi / (180 / (i + 2)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)
                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                    elif t == 2:
                        originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                        originx1 = r1 * math.cos(originx)
                        originy1 = r1 * math.sin(originx)
                        pointgroup1.append((originx1, originy1))
                        codegroup1.append(Path.MOVETO)
                        for i in range(a - 1):
                            x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = 0.5 * math.pi + (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                    elif t == 3:
                        originx = 1 * math.pi + (math.pi / (180 / (1)))
                        originx1 = r1 * math.cos(originx)
                        originy1 = r1 * math.sin(originx)
                        pointgroup1.append((originx1, originy1))
                        codegroup1.append(Path.MOVETO)
                        for i in range(a - 1):
                            x = 1 * math.pi + (math.pi / (180 / (i + 2)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = 1 * math.pi + (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                    elif t == 4:
                        originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                        originx1 = r1 * math.cos(originx)
                        originy1 = r1 * math.sin(originx)
                        pointgroup1.append((originx1, originy1))
                        codegroup1.append(Path.MOVETO)
                        for i in range(a - 1):
                            x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = 1.5 * math.pi + (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                return pointgroup, codegroup

                # a：总的弧长，t：相位 r:半径,point:点阵

            def outcyclemakergray(a, t, r1, r2):
                pointgroup = []
                codegroup = []
                pointgroup1 = []
                codegroup1 = []
                pointgroup2 = []
                codegroup2 = []
                if a != 0:

                    if t == 1:

                        codegroup1.append(Path.MOVETO)
                        for i in range(a):
                            x = 0.5 * math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = 0.5 * math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                    elif t == 2:
                        codegroup1.append(Path.MOVETO)
                        for i in range(a):
                            x = math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                    elif t == 3:
                        codegroup1.append(Path.MOVETO)
                        for i in range(a):
                            x = 1.5 * math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = 1.5 * math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                    elif t == 4:
                        codegroup1.append(Path.MOVETO)
                        for i in range(a):
                            x = 2 * math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r1 * math.cos(x)
                            y1 = r1 * math.sin(x)
                            pointgroup1.append((x1, y1))
                        for i in range(a - 1):
                            codegroup1.append(Path.LINETO)

                        for i in range(a):
                            x = 2 * math.pi - (math.pi / (180 / (i + 1)))
                            x1 = r2 * math.cos(x)
                            y1 = r2 * math.sin(x)
                            pointgroup2.append((x1, y1))
                        for i in range(a):
                            codegroup2.append(Path.LINETO)

                        pointgroup2.reverse()
                        pointgroup.extend(pointgroup1)
                        # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                        pointgroup.append(pointgroup2[0])
                        pointgroup.extend(pointgroup2)
                        # pointgroup.append(pointgroup2[0])
                        pointgroup.append(pointgroup1[0])
                        codegroup.extend(codegroup1)
                        codegroup.append(Path.LINETO)
                        codegroup.extend(codegroup2)
                        # codegroup.append(Path.LINETO)
                        codegroup.append(Path.LINETO)
                return pointgroup, codegroup

            def roadnamemaker(a):
                if a == 23:
                    s = '23.东环大道枫南路路口'
                elif a == 24:
                    s = '24.机场路枫南路路口'
                elif a == 55:
                    s = '55.市府大道白云山中路路口'
                elif a == 56:
                    s = '56.市府大道东环大道路口'
                elif a == 57:
                    s = '57.市府大道经中路路口'
                elif a == 58:
                    s = '58.市府大道机场路路口'
                elif a == 75:
                    s = '75.东环大道开元路路口'
                elif a == 77:
                    s = '77.东环大道康平路路口'
                elif a == 89:
                    s = '89.机场路开元路'
                return s

            def automakershow(a):
                fig = plt.figure()
                # canvas = FigureCanvas(fig)
                ax = fig.add_subplot(111)

                daycarlist = newdayperiodreadlist(a)
                print(" 读取"+str(a)+"路口当前时间段数据库完成 %s" % ctime())
                idtsclane = getidtsclane(tsclane, a)
                print(" 读取"+str(a)+"选择路口渠化信息完成 %s" % ctime())
                lend0, lend2, lend4, lend6 = sidnumcalculate(idtsclane)
                flowgroup = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist, idtsclane,
                                                                                               lend0, lend2, lend4,
                                                                                               lend6)
                #flowsize = max(flowgroup[0][0], flowgroup[1][0], flowgroup[2][0], flowgroup[3][0])
                flowsize=1500
                date = flowgroup
                k = 30
                k1 = 30
                r = 1
                size = 400
                h1_p = int(round((date[3][1] / date[3][0]), 2) * int(date[3][0] / flowsize * 40))
                h3_p = int(round((date[3][3] / date[3][0]), 2) * int(date[3][0] / flowsize * 40))
                h2_p = int(round((date[1][2] / date[1][0]), 2) * int(date[1][0] / flowsize * 40))
                h2_p1 = int(round((date[3][2] / date[3][0]), 2) * int(date[3][0] / flowsize * 40))
                h1_p1 = int(round((date[2][1] / date[2][0]), 2) * int(date[2][0] / flowsize * 40))
                h3_p1 = int(round((date[1][3] / date[1][0]), 2) * int(date[1][0] / flowsize * 40))
                h3_p2 = int(round((date[2][3] / date[2][0]), 2) * int(date[2][0] / flowsize * 40))

                test1, test2, h1_1, h2_1, h3_1 = pointcalculate_clockwisetest(0.15, 0.15,
                                                                              0.15 + round(date[0][1] / size, 2) * 0.05,
                                                                              0.15 + round(date[0][1] // size,
                                                                                           2) * 0.05, r, 0,
                                                                              2, 4, date[0], 1, 0.5, 0.5, flowsize)
                test3, test4, h1_2, h2_2, h3_2 = pointcalculate_clockwisetest(
                    -0.03 - round(date[0][2] // size, 2) * 0.05, 0,
                    -0.03, 0, r, h2_p, 2, 3, date[0], 1, 0.5, 0.5, flowsize)
                test5, test6, h1_3, h2_3, h3_3 = pointcalculate_clockwisetest(
                    -0.2 - round(date[0][3] // size, 2) * 0.05,
                    0.2 + round(date[0][3] // size, 2) * 0.05, -0.2,
                    0.2, r, h3_p1 + h3_p2, 2, 2, date[0], 1, 0.5, 0.5, flowsize)

                test7, test8, h1_4, h2_4, h3_4 = pointcalculate_clockwisetest(
                    0.15 - round(date[1][2] // size, 2) * 0.05,
                    -0.15 + round(date[1][2] // size, 2) * 0.05, 0.15,
                    -0.15, r, 0, 1, 3, date[1], 1, 0.5, 0.5, flowsize)
                test9, test10, h1_5, h2_5, h3_5 = pointcalculate_clockwisetest(0, 0.03 + round(date[1][3] // size,
                                                                                               2) * 0.05, 0,
                                                                               0.03, r, h3_p2, 1, 2, date[1], 1, 0.5,
                                                                               0.5, flowsize)
                test11, test12, h1_6, h2_6, h3_6 = pointcalculate_clockwisetest(
                    0.2 + round(date[1][1] // size, 2) * 0.05,
                    0.2 + round(date[1][1] // size, 2) * 0.05, 0.2,
                    0.2, r, h1_p + h1_p1, 1, 1, date[1], 1, 0.5,
                    0.5, flowsize)

                test13, test14, h1_7, h2_7, h3_7 = pointcalculate_clockwisetest(-0.15, -0.15,
                                                                                -0.15 - round(date[2][3] // size,
                                                                                              2) * 0.05,
                                                                                -0.15 - round(date[2][3] // size,
                                                                                              2) * 0.05, r,
                                                                                0, 4, 2, date[2], 1, 0.5, 0.5, flowsize)
                test15, test16, h1_8, h2_8, h3_8 = pointcalculate_clockwisetest(
                    0.03 + round(date[2][1] // size, 2) * 0.05, 0,
                    0.03, 0, r, h1_p, 4, 1, date[2], 1, 0.5, 0.5, flowsize)
                test17, test18, h1_9, h2_9, h3_9 = pointcalculate_clockwisetest(
                    0.2 + round(date[2][2] // size, 2) * 0.05,
                    -0.2 - round(date[2][2] // size, 2) * 0.05, 0.2,
                    -0.2, r, h1_1 + h2_p1, 4, 4, date[2], 1, 0.5,
                    0.5, flowsize)

                test19, test20, h1_10, h2_10, h3_10 = pointcalculate_clockwisetest(-0.15, 0.15,
                                                                                   -0.15 - round(date[3][1] // size,
                                                                                                 2) * 0.05,
                                                                                   0.15 + round(date[3][1] // size,
                                                                                                2) * 0.05,
                                                                                   r, 0, 3, 1, date[3], 1, 0.5, 0.5,
                                                                                   flowsize)
                test21, test22, h1_11, h2_11, h3_11 = pointcalculate_clockwisetest(0,
                                                                                   -0.03 - round(date[3][2] // size,
                                                                                                 2) * 0.05,
                                                                                   0, -0.03, r, h1_1, 3, 4, date[3], 1,
                                                                                   0.5,
                                                                                   0.5, flowsize)
                # test23,test24,h1_12,h2_12,h3_12=pointcalculate_clockwisetest(-0.4,-0.4,-0.3,-0.3,r,h2_2+h2_4,3,3,date[3],1,0.5,0.5)
                test23, test24, h1_12, h2_12, h3_12 = pointcalculate_clockwisetest(
                    -0.2 - round(date[3][3] // size, 2) * 0.05,
                    -0.2 - round(date[3][3] // size, 2) * 0.05,
                    -0.2, -0.2, r, h2_4 + h2_1, 3, 3, date[3], 1,
                    0.5, 0.5, flowsize)

                testout1, testout2 = outcyclemakerblack(h1_4 + h2_4 + h3_4, 1, 1.1, 1)
                testout3, testout4 = outcyclemakerblack(h1_1 + h2_1 + h3_1, 2, 1.1, 1)
                testout5, testout6 = outcyclemakerblack(h1_10 + h2_10 + h3_10, 3, 1.1, 1)
                testout7, testout8 = outcyclemakerblack(h1_7 + h2_7 + h3_7, 4, 1.1, 1)

                testout9, testout10 = outcyclemakergray(h1_4 + h1_7 + h1_10, 1, 1.1, 1)
                testout11, testout12 = outcyclemakergray(h1_1 + h2_7 + h2_10, 4, 1.1, 1)
                testout13, testout14 = outcyclemakergray(h2_1 + h2_4 + h3_10, 3, 1.1, 1)
                testout15, testout16 = outcyclemakergray(h3_1 + h3_4 + h3_7, 2, 1.1, 1)

                pathmaker(testout1, testout2, 'black', 'black', ax)
                pathmaker(testout3, testout4, 'black', 'black', ax)
                pathmaker(testout5, testout6, 'black', 'black', ax)
                pathmaker(testout7, testout8, 'black', 'black', ax)

                pathmaker(testout9, testout10, 'gray', 'gray', ax)
                pathmaker(testout11, testout12, 'gray', 'gray', ax)
                pathmaker(testout13, testout14, 'gray', 'gray', ax)
                pathmaker(testout15, testout16, 'gray', 'gray', ax)
                pathmaker(test1, test2, 'seagreen', 'seagreen', ax)
                pathmaker(test3, test4, 'seagreen', 'seagreen', ax)
                pathmaker(test5, test6, 'seagreen', 'seagreen', ax)

                pathmaker(test7, test8, 'orange', 'orange', ax)
                pathmaker(test9, test10, 'orange', 'orange', ax)
                pathmaker(test11, test12, 'orange', 'orange', ax)

                pathmaker(test13, test14, 'salmon', 'salmon', ax)
                pathmaker(test15, test16, 'salmon', 'salmon', ax)
                pathmaker(test17, test18, 'salmon', 'salmon', ax)

                pathmaker(test19, test20, 'skyblue', 'skyblue', ax)
                pathmaker(test21, test22, 'skyblue', 'skyblue', ax)
                pathmaker(test23, test24, 'skyblue', 'skyblue', ax)

                ax.set_xlim(-2, 2)
                ax.set_ylim(-2, 2)
                ax.set_xticks([])
                ax.set_yticks([])
                s = roadnamemaker(a)
                plt.text(0, 0, s, horizontalalignment='center', va='center', fontsize='18')
                ax.set_aspect('equal')
                ax.set_frame_on(False)
                # plt.imshow()
                # canvas.print_figure('demo.png',bbox_inches='tight',transparent=True)
                path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
                plt.savefig(path+"\static\images\_mappicture/" + str(a) +'_'+str(ran)+ '.png', bbox_inches='tight',
                            transparent=True, dpi=58)
                plt.close()
                # s="F:\pythonwork\jiaotongweb"+"\"+
                # shutil.copy("F:\pythonwork\jiaotongweb\examples.jpg", "F:\pythonwork\jiaotongweb\chart\static")
                # canvas.print_figure('demo.jpg')

            automakershow(23)
            automakershow(24)
            automakershow(55)
            automakershow(56)
            automakershow(57)
            automakershow(58)
            automakershow(75)
            automakershow(77)
            automakershow(89)





    else:

        sectorpicture_form = SectordiagramForm();
        context['sectorpicture_form'] = sectorpicture_form

    n = sectordiagram.objects.get(id=1)
    date1 = str(n.originyear) + '.' + str(n.originmonth) + '.' + str(n.originday)+' '+str(n.originhour)+':'+str(n.originmin)+':0'
    date2 = str(n.endyear) + '.' + str(n.endmonth) + '.' + str(n.endday) + ' '  +str(n.endhour)+':'+str(n.endmin)+':59'
    context['date1'] = date1
    context['date2'] = date2
    context['p23'] = "/static/images/_mappicture/" + str(23) +'_'+str(ran)+ '.png'
    context['p24'] = "/static/images/_mappicture/" + str(24)+'_' + str(ran) + '.png'
    context['p55'] = "/static/images/_mappicture/" + str(55) +'_'+ str(ran) + '.png'
    context['p56'] = "/static/images/_mappicture/" + str(56) +'_'+ str(ran) + '.png'
    context['p57'] = "/static/images/_mappicture/" + str(57) +'_'+ str(ran) + '.png'
    context['p58'] = "/static/images/_mappicture/" + str(58) +'_'+ str(ran) + '.png'
    context['p75'] = "/static/images/_mappicture/" + str(75) +'_'+ str(ran) + '.png'
    context['p77'] = "/static/images/_mappicture/" + str(77) +'_'+ str(ran) + '.png'
    context['p89'] = "/static/images/_mappicture/" + str(89)+'_' + str(ran) + '.png'
    context['netname123'] = "/static/images/_flowchart/examples" + str(ran) + ".jpg"
    print(context['p23'])

    return render(resquest, 'mapbase.html', context)



def sectorShow_picture(resquest):
    context = {}
    sectorpicture_form = SectordiagramForm();
    context['sectorpicture_form'] = sectorpicture_form;
    n = sectordiagram.objects.get(id=1)
    date1 = str(n.originyear) + '-' + str(n.originmonth) + '-' + str(n.originday) + ' ' + str(n.originhour) + ':' + str(
        n.originmin) + ':0'
    date2 = str(n.endyear) + '-' + str(n.endmonth) + '-' + str(n.endday) + ' ' + str(n.endhour) + ':' + str(
        n.endmin) + ':59'

    context['date1'] = date1
    context['date2'] = date2

    PictureData = [date1,date2]
    print(PictureData)

    def gettsclanelist():  # 读取渠化信息
        p = []
        results = Tsclane.objects.all()
        for row in results:
            if row.sid != 0:
                sid = row.sid
                movement = row.movement
                dircetion = row.direction
                intersectionld = row.intersectionid
                p.append([sid, movement, dircetion, intersectionld])
        return p

    tsclane = gettsclanelist()
    print("初始化完成 %s" % ctime())

    def newdayperiodreadlist(a):  # 读取路口数据存入列表 a b c年月日
        # y = str(y)
        # m = str(m)
        # d = str(d)
        # h = str(h)
        # min = str(min)
        # y1 = str(y1)
        # m1 = str(m1)
        # d1 = str(d1)
        # h1 = str(h1)
        # min1 = str(min1 - 1)
        #
        # t5 = y + '-' + m + '-' + d + ' ' + h + ':' + min + ':0'
        # t6 = y1 + '-' + m1 + '-' + d1 + ' ' + h1 + ':' + min1 + ':59'

        car = []
        results = []

        if a == 23:
            results = I023.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 24:
            results = I024.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 55:
            results = I055.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 56:
            results = I056.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 57:
            results = I057.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 58:
            results = I058.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 75:
            results = I075.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 77:
            results = I077.objects.filter(passtime__lte=date2,passtime__gte=date1)
        elif a == 89:
            results = I089.objects.filter(passtime__lte=date2,passtime__gte=date1)
        else:
            results = []


        #print(len(results))
        #print(results)

        for rowa in results:
            id = rowa.id
            inteid = rowa.inteid
            direction = rowa.direction
            lane = rowa.lane
            carplate = rowa.carplate
            passtime = rowa.passtime
            traveltime = rowa.traveltime
            upinteid = rowa.upinteid
            updirection = rowa.updirection
            uplane = rowa.uplane
            car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection, uplane])
        return car
    # daycarlist_23=newdayperiodreadlist(23)
    # daycarlist_24 = newdayperiodreadlist(24)
    # daycarlist_55 = newdayperiodreadlist(55)
    # daycarlist_56 = newdayperiodreadlist(56)
    # daycarlist_57 = newdayperiodreadlist(57)
    # daycarlist_58 = newdayperiodreadlist(58)
    # daycarlist_75 = newdayperiodreadlist(75)
    # daycarlist_77 = newdayperiodreadlist(77)
    # daycarlist_89 = newdayperiodreadlist(89)
    #print(" 读取路口当前时间段数据库完成 %s" % ctime())

    def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
        t = []
        for row in a:
            if row[3] == b:
                t.append(row)
        return t


    # idtsclane_23 = getidtsclane(tsclane, 23)
    # idtsclane_24 = getidtsclane(tsclane, 24)
    # idtsclane_55 = getidtsclane(tsclane, 55)
    # idtsclane_56 = getidtsclane(tsclane, 56)
    # idtsclane_57 = getidtsclane(tsclane, 57)
    # idtsclane_58 = getidtsclane(tsclane, 58)
    # idtsclane_75 = getidtsclane(tsclane, 75)
    # idtsclane_77 = getidtsclane(tsclane, 77)
    # idtsclane_89 = getidtsclane(tsclane, 89)

    #print(" 读取选择路口渠化信息完成 %s" % ctime())

    def sidnumcalculate(a):  # 根据渠化信息得到车辆转向的路口,a渠化信息
        sid = 0
        d0 = []
        d2 = []
        d4 = []
        d6 = []
        for row in a:  # 得到各个direcition lane的个数
            if row[2] == 0:
                d0.append(row)
            elif row[2] == 2:
                d2.append(row)
            elif row[2] == 4:
                d4.append(row)
            elif row[2] == 6:
                d6.append(row)
        return len(d0), len(d2), len(d4), len(d6)

    # lend0_23, lend2_23, lend4_23, lend6_23 = sidnumcalculate(idtsclane_23)
    # lend0_24, lend2_24, lend4_24, lend6_24 = sidnumcalculate(idtsclane_24)
    # lend0_55, lend2_55, lend4_55, lend6_55 = sidnumcalculate(idtsclane_55)
    # lend0_56, lend2_56, lend4_56, lend6_56 = sidnumcalculate(idtsclane_56)
    # lend0_57, lend2_57, lend4_57, lend6_57 = sidnumcalculate(idtsclane_57)
    # lend0_58, lend2_58, lend4_58, lend6_58 = sidnumcalculate(idtsclane_58)
    # lend0_75, lend2_75, lend4_75, lend6_75 = sidnumcalculate(idtsclane_75)
    # lend0_77, lend2_77, lend4_77, lend6_77 = sidnumcalculate(idtsclane_77)
    # lend0_89, lend2_89, lend4_89, lend6_89 = sidnumcalculate(idtsclane_89)


    def movementdirectioncalculate(a, lend0, lend2, lend4, lend6, d, l):
        sid = 0
        movement = 0
        if d == 0:
            sid = l + lend6 + lend4 + lend2
        elif d == 2:
            sid = l + lend6 + lend4
        elif d == 4:
            sid = l + lend6
        elif d == 6:
            sid = l
        for row in a:
            if row[0] == sid:
                movement = row[1]
        return movement

    def turndirectioncalculate(a,b): #a路口id b：movement
        k=0
        if a==0:
            if b==1:
                k=6
            elif b==2:
                k=4
            elif b==3:
                k=2
            elif b==4: #直-右→右
                k=6
            elif b==5: #直-右-右→直
                k=4
            elif b==6: #直-左→左
                k=2
            elif b==7:  #左-掉头→掉头
                k=-999  #掉头
            elif b==8:  #右-左→右
                k=6
            elif b==9:
                k=-999
        elif a==2:
            if b==1: #右
                k=0
            elif b==2:#直
                k=6
            elif b==3:#左
                k=4
            elif b==4: #直-右→右
                k=0
            elif b==5: #直-右-右→直
                k=6
            elif b==6: #直-左→左
                k=4
            elif b==7:  #左-掉头→掉头
                k=-999  #掉头
            elif b==8:  #右-左→右
                k=0
            elif b==9:
                k=-999
        elif a==4:
            if b == 1:  # 右
                k = 2
            elif b == 2:  # 直
                k = 0
            elif b == 3:  # 左
                k = 6
            elif b == 4:  # 直-右→右
                k = 2
            elif b == 5:  # 直-右-右→直
                k = 0
            elif b == 6:  # 直-左→左
                k = 6
            elif b == 7:  # 左-掉头→掉头
                k = -999  # 掉头
            elif b == 8:  # 右-左→右
                k = 2
            elif b == 9:
                k = -999
        elif a==6:
            if b == 1:  # 右
                k = 4
            elif b == 2:  # 直
                k = 2
            elif b == 3:  # 左
                k = 0
            elif b == 4:  # 直-右→右
                k = 4
            elif b == 5:  # 直-右-右→直
                k = 2
            elif b == 6:  # 直-左→左
                k = 0
            elif b == 7:  # 左-掉头→掉头
                k = -999  # 掉头
            elif b == 8:  # 右-左→右
                k = 4
            elif b == 9:
                k = -999
        return k

    def flowcalculate(a):
        if len(a)!=0:
            num = len(a)
            timeArray1 = time.strptime(str(a[0][5]), "%Y-%m-%d %H:%M:%S")
            utctime1 = int(time.mktime(timeArray1))
            timeArray2 = time.strptime(str(a[len(a) - 1][5]), "%Y-%m-%d %H:%M:%S")
            utctime2 = int(time.mktime(timeArray2))
            utctime = utctime2 - utctime1
            inttime = utctime / 3600
            flow= round(num / inttime, 2)
        else:
            flow=0
        return flow

    def inflowcalculate(a, b,lend0,lend2,lend4,lend6):

        daycarlist_0 = []
        daycarlist_0to2 = []
        daycarlist_0to4 = []
        daycarlist_0to6 = []
        daycarlist_2 = []
        daycarlist_2to0 = []
        daycarlist_2to4 = []
        daycarlist_2to6 = []
        daycarlist_4 = []
        daycarlist_4to0 = []
        daycarlist_4to2 = []
        daycarlist_4to6 = []
        daycarlist_6 = []
        daycarlist_6to0 = []
        daycarlist_6to2 = []
        daycarlist_6to4 = []
        for row in a:
            if row[2] == 0:
                daycarlist_0.append(row)
            elif row[2] == 2:
                daycarlist_2.append(row)
            elif row[2] == 4:
                daycarlist_4.append(row)
            elif row[2] == 6:
                daycarlist_6.append(row)

        if len(daycarlist_0) != 0:
            for row in daycarlist_0:
                movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                k = turndirectioncalculate(0, movement)
                if k == 2:
                    daycarlist_0to2.append(row)
                elif k == 4:
                    daycarlist_0to4.append(row)
                elif k == 6:
                    daycarlist_0to6.append(row)
            flow_0 = flowcalculate(daycarlist_0)
            flow_0to2 = flowcalculate(daycarlist_0to2)
            flow_0to4 = flowcalculate(daycarlist_0to4)
            flow_0to6 = flowcalculate(daycarlist_0to6)
        else:
            flow_0, flow_0to2, flow_0to4, flow_0to6 = 1, 0, 0, 0

        if len(daycarlist_2) != 0:
            for row in daycarlist_2:
                movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                k = turndirectioncalculate(2, movement)
                if k == 0:
                    daycarlist_2to0.append(row)
                elif k == 4:
                    daycarlist_2to4.append(row)
                elif k == 6:
                    daycarlist_2to6.append(row)
            flow_2 = flowcalculate(daycarlist_2)
            flow_2to0 = flowcalculate(daycarlist_2to0)
            flow_2to4 = flowcalculate(daycarlist_2to4)
            flow_2to6 = flowcalculate(daycarlist_2to6)
        else:
            flow_2, flow_2to0, flow_2to4, flow_2to6 = 1, 0, 0, 0
        if len(daycarlist_4) != 0:
            for row in daycarlist_4:
                movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                k = turndirectioncalculate(4, movement)
                if k == 0:
                    daycarlist_4to0.append(row)
                elif k == 2:
                    daycarlist_4to2.append(row)
                elif k == 6:
                    daycarlist_4to6.append(row)
            flow_4 = flowcalculate(daycarlist_4)
            flow_4to0 = flowcalculate(daycarlist_4to0)
            flow_4to2 = flowcalculate(daycarlist_4to2)
            flow_4to6 = flowcalculate(daycarlist_4to6)
        else:
            flow_4, flow_4to0, flow_4to2, flow_4to6 = 1, 0, 0, 0

        if len(daycarlist_6) != 0:
            for row in daycarlist_6:
                movement = movementdirectioncalculate(b, lend0, lend2, lend4, lend6, row[2], row[3])
                k = turndirectioncalculate(6, movement)
                if k == 0:
                    daycarlist_6to0.append(row)
                elif k == 2:
                    daycarlist_6to2.append(row)
                elif k == 4:
                    daycarlist_6to4.append(row)
            flow_6 = flowcalculate(daycarlist_6)
            flow_6to0 = flowcalculate(daycarlist_6to0)
            flow_6to2 = flowcalculate(daycarlist_6to2)
            flow_6to4 = flowcalculate(daycarlist_6to4)
        else:
            flow_6, flow_6to0, flow_6to2, flow_6to4 = 1, 0, 0, 0

        return [flow_0, flow_0to2, flow_4, flow_0to6], [flow_2, flow_2to0, flow_2to4, flow_2to6], [flow_4, flow_4to0,
                                                                                                   flow_4to2,
                                                                                                   flow_4to6], [flow_6,
                                                                                                                flow_6to0,
                                                                                                                flow_6to2,
                                                                                                                flow_6to4]


    # flowgroup_23 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_23, idtsclane_23,lend0_23,lend2_23,lend4_23,lend6_23)
    # flowgroup_24 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_24, idtsclane_24,
    #                                                                                   lend0_24, lend2_24, lend4_24,
    #                                                                                   lend6_24)
    # flowgroup_55 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_55, idtsclane_55,
    #                                                                                   lend0_55, lend2_55, lend4_55,
    #                                                                                   lend6_55)
    # flowgroup_56 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_56, idtsclane_56,
    #                                                                                   lend0_56, lend2_56, lend4_56,
    #                                                                                   lend6_56)
    # flowgroup_57 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_57, idtsclane_57,
    #                                                                                   lend0_57, lend2_57, lend4_57,
    #                                                                                   lend6_57)
    # flowgroup_58 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_58, idtsclane_58,
    #                                                                                   lend0_58, lend2_58, lend4_58,
    #                                                                                   lend6_58)
    # flowgroup_75 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_75, idtsclane_75,
    #                                                                                   lend0_75, lend2_75, lend4_75,
    #                                                                                   lend6_75)
    # flowgroup_77 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_77, idtsclane_77,
    #                                                                                   lend0_77, lend2_77, lend4_77,
    #                                                                                   lend6_77)
    # flowgroup_89 = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist_89, idtsclane_89,
    #                                                                                   lend0_89, lend2_89, lend4_89,
    #                                                                                   lend6_89)

    mpl.rcParams['font.sans-serif'] = ['SimHei']

    # fig_23 = plt.figure()
    # fig_24 = plt.figure()
    # fig_55 = plt.figure()
    # fig_56 = plt.figure()
    # fig_57 = plt.figure()
    # fig_58 = plt.figure()
    # fig_75 = plt.figure()
    # fig_77 = plt.figure()
    # fig_89 = plt.figure()
    #
    # ax_23 = fig_23.add_subplot(111)
    # ax_24 = fig_24.add_subplot(111)
    # ax_55 = fig_55.add_subplot(111)
    # ax_56 = fig_56.add_subplot(111)
    # ax_57 = fig_57.add_subplot(111)
    # ax_58 = fig_58.add_subplot(111)
    # ax_75 = fig_75.add_subplot(111)
    # ax_77 = fig_77.add_subplot(111)
    # ax_89 = fig_89.add_subplot(111)
    #
    #
    # date_23 = flowgroup_23
    # date_24 = flowgroup_24
    # date_55 = flowgroup_55
    # date_56 = flowgroup_56
    # date_57 = flowgroup_57
    # date_58 = flowgroup_58
    # date_75 = flowgroup_75
    # date_77 = flowgroup_77
    # date_89 = flowgroup_89


    def pointcalculate_clockwisetest(c1, d1, c2, d2, r, p, t1, t2, date, type, tb1,
                                     tb2,flowsize):  # c1 ,d1,c2,d2:两条贝塞尔曲线的中间点，r：半径，p：补偿角，t1:：起点相位，t2：终点相位，date：数据，type：类型，tb1，tb2：bellse的参数t
        pointgroup = []
        codegroup = []
        h1 = 0
        h2 = 0
        h3 = 0
        if type == 1:

            if date[0] != -999:
                pointgroup = []
                pointgroup1 = []
                pointgroup2 = []
                pointgroup3 = []
                pointgroup4 = []
                codegroup = []
                codegroup1 = []
                codegroup2 = []
                codegroup3 = []
                codegroup4 = []

                h1 = int(round((date[1] / date[0]), 2) * int(date[0] / flowsize * 40))
                # h2=int(date[0]/1000*30)-h1
                h2 = int(round((date[2] / date[0]), 2) * int(date[0] / flowsize * 40))
                h3 = int(round((date[3] / date[0]), 2) * int(date[0] / flowsize * 40))
                # pointgroup.append(origin)
                # codegroup.append(Path.MOVETO)
                if t1 == 1:
                    if t2 == 1:
                        if h1 != 0:
                            originx = (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h1 + h2 + h3 - 1):
                                x = (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h2 + h3:len(pointgroup1)]
                            for i in range(h1 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h1):
                                x = 0.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h1):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 2:
                        if h3 != 0:
                            originx = (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h2 + h3 - 1):
                                x = (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h2:len(pointgroup1)]
                            for i in range(h3 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h3):
                                x = math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h3):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 3:
                        if h2 != 0:
                            originx = (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h2 - 1):
                                x = (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            # pointgroup1=pointgroup1[h1:len(pointgroup1)]
                            for i in range(h2 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h2):
                                x = 1.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h2):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 4:
                        123
                elif t1 == 2:
                    if t2 == 1:
                        123
                    elif t2 == 2:
                        if h3 != 0:
                            originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup.append(Path.MOVETO)
                            for i in range(h1 + h2 + h3 - 1):
                                x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h1 + h2:len(pointgroup1)]
                            for i in range(h3 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h3):
                                x = math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h3):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 3:
                        if h2 != 0:
                            originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup.append(Path.MOVETO)
                            for i in range(h1 + h2 - 1):
                                x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h1:len(pointgroup1)]
                            for i in range(h2 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h2):
                                x = 1.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h2):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 4:
                        if h1 != 0:
                            originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup.append(Path.MOVETO)
                            for i in range(h1 - 1):
                                x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            for i in range(h1 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h1):
                                x = 2 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h1):
                                codegroup3.append(Path.LINETO)
                            x1 = (c1 - numpy.square(1 - tb1) * pointgroup1[h1 - 1][0] - numpy.square(tb1) *
                                  pointgroup3[h1 - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (d1 - numpy.square(1 - tb1) * pointgroup1[h1 - 1][1] - numpy.square(tb1) *
                                  pointgroup3[h1 - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[h1 - 1], (x1, y1), pointgroup3[h1 - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)

                elif t1 == 3:
                    if t2 == 1:
                        if h1 != 0:
                            originx = math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h1 - 1):
                                x = math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                                # pointgroup1 = pointgroup1[h3:len(pointgroup1)]
                            for i in range(h1 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h1):
                                x = 0.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h1):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 2:
                        123
                    elif t2 == 3:
                        if h3 != 0:
                            originx = math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h1 + h2 + h3 - 1):
                                x = math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h2 + h1:len(pointgroup1)]
                            for i in range(h3 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h3):
                                x = 1.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h3):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 4:
                        if h2 != 0:
                            originx = math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h2 + h1 - 1):
                                x = math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h1:len(pointgroup1)]
                            for i in range(h2 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h2):
                                x = 2 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h2):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                elif t1 == 4:
                    if t2 == 1:
                        if h1 != 0:
                            originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h1 + h3 - 1):
                                x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h3:len(pointgroup1)]
                            for i in range(h1 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h1):
                                x = 0.5 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h1):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 2:
                        if h3 != 0:
                            originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h3 - 1):
                                x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                                # pointgroup1 = pointgroup1[h2:len(pointgroup1)]
                            for i in range(h3 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h3):
                                x = math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h3):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
                    elif t2 == 3:
                        123
                    elif t2 == 4:
                        if h2 != 0:
                            originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                            originx1 = r * math.cos(originx)
                            originy1 = r * math.sin(originx)
                            pointgroup1.append((originx1, originy1))
                            codegroup1.append(Path.MOVETO)
                            for i in range(h2 + h1 + h3 - 1):
                                x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup1.append((x1, y1))
                            pointgroup1 = pointgroup1[h1 + h3:len(pointgroup1)]
                            for i in range(h2 - 1):
                                codegroup1.append(Path.LINETO)

                            for i in range(h2):
                                x = 2 * math.pi - (math.pi / (180 / (i + 1 + p)))
                                x1 = r * math.cos(x)
                                y1 = r * math.sin(x)
                                pointgroup3.append((x1, y1))
                            for i in range(h2):
                                codegroup3.append(Path.LINETO)
                            x1 = (
                                 c1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][0] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][0]) / (
                                     2 * tb1 * (1 - tb1))
                            y1 = (
                                 d1 - numpy.square(1 - tb1) * pointgroup1[len(pointgroup1) - 1][1] - numpy.square(tb1) *
                                 pointgroup3[len(pointgroup3) - 1][1]) / (
                                     2 * tb1 * (1 - tb1))
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (x1, y1),
                                           pointgroup3[len(pointgroup3) - 1]]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup2 = [pointgroup1[len(pointgroup1) - 1], (0, 0), (0, 0),
                                           pointgroup3[len(pointgroup3) - 1]]
                            codegroup2 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                            x2 = (c2 - numpy.square(1 - tb2) * pointgroup3[0][0] - numpy.square(tb2) * pointgroup1[0][
                                0]) / (
                                     2 * tb2 * (1 - tb2))
                            y2 = (d2 - numpy.square(1 - tb2) * pointgroup3[0][1] - numpy.square(tb2) * pointgroup1[0][
                                1]) / (
                                     2 * tb2 * (1 - tb2))
                            pointgroup4 = [pointgroup3[0], (x2, y2), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE3, Path.CURVE3]
                            pointgroup4 = [pointgroup3[0], (0, 0), pointgroup1[0]]
                            pointgroup4 = [pointgroup3[0], (0, 0), (0, 0), pointgroup1[0]]
                            codegroup4 = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                            pointgroup.extend(pointgroup1)
                            pointgroup.extend(pointgroup2)
                            pointgroup.extend(pointgroup3)
                            pointgroup.extend(pointgroup4)
                            codegroup.extend(codegroup1)
                            codegroup.extend(codegroup2)
                            codegroup.extend(codegroup3)
                            codegroup.extend(codegroup4)
        return pointgroup, codegroup, h1, h2, h3

    # h1_p_23 = int(round((date_23[3][1] / date_23[3][0]), 2) * int(date_23[3][0] / 1000 * 30))
    # h3_p_23 = int(round((date_23[3][3] / date_23[3][0]), 2) * int(date_23[3][0] / 1000 * 30))
    # h2_p_23 = int(round((date_23[1][2] / date_23[1][0]), 2) * int(date_23[1][0] / 1000 * 30))
    # h2_p1_23 = int(round((date_23[3][2] / date_23[3][0]), 2) * int(date_23[3][0] / 1000 * 30))
    # h1_p1_23 = int(round((date_23[2][1] / date_23[2][0]), 2) * int(date_23[2][0] / 1000 * 30))
    # h3_p1_23 = int(round((date_23[1][3] / date_23[1][0]), 2) * int(date_23[1][0] / 1000 * 30))
    # h3_p2_23 = int(round((date_23[2][3] / date_23[2][0]), 2) * int(date_23[2][0] / 1000 * 30))
    #
    # h1_p_24 = int(round((date_24[3][1] / date_24[3][0]), 2) * int(date_24[3][0] / 1000 * 30))
    # h3_p_24 = int(round((date_24[3][3] / date_24[3][0]), 2) * int(date_24[3][0] / 1000 * 30))
    # h2_p_24 = int(round((date_24[1][2] / date_24[1][0]), 2) * int(date_24[1][0] / 1000 * 30))
    # h2_p1_24 = int(round((date_24[3][2] / date_24[3][0]), 2) * int(date_24[3][0] / 1000 * 30))
    # h1_p1_24 = int(round((date_24[2][1] / date_24[2][0]), 2) * int(date_24[2][0] / 1000 * 30))
    # h3_p1_24 = int(round((date_24[1][3] / date_24[1][0]), 2) * int(date_24[1][0] / 1000 * 30))
    # h3_p2_24 = int(round((date_24[2][3] / date_24[2][0]), 2) * int(date_24[2][0] / 1000 * 30))
    #
    # h1_p_55 = int(round((date_55[3][1] / date_55[3][0]), 2) * int(date_55[3][0] / 1000 * 30))
    # h3_p_55 = int(round((date_55[3][3] / date_55[3][0]), 2) * int(date_55[3][0] / 1000 * 30))
    # h2_p_55 = int(round((date_55[1][2] / date_55[1][0]), 2) * int(date_55[1][0] / 1000 * 30))
    # h2_p1_55 = int(round((date_55[3][2] / date_55[3][0]), 2) * int(date_55[3][0] / 1000 * 30))
    # h1_p1_55 = int(round((date_55[2][1] / date_55[2][0]), 2) * int(date_55[2][0] / 1000 * 30))
    # h3_p1_55 = int(round((date_55[1][3] / date_55[1][0]), 2) * int(date_55[1][0] / 1000 * 30))
    # h3_p2_55 = int(round((date_55[2][3] / date_55[2][0]), 2) * int(date_55[2][0] / 1000 * 30))
    #
    # h1_p_56 = int(round((date_56[3][1] / date_56[3][0]), 2) * int(date_56[3][0] / 1000 * 30))
    # h3_p_56 = int(round((date_56[3][3] / date_56[3][0]), 2) * int(date_56[3][0] / 1000 * 30))
    # h2_p_56 = int(round((date_56[1][2] / date_56[1][0]), 2) * int(date_56[1][0] / 1000 * 30))
    # h2_p1_56 = int(round((date_56[3][2] / date_56[3][0]), 2) * int(date_56[3][0] / 1000 * 30))
    # h1_p1_56 = int(round((date_56[2][1] / date_56[2][0]), 2) * int(date_56[2][0] / 1000 * 30))
    # h3_p1_56 = int(round((date_56[1][3] / date_56[1][0]), 2) * int(date_56[1][0] / 1000 * 30))
    # h3_p2_56 = int(round((date_56[2][3] / date_56[2][0]), 2) * int(date_56[2][0] / 1000 * 30))
    #
    # h1_p_57 = int(round((date_57[3][1] / date_57[3][0]), 2) * int(date_57[3][0] / 1000 * 30))
    # h3_p_57 = int(round((date_57[3][3] / date_57[3][0]), 2) * int(date_57[3][0] / 1000 * 30))
    # h2_p_57 = int(round((date_57[1][2] / date_57[1][0]), 2) * int(date_57[1][0] / 1000 * 30))
    # h2_p1_57 = int(round((date_57[3][2] / date_57[3][0]), 2) * int(date_57[3][0] / 1000 * 30))
    # h1_p1_57 = int(round((date_57[2][1] / date_57[2][0]), 2) * int(date_57[2][0] / 1000 * 30))
    # h3_p1_57 = int(round((date_57[1][3] / date_57[1][0]), 2) * int(date_57[1][0] / 1000 * 30))
    # h3_p2_57 = int(round((date_57[2][3] / date_57[2][0]), 2) * int(date_57[2][0] / 1000 * 30))
    #
    # h1_p_58 = int(round((date_58[3][1] / date_58[3][0]), 2) * int(date_58[3][0] / 1000 * 30))
    # h3_p_58 = int(round((date_58[3][3] / date_58[3][0]), 2) * int(date_58[3][0] / 1000 * 30))
    # h2_p_58 = int(round((date_58[1][2] / date_58[1][0]), 2) * int(date_58[1][0] / 1000 * 30))
    # h2_p1_58 = int(round((date_58[3][2] / date_58[3][0]), 2) * int(date_58[3][0] / 1000 * 30))
    # h1_p1_58 = int(round((date_58[2][1] / date_58[2][0]), 2) * int(date_58[2][0] / 1000 * 30))
    # h3_p1_58 = int(round((date_58[1][3] / date_58[1][0]), 2) * int(date_58[1][0] / 1000 * 30))
    # h3_p2_58 = int(round((date_58[2][3] / date_58[2][0]), 2) * int(date_58[2][0] / 1000 * 30))
    #
    # h1_p_75 = int(round((date_75[3][1] / date_75[3][0]), 2) * int(date_75[3][0] / 1000 * 30))
    # h3_p_75 = int(round((date_75[3][3] / date_75[3][0]), 2) * int(date_75[3][0] / 1000 * 30))
    # h2_p_75 = int(round((date_75[1][2] / date_75[1][0]), 2) * int(date_75[1][0] / 1000 * 30))
    # h2_p1_75 = int(round((date_75[3][2] / date_75[3][0]), 2) * int(date_75[3][0] / 1000 * 30))
    # h1_p1_75 = int(round((date_75[2][1] / date_75[2][0]), 2) * int(date_75[2][0] / 1000 * 30))
    # h3_p1_75 = int(round((date_75[1][3] / date_75[1][0]), 2) * int(date_75[1][0] / 1000 * 30))
    # h3_p2_75 = int(round((date_75[2][3] / date_75[2][0]), 2) * int(date_75[2][0] / 1000 * 30))
    #
    # h1_p_77 = int(round((date_77[3][1] / date_77[3][0]), 2) * int(date_77[3][0] / 1000 * 30))
    # h3_p_77= int(round((date_77[3][3] / date_77[3][0]), 2) * int(date_77[3][0] / 1000 * 30))
    # h2_p_77 = int(round((date_77[1][2] / date_77[1][0]), 2) * int(date_77[1][0] / 1000 * 30))
    # h2_p1_77 = int(round((date_77[3][2] / date_77[3][0]), 2) * int(date_77[3][0] / 1000 * 30))
    # h1_p1_77 = int(round((date_77[2][1] / date_77[2][0]), 2) * int(date_77[2][0] / 1000 * 30))
    # h3_p1_77 = int(round((date_77[1][3] / date_77[1][0]), 2) * int(date_77[1][0] / 1000 * 30))
    # h3_p2_77 = int(round((date_77[2][3] / date_77[2][0]), 2) * int(date_77[2][0] / 1000 * 30))
    #
    # h1_p_89 = int(round((date_89 [3][1] / date_77[3][0]), 2) * int(date_89 [3][0] / 1000 * 30))
    # h3_p_89  = int(round((date_89 [3][3] / date_77[3][0]), 2) * int(date_89 [3][0] / 1000 * 30))
    # h2_p_89  = int(round((date_89 [1][2] / date_77[1][0]), 2) * int(date_89 [1][0] / 1000 * 30))
    # h2_p1_89  = int(round((date_89 [3][2] / date_77[3][0]), 2) * int(date_89 [3][0] / 1000 * 30))
    # h1_p1_89  = int(round((date_89 [2][1] / date_77[2][0]), 2) * int(date_89 [2][0] / 1000 * 30))
    # h3_p1_89  = int(round((date_89 [1][3] / date_77[1][0]), 2) * int(date_89 [1][0] / 1000 * 30))
    # h3_p2_89  = int(round((date_89 [2][3] / date_77[2][0]), 2) * int(date_89 [2][0] / 1000 * 30))
    #
    # r = 1
    # test1_23, test2_23, h1_1_23, h2_1_23, h3_1_23 = pointcalculate_clockwisetest(0.15, 0.15, 0.15 + round(date_23[0][1] / size, 2) * 0.05,
    #                                                           0.15 + round(date_23[0][1] // size, 2) * 0.05, r, 0, 2, 4,
    #                                                           date_23[0], 1, 0.5, 0.5)
    # test3_23, test4_23, h1_2_23, h2_2_23, h3_2_23 = pointcalculate_clockwisetest(-0.03 - round(date_23[0][2] // size, 2) * 0.05, 0, -0.03, 0,
    #                                                               r, h2_p_23, 2, 3, date_23[0], 1, 0.5, 0.5)
    # test5_23, test6_23, h1_3_23, h2_3_23, h3_3_23 = pointcalculate_clockwisetest(-0.2 - round(date_23[0][3] // size, 2) * 0.05,
    #                                                               0.2 + round(date_23[0][3] // size, 2) * 0.05, -0.2, 0.2, r,
    #                                                               h3_p1_23 + h3_p2_23, 2, 2, date_23[0], 1, 0.5, 0.5)
    #
    # test7_23, test8_23, h1_4_23, h2_4_23, h3_4_23 = pointcalculate_clockwisetest(0.15 - round(date_23[1][2] // size, 2) * 0.05,
    #                                                               -0.15 + round(date_23[1][2] // size, 2) * 0.05, 0.15, -0.15,
    #                                                               r, 0, 1, 3, date_23[1], 1, 0.5, 0.5)
    # test9_23, test10_23, h1_5_23, h2_5_23, h3_5_23 = pointcalculate_clockwisetest(0, 0.03 + round(date_23[1][3] // size, 2) * 0.05, 0, 0.03,
    #                                                                r, h3_p2_23, 1, 2, date_23[1], 1, 0.5, 0.5)
    # test11_23, test12_23, h1_6_23, h2_6_23, h3_6_23 = pointcalculate_clockwisetest(0.2 + round(date_23[1][1] // size, 2) * 0.05,
    #                                                                 0.2 + round(date_23[1][1] // size, 2) * 0.05, 0.2, 0.2, r,
    #                                                                 h1_p_23 + h1_p1_23, 1, 1, date_23[1], 1, 0.5, 0.5)
    #
    # test13, test14, h1_7, h2_7, h3_7 = pointcalculate_clockwisetest(-0.15, -0.15,
    #                                                                 -0.15 - round(date_23[2][3] // size, 2) * 0.05,
    #                                                                 -0.15 - round(date_23[2][3] // size, 2) * 0.05, r, 0, 4, 2,
    #                                                                 date_23[2], 1, 0.5, 0.5)
    # test15, test16, h1_8, h2_8, h3_8 = pointcalculate_clockwisetest(0.03 + round(date_23[2][1] // size, 2) * 0.05, 0, 0.03, 0,
    #                                                                 r, h1_p_23, 4, 1, date_23[2], 1, 0.5, 0.5)
    # test17, test18, h1_9, h2_9, h3_9 = pointcalculate_clockwisetest(0.2 + round(date_23[2][2] // size, 2) * 0.05,
    #                                                                 -0.2 - round(date_23[2][2] // size, 2) * 0.05, 0.2, -0.2,
    #                                                                 r, h1_1_23 + h2_p1_23, 4, 4, date_23[2], 1, 0.5, 0.5)
    #
    # test19, test20, h1_10, h2_10, h3_10 = pointcalculate_clockwisetest(-0.15, 0.15,
    #                                                                    -0.15 - round(date_23[3][1] // size, 2) * 0.05,
    #                                                                    0.15 + round(date_23[3][1] // size, 2) * 0.05, r, 0, 3,
    #                                                                    1, date_23[3], 1, 0.5, 0.5)
    # test21, test22, h1_11, h2_11, h3_11 = pointcalculate_clockwisetest(0, -0.03 - round(date_23[3][2] // size, 2) * 0.05, 0,
    #                                                                    -0.03, r, h1_1_23, 3, 4, date_23[3], 1, 0.5, 0.5)
    # # test23,test24,h1_12,h2_12,h3_12=pointcalculate_clockwisetest(-0.4,-0.4,-0.3,-0.3,r,h2_2+h2_4,3,3,date[3],1,0.5,0.5)
    # test23, test24, h1_12, h2_12, h3_12 = pointcalculate_clockwisetest(-0.2 - round(date_23[3][3] // size, 2) * 0.05,
    #                                                                    -0.2 - round(date_23[3][3] // size, 2) * 0.05, -0.2,
    #                                                                    -0.2, r, h2_4_23 + h2_1_23, 3, 3, date[3]_23, 1, 0.5, 0.5)

    def pathmaker(a, b, c, d,ax):  # a:点组，b：路劲组，c：颜色参数
        if len(a) != 0:
            path = Path(a, b)
            patch = patches.PathPatch(path, facecolor=c, alpha=0.8, edgecolor=d)
            ax.add_patch(patch)

    def outcyclemakerblack(a, t, r1, r2):  # a：总的弧长，t：相位 r:半径,point:点阵
        pointgroup = []
        codegroup = []
        pointgroup1 = []
        codegroup1 = []
        pointgroup2 = []
        codegroup2 = []
        if a != 0:

            if t == 1:
                originx = (math.pi / (180 / (1)))
                originx1 = r1 * math.cos(originx)
                originy1 = r1 * math.sin(originx)
                pointgroup1.append((originx1, originy1))
                codegroup1.append(Path.MOVETO)
                for i in range(a - 1):
                    x = (math.pi / (180 / (i + 2)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)
                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
            elif t == 2:
                originx = 0.5 * math.pi + (math.pi / (180 / (1)))
                originx1 = r1 * math.cos(originx)
                originy1 = r1 * math.sin(originx)
                pointgroup1.append((originx1, originy1))
                codegroup1.append(Path.MOVETO)
                for i in range(a - 1):
                    x = 0.5 * math.pi + (math.pi / (180 / (i + 2)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = 0.5 * math.pi + (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
            elif t == 3:
                originx = 1 * math.pi + (math.pi / (180 / (1)))
                originx1 = r1 * math.cos(originx)
                originy1 = r1 * math.sin(originx)
                pointgroup1.append((originx1, originy1))
                codegroup1.append(Path.MOVETO)
                for i in range(a - 1):
                    x = 1 * math.pi + (math.pi / (180 / (i + 2)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = 1 * math.pi + (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
            elif t == 4:
                originx = 1.5 * math.pi + (math.pi / (180 / (1)))
                originx1 = r1 * math.cos(originx)
                originy1 = r1 * math.sin(originx)
                pointgroup1.append((originx1, originy1))
                codegroup1.append(Path.MOVETO)
                for i in range(a - 1):
                    x = 1.5 * math.pi + (math.pi / (180 / (i + 2)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = 1.5 * math.pi + (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
        return pointgroup, codegroup

        # a：总的弧长，t：相位 r:半径,point:点阵

    def outcyclemakergray(a, t, r1, r2):
        pointgroup = []
        codegroup = []
        pointgroup1 = []
        codegroup1 = []
        pointgroup2 = []
        codegroup2 = []
        if a != 0:

            if t == 1:

                codegroup1.append(Path.MOVETO)
                for i in range(a):
                    x = 0.5 * math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = 0.5 * math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
            elif t == 2:
                codegroup1.append(Path.MOVETO)
                for i in range(a):
                    x = math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
            elif t == 3:
                codegroup1.append(Path.MOVETO)
                for i in range(a):
                    x = 1.5 * math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = 1.5 * math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
            elif t == 4:
                codegroup1.append(Path.MOVETO)
                for i in range(a):
                    x = 2 * math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r1 * math.cos(x)
                    y1 = r1 * math.sin(x)
                    pointgroup1.append((x1, y1))
                for i in range(a - 1):
                    codegroup1.append(Path.LINETO)

                for i in range(a):
                    x = 2 * math.pi - (math.pi / (180 / (i + 1)))
                    x1 = r2 * math.cos(x)
                    y1 = r2 * math.sin(x)
                    pointgroup2.append((x1, y1))
                for i in range(a):
                    codegroup2.append(Path.LINETO)

                pointgroup2.reverse()
                pointgroup.extend(pointgroup1)
                # pointgroup.append(pointgroup2[len(pointgroup2)-1])
                pointgroup.append(pointgroup2[0])
                pointgroup.extend(pointgroup2)
                # pointgroup.append(pointgroup2[0])
                pointgroup.append(pointgroup1[0])
                codegroup.extend(codegroup1)
                codegroup.append(Path.LINETO)
                codegroup.extend(codegroup2)
                # codegroup.append(Path.LINETO)
                codegroup.append(Path.LINETO)
        return pointgroup, codegroup

    def roadnamemaker(a):
        if a == 23:
            s = '23.东环大道枫南路路口'
        elif a == 24:
            s = '24.机场路枫南路路口'
        elif a == 55:
            s = '55.市府大道白云山中路路口'
        elif a == 56:
            s = '56.市府大道东环大道路口'
        elif a == 57:
            s = '57.市府大道经中路路口'
        elif a == 58:
            s = '58.市府大道机场路路口'
        elif a == 75:
            s = '75.东环大道开元路路口'
        elif a == 77:
            s = '77.东环大道康平路路口'
        elif a == 89:
            s = '89.机场路开元路'
        return s
    def automakershow(a):
        fig = plt.figure()
        # canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        daycarlist=newdayperiodreadlist(a)
        print(" 读取路口当前时间段数据库完成 %s" % ctime())
        idtsclane = getidtsclane(tsclane, a)
        print(" 读取选择路口渠化信息完成 %s" % ctime())
        lend0, lend2, lend4, lend6 = sidnumcalculate(idtsclane)
        flowgroup = [flowgroup0, flowgroup2, flowgroup4, flowgroup6] = inflowcalculate(daycarlist, idtsclane,
                                                                                          lend0, lend2, lend4,
                                                                                     lend6)
        flowsize = max(flowgroup[0][0],flowgroup[1][0],flowgroup[2][0],flowgroup[3][0])
        date = flowgroup
        k = 30
        k1 = 30
        r = 1
        size = 400
        h1_p = int(round((date[3][1] / date[3][0]), 2) * int(date[3][0] / flowsize * 40))
        h3_p = int(round((date[3][3] / date[3][0]), 2) * int(date[3][0] / flowsize * 40))
        h2_p = int(round((date[1][2] / date[1][0]), 2) * int(date[1][0] / flowsize * 40))
        h2_p1 = int(round((date[3][2] / date[3][0]), 2) * int(date[3][0] / flowsize * 40))
        h1_p1 = int(round((date[2][1] / date[2][0]), 2) * int(date[2][0] / flowsize * 40))
        h3_p1 = int(round((date[1][3] / date[1][0]), 2) * int(date[1][0] / flowsize * 40))
        h3_p2 = int(round((date[2][3] / date[2][0]), 2) * int(date[2][0] / flowsize * 40))

        test1, test2, h1_1, h2_1, h3_1 = pointcalculate_clockwisetest(0.15, 0.15,
                                                                      0.15 + round(date[0][1] / size, 2) * 0.05,
                                                                      0.15 + round(date[0][1] // size, 2) * 0.05, r, 0,
                                                                      2, 4, date[0], 1, 0.5, 0.5,flowsize)
        test3, test4, h1_2, h2_2, h3_2 = pointcalculate_clockwisetest(-0.03 - round(date[0][2] // size, 2) * 0.05, 0,
                                                                      -0.03, 0, r, h2_p, 2, 3, date[0], 1, 0.5, 0.5,flowsize)
        test5, test6, h1_3, h2_3, h3_3 = pointcalculate_clockwisetest(-0.2 - round(date[0][3] // size, 2) * 0.05,
                                                                      0.2 + round(date[0][3] // size, 2) * 0.05, -0.2,
                                                                      0.2, r, h3_p1 + h3_p2, 2, 2, date[0], 1, 0.5, 0.5,flowsize)

        test7, test8, h1_4, h2_4, h3_4 = pointcalculate_clockwisetest(0.15 - round(date[1][2] // size, 2) * 0.05,
                                                                      -0.15 + round(date[1][2] // size, 2) * 0.05, 0.15,
                                                                      -0.15, r, 0, 1, 3, date[1], 1, 0.5, 0.5,flowsize)
        test9, test10, h1_5, h2_5, h3_5 = pointcalculate_clockwisetest(0, 0.03 + round(date[1][3] // size, 2) * 0.05, 0,
                                                                       0.03, r, h3_p2, 1, 2, date[1], 1, 0.5, 0.5,flowsize)
        test11, test12, h1_6, h2_6, h3_6 = pointcalculate_clockwisetest(0.2 + round(date[1][1] // size, 2) * 0.05,
                                                                        0.2 + round(date[1][1] // size, 2) * 0.05, 0.2,
                                                                        0.2, r, h1_p + h1_p1, 1, 1, date[1], 1, 0.5,
                                                                        0.5,flowsize)

        test13, test14, h1_7, h2_7, h3_7 = pointcalculate_clockwisetest(-0.15, -0.15,
                                                                        -0.15 - round(date[2][3] // size, 2) * 0.05,
                                                                        -0.15 - round(date[2][3] // size, 2) * 0.05, r,
                                                                        0, 4, 2, date[2], 1, 0.5, 0.5,flowsize)
        test15, test16, h1_8, h2_8, h3_8 = pointcalculate_clockwisetest(0.03 + round(date[2][1] // size, 2) * 0.05, 0,
                                                                        0.03, 0, r, h1_p, 4, 1, date[2], 1, 0.5, 0.5,flowsize)
        test17, test18, h1_9, h2_9, h3_9 = pointcalculate_clockwisetest(0.2 + round(date[2][2] // size, 2) * 0.05,
                                                                        -0.2 - round(date[2][2] // size, 2) * 0.05, 0.2,
                                                                        -0.2, r, h1_1 + h2_p1, 4, 4, date[2], 1, 0.5,
                                                                        0.5,flowsize)

        test19, test20, h1_10, h2_10, h3_10 = pointcalculate_clockwisetest(-0.15, 0.15,
                                                                           -0.15 - round(date[3][1] // size, 2) * 0.05,
                                                                           0.15 + round(date[3][1] // size, 2) * 0.05,
                                                                           r, 0, 3, 1, date[3], 1, 0.5, 0.5,flowsize)
        test21, test22, h1_11, h2_11, h3_11 = pointcalculate_clockwisetest(0,
                                                                           -0.03 - round(date[3][2] // size, 2) * 0.05,
                                                                           0, -0.03, r, h1_1, 3, 4, date[3], 1, 0.5,
                                                                           0.5,flowsize)
        # test23,test24,h1_12,h2_12,h3_12=pointcalculate_clockwisetest(-0.4,-0.4,-0.3,-0.3,r,h2_2+h2_4,3,3,date[3],1,0.5,0.5)
        test23, test24, h1_12, h2_12, h3_12 = pointcalculate_clockwisetest(-0.2 - round(date[3][3] // size, 2) * 0.05,
                                                                           -0.2 - round(date[3][3] // size, 2) * 0.05,
                                                                           -0.2, -0.2, r, h2_4 + h2_1, 3, 3, date[3], 1,
                                                                           0.5, 0.5,flowsize)

        testout1, testout2 = outcyclemakerblack(h1_4 + h2_4 + h3_4, 1, 1.1, 1)
        testout3, testout4 = outcyclemakerblack(h1_1 + h2_1 + h3_1, 2, 1.1, 1)
        testout5, testout6 = outcyclemakerblack(h1_10 + h2_10 + h3_10, 3, 1.1, 1)
        testout7, testout8 = outcyclemakerblack(h1_7 + h2_7 + h3_7, 4, 1.1, 1)

        testout9, testout10 = outcyclemakergray(h1_4 + h1_7 + h1_10, 1, 1.1, 1)
        testout11, testout12 = outcyclemakergray(h1_1 + h2_7 + h2_10, 4, 1.1, 1)
        testout13, testout14 = outcyclemakergray(h2_1 + h2_4 + h3_10, 3, 1.1, 1)
        testout15, testout16 = outcyclemakergray(h3_1 + h3_4 + h3_7, 2, 1.1, 1)

        pathmaker(testout1, testout2, 'black', 'black',ax)
        pathmaker(testout3, testout4, 'black', 'black',ax)
        pathmaker(testout5, testout6, 'black', 'black',ax)
        pathmaker(testout7, testout8, 'black', 'black',ax)

        pathmaker(testout9, testout10, 'gray', 'gray',ax)
        pathmaker(testout11, testout12, 'gray', 'gray',ax)
        pathmaker(testout13, testout14, 'gray', 'gray',ax)
        pathmaker(testout15, testout16, 'gray', 'gray',ax)
        pathmaker(test1, test2, 'seagreen', 'seagreen',ax)
        pathmaker(test3, test4, 'seagreen', 'seagreen',ax)
        pathmaker(test5, test6, 'seagreen', 'seagreen',ax)

        pathmaker(test7, test8, 'orange', 'orange',ax)
        pathmaker(test9, test10, 'orange', 'orange',ax)
        pathmaker(test11, test12, 'orange', 'orange',ax)

        pathmaker(test13, test14, 'salmon', 'salmon',ax)
        pathmaker(test15, test16, 'salmon', 'salmon',ax)
        pathmaker(test17, test18, 'salmon', 'salmon',ax)

        pathmaker(test19, test20, 'skyblue', 'skyblue',ax)
        pathmaker(test21, test22, 'skyblue', 'skyblue',ax)
        pathmaker(test23, test24, 'skyblue', 'skyblue',ax)

        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_xticks([])
        ax.set_yticks([])
        s = roadnamemaker(a)
        plt.text(0, 0, s, horizontalalignment='center', va='center',fontsize='18')
        ax.set_aspect('equal')
        ax.set_frame_on(False)
        # plt.imshow()
        # canvas.print_figure('demo.png',bbox_inches='tight',transparent=True)
        plt.savefig("D:\pythonwork\jiaotongweb\chart\static/"+str(a)+'.png', bbox_inches='tight', transparent=True, dpi=58)
        plt.close()
       # s="F:\pythonwork\jiaotongweb"+"\"+
        #shutil.copy("F:\pythonwork\jiaotongweb\examples.jpg", "F:\pythonwork\jiaotongweb\chart\static")
        # canvas.print_figure('demo.jpg')

    automakershow(23)
    automakershow(24)
    automakershow(55)
    automakershow(56)
    automakershow(57)
    automakershow(58)
    automakershow(75)
    automakershow(77)
    automakershow(89)

    return render(resquest, 'mapshow.html', context)





def Get_Date(resquest):
    context={}
    ran=random.randint(0,50)

    global glo_direction
    if resquest.method=="POST":

        picture_form=ChartForm(data=resquest.POST,auto_id="%s")
        context['picture_form']=picture_form
        print(picture_form.is_valid())
        if  picture_form.is_valid():



            year=picture_form.cleaned_data['year']
            month=picture_form.cleaned_data['month']
            day=picture_form.cleaned_data['day']
            direction=picture_form.cleaned_data['direction']
            Xaxisa = picture_form.cleaned_data['Xaxisa']
            Xaxisb = picture_form.cleaned_data['Xaxisb']
            Yaxis = picture_form.cleaned_data['Yaxis']
            Alane =picture_form.cleaned_data['Alane']
            Blane = picture_form.cleaned_data['Blane']
            Clane = picture_form.cleaned_data['Clane']
            Dlane= picture_form.cleaned_data['Dlane']
           # print(year,month,day,direction,Xaxisa,Xaxisb,Yaxis,Alane,Blane,Clane,Dlane)
            glo_direction=direction
            t=chartdate.objects.get(id=1)
            t.year=year
            t.month=month
            t.day=day
            t.direction=direction
            t.Xaxisa=Xaxisa
            t.Xaxisb=Xaxisb
            t.Yaxis=Yaxis
            t.Alane=Alane
            t.Blane=Blane
            t.Clane=Clane
            t.Dlane=Dlane

            t.save()

            def gettsclanelist():  # 读取渠化信息
                p = []
                results = Tsclane.objects.all()
                for row in results:
                    if row.sid != 0:
                        sid = row.sid
                        movement = row.movement
                        dircetion = row.direction
                        intersectionld = row.intersectionid
                        p.append([sid, movement, dircetion, intersectionld])
                return p

            tsclane = gettsclanelist()
            print("初始化完成 %s" % ctime())



            def newperiodreadlist(a):  # 读取路口数据存入列表
                flag = 0
                car = []
                results = []

                if a == 23:
                    results = I023.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 24:
                    results = I024.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 55:
                    results = I055.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 56:
                    results = I056.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 57:
                    results = I057.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 58:
                    results = I058.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 75:
                    results = I075.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 77:
                    results = I077.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                elif a == 89:
                    results = I089.objects.filter(passtime__year=t.year, passtime__month=t.month, passtime__day=t.day)
                else:
                    results = []

                # print(results[0][0])
                if results:
                    for rowa in results:
                        id = rowa.id
                        inteid = rowa.inteid
                        direction = rowa.direction
                        lane = rowa.lane
                        carplate = rowa.carplate
                        passtime = rowa.passtime
                        traveltime = rowa.traveltime
                        upinteid = rowa.upinteid
                        updirection = rowa.updirection
                        uplane = rowa.uplane
                        car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection,
                                    uplane])
                    return car
                else:
                    results = [-999]
                    return results

            daycarlist = []
            daycarlist = newperiodreadlist(t.direction)
            print(t.direction)
            # print(daycarlist)
            print(" 读取路口当前日期数据库完成 %s" % ctime())

            # print(daycarlist[10])
            #  选择时间结束，得到指定日期list：daycarlist
            #  将该时间点按方向和转向分类

            def getidtsclane(a):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
                c = []
                for row in a:
                    if row[3] == t.direction:
                        c.append(row)
                return c

            idtsclane = []
            idtsclane = getidtsclane(tsclane)
            print(" 读取选择路口渠化信息完成 %s" % ctime())

            # print(idtsclane)

            def getlanesid(a, b):  # 得到对应sid的direction和lane   a:渠化列表 b 路口sid
                k = [0, 0]
                d0 = []
                d2 = []
                d4 = []
                d6 = []
                for row in a:  # 得到各个direcition lane的个数
                    if row[2] == 0:
                        d0.append(row)
                    elif row[2] == 2:
                        d2.append(row)
                    elif row[2] == 4:
                        d4.append(row)
                    elif row[2] == 6:
                        d6.append(row)
                for row in a:
                    if row[0] == b:  # sid相等采匹配k[0]和k[1]
                        k[0] = row[2]  # direction
                        if k[0] == 6:
                            k[1] = row[0]  # lane
                        elif k[0] == 4:
                            k[1] = row[0] - len(d6)
                        elif k[0] == 2:
                            k[1] = row[0] - len(d6) - len(d4)
                        elif k[0] == 0:
                            k[1] = row[0] - len(d6) - len(d4) - len(d2)
                return k

            # 输出sid对应的direction和lane
            def laneclass(a, b, c):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
                p = []
                p = getlanesid(b, c)
                c = p[0]  # direction
                d = p[1]  # lane
                t = []
                for row in a:
                    if row[2] == c and row[3] == d:
                        t.append(row)
                return t

            # print(len(idtsclane))
            def automakesidlist(a, b):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
                sidlen = len(b)
                f = []
                for i in range(sidlen):
                    v = []
                    v = laneclass(a, b, i + 1)
                    f.append(v)
                return f

            sidlanelist = []
            sidlanelist = automakesidlist(daycarlist, idtsclane)  # sidlanelist是一个列表，长度是路口总id长度，里面包含了对应sid的列表

            #  print(sidlanelist)
            # sidlanelist有sid个数的列表，里面是按日期和sid分开的子列表

            # 一个数据一个点
            def pointmaker(a, b):  # a为一个数据,b为周期
                x = [0, 0]
                x[0] = a[5].hour + a[5].minute / 60 + a[5].second / 3600  # 横坐标
                x[1] = (a[5].hour * 3600 + a[5].minute * 60 + a[5].second) % b
                return x

            # 一个列表数据一个列表点
            def pointlistmaker(a, b, c, d):  # a为指定列表 b为周期 c时间起点 d 时间终点
                t = [[], []]
                for row in a:
                    if row[5].hour >= c and row[5].hour <= d:
                        x = row[5].hour + row[5].minute / 60 + row[5].second / 3600  # 横坐标
                        y = (row[5].hour * 3600 + row[5].minute * 60 + row[5].second) % b
                        t[0].append(x)
                        t[1].append(y)
                return t

            def autopointlistmaker(a, b, c, d):  # a sidlanelist b 周期 c时间起点 d时间终点
                t = []
                for row in a:  # 每一个row都是一个列表
                    u = []
                    u = pointlistmaker(row, b, c, d)
                    t.append(u)
                return t

            pointlist = []
            pointlist = autopointlistmaker(sidlanelist, t.Yaxis, t.Xaxisa, t.Xaxisb)
            print(" 点阵完成 %s" % ctime())

            # 点阵生成完毕 按sid编号

            fig=plt.figure(figsize=(12,6))
            ax=fig.add_axes([0.03,0.05,0.95,0.94])
            def picturemaker(a, e, f):  # a sid编号 b周期 c d时间区间 e为点阵 f：点的颜色
                if a != -999:  # plt.plot(pointlist[0][i][0],pointlist[0][i][1],color='red',marker='.')
                    ax.scatter(e[a - 1][0], e[a - 1][1], s=0.2 * 10, c=f);
                    # plt.xlabel('周期')
                    # plt.ylabel('时间')
                    # plt.xlim(0,24)

            def autopicturemaker(a, b, c, d, e, f, g, h):  # avcd 4路编号 e周期 f,g时间区间，h点阵
               # plt.figure(figsize=(12, 6))

                picturemaker(a, h, "red")
                picturemaker(b, h, "b")
                picturemaker(c, h, "g")
                picturemaker(d, h, 'y')
                ax.set_ylim(0,e)
                ax.set_xlim(f,g)
                ax.set_xticks(np.linspace(f, g, g - f + 1, endpoint=True))
                ax.set_yticks(np.linspace(0, e, (e - 0)/10 + 1, endpoint=True))
                # plt.ylim(0, e)
                # plt.xlim(0, 24)
                # plt.xticks(np.linspace(f, g, g - f + 1, endpoint=True))
                # plt.yticks(np.linspace(0, e, (e - 0)/10 + 1, endpoint=True))

                path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
                picturename = "D:\pythonwork\jiaotongweb\chart\static\images\_flowchart\examples" + str(ran) + ".jpg"
                #plt.savefig(picturename, dpi=200)
                print(str(ran))
                name='examples'+str(ran)
                plt.savefig(path+"\static\images\_flowchart/"+name+".jpg",dpi=200)
                plt.close()



                #shutil.copy("F:\pythonwork\jiaotongweb\examples.jpg", "F:\pythonwork\jiaotongweb\chart\static")
                print(" 图片生成完成 %s" % ctime())
                # plt.show()

            autopicturemaker(t.Alane, t.Blane, t.Clane, t.Dlane, t.Yaxis, t.Xaxisa, t.Xaxisb, pointlist)  # 红 蓝 绿 黄







       # return render(resquest,'flowchart.html',{context})
    else:

        picture_form=ChartForm();
        context['picture_form'] = picture_form;

    n=chartdate.objects.get(id=1)
    date=str(n.year)+'.'+str(n.month)+'.'+str(n.day)
    id=n.direction
    origin=n.Xaxisa
    end=n.Xaxisb
    perior=n.Yaxis
    sid=str(n.Alane)+'.'+str(n.Blane)+'.'+str(n.Clane)+'.'+str(n.Dlane)
    context['date']=date
    context['id']=id
    context['origin']=origin
    context['end']=end
    context['perior']=perior
    context['sid']=sid
    context['t'] = '/' + 'flowchart9527' + '/' + str(random.randint(1, 999))
    context['netname123'] ="/static/images/_flowchart/examples"+str(ran)+".jpg"

    return render(resquest, 'flowchart.html',context )

def Show_picture(resquest):
    context={}
    picture_form=ChartForm();
    context['picture_form']=picture_form;
    t=chartdate.objects.get(id=1)
    date=str(t.year)+'.'+str(t.month)+'.'+str(t.day)
    id=t.direction
    origin=t.Xaxisa
    end=t.Xaxisb
    perior=t.Yaxis
    sid=str(t.Alane)+'.'+str(t.Blane)+'.'+str(t.Clane)+'.'+str(t.Dlane)
    context['date']=date
    context['id']=id
    context['origin']=origin
    context['end']=end
    context['perior']=perior
    context['sid']=sid
    PictureData=[t.year, t.month, t.day, t.direction, t.Xaxisa, t.Xaxisb, t.Yaxis, t.Alane, t.Blane, t.Clane, t.Dlane]
    print(PictureData)

    tsclane = []

    def gettsclanelist(): #读取渠化信息
        p=[]
        results = Tsclane.objects.all()
        for row in results:
            if row.sid!= 0:
                sid = row.sid
                movement = row.movement
                dircetion = row.direction
                intersectionld = row.intersectionid
                p.append([sid, movement, dircetion, intersectionld])
        return p

    tsclane = gettsclanelist()
    print("初始化完成 %s" % ctime())


    # def periodreadlist(a):  # 读取路口数据存入列表
    #     flag = 0
    #     car = []
    #
    #     if a == 23:
    #         results = I023.objects.all()
    #     elif a == 24:
    #         results = I024.objects.all()
    #     elif a == 55:
    #         results = I055.objects.all()
    #     elif a == 56:
    #         results = I056.objects.all()
    #     elif a == 57:
    #         results = I057.objects.all()
    #     elif a == 58:
    #         results = I058.objects.all()
    #     elif a == 75:
    #         results = I075.objects.all()
    #     elif a == 77:
    #         results = I077.objects.all()
    #     elif a == 89:
    #         results = I089.objects.all()
    #     else:
    #
    #         return car
    #
    #     for rowa in results:
    #         id = rowa.id
    #         inteid = rowa.inteid
    #         direction = rowa.direction
    #         lane = rowa.lane
    #         carplate = rowa.carplate
    #         passtime = rowa.passtime
    #         traveltime = rowa.traveltime
    #         upinteid = rowa.upinteid
    #         updirection = rowa.updirection
    #         uplane = rowa.uplane
    #         car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection, uplane])
    #     return car
    #
    # carlist = periodreadlist(t.direction)
    # # print(carlist[10])
    # print("读取路口数据完成 %s" % ctime())
    #
    # # 选择路口并读取数据库结束
    #
    # # 选择时间
    # def dayperiodreadlist(d):  # f为当前路口总列表，此函数为提取指定日期列表并返回,abc年月日,d为diection
    #     day = []
    #     for row in d:
    #         if row[5].year == t.year and row[5].month == t.month and row[5].day == t.day:
    #             day.append(row)
    #     return day
    #
    # daycarlist = []
    # daycarlist = dayperiodreadlist(carlist)
    # print(" 读取路口当前日期数据库完成 %s" % ctime())

    def newperiodreadlist(a):  # 读取路口数据存入列表
        flag=0
        car = []
        results=[]

        if a == 23:
             results = I023.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 24:
             results = I024.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 55:
             results = I055.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 56:
             results = I056.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 57:
             results = I057.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 58:
             results = I058.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 75:
             results = I075.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 77:
             results = I077.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        elif a == 89:
             results = I089.objects.filter(passtime__year=t.year,passtime__month=t.month,passtime__day=t.day)
        else:
             results=[]

        #print(results[0][0])
        if results:
            for rowa in results:
                id = rowa.id
                inteid = rowa.inteid
                direction = rowa.direction
                lane = rowa.lane
                carplate = rowa.carplate
                passtime = rowa.passtime
                traveltime = rowa.traveltime
                upinteid = rowa.upinteid
                updirection = rowa.updirection
                uplane = rowa.uplane
                car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection, uplane])
            return car
        else:
            results=[-999]
            return results



    daycarlist = []
    daycarlist = newperiodreadlist(t.direction)
    print(t.direction)
   # print(daycarlist)
    print(" 读取路口当前日期数据库完成 %s" % ctime())
   # print(daycarlist[10])
   #  选择时间结束，得到指定日期list：daycarlist
   #  将该时间点按方向和转向分类

    def getidtsclane(a):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
        c = []
        for row in a:
            if row[3] ==t.direction:
                c.append(row)
        return c

    idtsclane = []
    idtsclane = getidtsclane(tsclane)
    print(" 读取选择路口渠化信息完成 %s" % ctime())
    #print(idtsclane)

    def getlanesid(a, b):  # 得到对应sid的direction和lane   a:渠化列表 b 路口sid
        k = [0, 0]
        d0 = []
        d2 = []
        d4 = []
        d6 = []
        for row in a:  # 得到各个direcition lane的个数
            if row[2] == 0:
                d0.append(row)
            elif row[2] == 2:
                d2.append(row)
            elif row[2] == 4:
                d4.append(row)
            elif row[2] == 6:
                d6.append(row)
        for row in a:
            if row[0] == b:  # sid相等采匹配k[0]和k[1]
                k[0] = row[2]  # direction
                if k[0] == 6:
                    k[1] = row[0]  # lane
                elif k[0] == 4:
                    k[1] = row[0] - len(d6)
                elif k[0] == 2:
                    k[1] = row[0] - len(d6) - len(d4)
                elif k[0] == 0:
                    k[1] = row[0] - len(d6) - len(d4) - len(d2)
        return k

    # 输出sid对应的direction和lane
    def laneclass(a, b, c):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
        p = []
        p = getlanesid(b, c)
        c = p[0]  # direction
        d = p[1]  # lane
        t = []
        for row in a:
            if row[2] == c and row[3] == d:
                t.append(row)
        return t

    # print(len(idtsclane))
    def automakesidlist(a, b):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
        sidlen = len(b)
        f = []
        for i in range(sidlen):
            v = []
            v = laneclass(a, b, i + 1)
            f.append(v)
        return f

    sidlanelist = []
    sidlanelist = automakesidlist(daycarlist, idtsclane)  # sidlanelist是一个列表，长度是路口总id长度，里面包含了对应sid的列表
  #  print(sidlanelist)
    # sidlanelist有sid个数的列表，里面是按日期和sid分开的子列表

    # 一个数据一个点
    def pointmaker(a, b):  # a为一个数据,b为周期
        x = [0, 0]
        x[0] = a[5].hour + a[5].minute / 60 + a[5].second / 3600  # 横坐标
        x[1] = (a[5].hour * 3600 + a[5].minute * 60 + a[5].second) % b
        return x

    # 一个列表数据一个列表点
    def pointlistmaker(a, b,c,d):  # a为指定列表 b为周期 c时间起点 d 时间终点
        t = [[], []]
        for row in a:
            if row[5].hour>=c and row[5].hour<=d:
                x = row[5].hour + row[5].minute / 60 + row[5].second / 3600  # 横坐标
                y = (row[5].hour * 3600 + row[5].minute * 60 + row[5].second) % b
                t[0].append(x)
                t[1].append(y)
        return t

    def autopointlistmaker(a, b,c,d):  # a sidlanelist b 周期 c时间起点 d时间终点
        t = []
        for row in a:  # 每一个row都是一个列表
            u = []
            u = pointlistmaker(row, b,c,d)
            t.append(u)
        return t

    pointlist = []
    pointlist = autopointlistmaker(sidlanelist, t.Yaxis, t.Xaxisa,t. Xaxisb)
    print(" 点阵完成 %s" % ctime())

    # 点阵生成完毕 按sid编号



    def picturemaker(a, e, f):  # a sid编号 b周期 c d时间区间 e为点阵 f：点的颜色
        if a != -999:  # plt.plot(pointlist[0][i][0],pointlist[0][i][1],color='red',marker='.')
            plt.scatter(e[a - 1][0], e[a - 1][1], s=0.2 * 10, c=f);
            # plt.xlabel('周期')
            # plt.ylabel('时间')
            # plt.xlim(0,24)

    def autopicturemaker(a, b, c, d, e, f, g, h):  # avcd 4路编号 e周期 f,g时间区间，h点阵
        plt.figure(figsize=(12, 6))
        picturemaker(a, h, "red")
        picturemaker(b, h, "b")
        picturemaker(c, h, "g")
        picturemaker(d, h, 'y')
        plt.ylim(0, e)
        plt.xticks(np.linspace(f, g, g - f + 1, endpoint=True))
        plt.savefig("examples.jpg", dpi=300)
        shutil.copy("D:\pythonwork\jiaotongweb\examples.jpg", "D:\pythonwork\jiaotongweb\chart\static")
        print(" 图片生成完成 %s" % ctime())
       # plt.show()

    autopicturemaker(t.Alane, t.Blane, t.Clane, t.Dlane, t.Yaxis, t.Xaxisa, t.Xaxisb, pointlist)  # 红 蓝 绿 黄

    return render(resquest,'show.html',context)


def datacheck_GetData(resquest):


# Create your views here.
    context = {}
    ran=random.randint(0,50)
   # picturename=
    if resquest.method == "POST":
        connect = pymysql.Connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='8200506',
            db='test',
            charset='utf8'
        )
        cursor = connect.cursor()
        datapicture_form = datacheckForm(data=resquest.POST, auto_id="%s")
        context['datapicture_form'] = datapicture_form
        print(datapicture_form.is_valid())
        if datapicture_form.is_valid():
            originyear = datapicture_form.cleaned_data['originyear']
            originmonth = datapicture_form.cleaned_data['originmonth']
            originday = datapicture_form.cleaned_data['originday']
            endyear = datapicture_form.cleaned_data['endyear']
            endmonth = datapicture_form.cleaned_data['endmonth']
            endday = datapicture_form.cleaned_data['endday']
            intersectionid=datapicture_form.cleaned_data['intersectionid']
            time_lenth=datapicture_form.cleaned_data['time_lenth']



            t = datacheck.objects.get(id=1)
            t.originyear=originyear
            t.originmonth=originmonth
            t.originday=originday
            t.endyear=endyear
            t.endmonth=endmonth
            t.endday=endday
            t.intersectionid=intersectionid
            t.time_lenth=time_lenth
            t.save()

            def gettsclanelist():  # 读取渠化信息
                p = []
                results = Tsclane.objects.all()
                for row in results:
                    if row.sid != 0:
                        sid = row.sid
                        movement = row.movement
                        dircetion = row.direction
                        intersectionld = row.intersectionid
                        p.append([sid, movement, dircetion, intersectionld])
                return p

            tsclane = gettsclanelist()
            print("初始化完成 %s" % ctime())

            def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
                t = []
                for row in a:
                    if row[3] == b:
                        t.append(row)
                return t

            def dayperiodreadlist(b, y, m, d, y1, m1, d1, t):  # 读取路口数据存入列表 a b c年月日，t：时间间隔
                day = d
                step = int((d1 - d) * 24 * 60 / t)
                y = str(y)
                m = str(m)
                d = str(d)

                y1 = str(y1)
                m1 = str(m1)
                d1 = str(d1)

                t1 = y + '-' + m + '-' + d + ' ' + '0:0:0'
                t2 = y1 + '-' + m1 + '-' + d1 + ' ' + '0:0:0'

                print(t1)
                print(t2)

                allcar = []
                # a1="select * from %s WHERE passtime BETWEEN '20170526' and '20170527'"
                # a1 = "select * from %s WHERE passtime BETWEEN '2017-05-26 0:0:0' and '2017-05-26 23:59:59'"
                a2 = "select * from %s WHERE passtime BETWEEN '%s' and '%s'"

                hour = 0
                timelist = []
                for i in range(step + 1):
                    min = i * t
                    if min % 60 == 0 and min != 0:
                        min = 0
                        hour = hour + 1
                    else:
                        min = min - int(min / 60) * 60
                    if hour % 24 == 0 and hour != 0:
                        hour = 0
                        day = day + 1
                    time1 = y + '-' + m + '-' + str(day) + ' ' + str(hour) + ":" + str(min) + ":" + "0"
                    timelist.append(time1)
                cursor.execute(a2 % (b, t1, t2))
                results = cursor.fetchall()
                row_num = 0;
                for i in range(step):

                    car = []

                    for j in range(len(results) - row_num):
                        id = results[j + row_num][0]
                        inteid = results[j + row_num][1]
                        direction = results[j + row_num][2]
                        lane = results[j + row_num][3]
                        carplate = results[j + row_num][4]
                        passtime = results[j + row_num][5]
                        traveltime = results[j + row_num][6]
                        upinteid = results[j + row_num][7]
                        updirection = results[j + row_num][8]
                        uplane = results[j + row_num][9]
                        if passtime >= datetime.strptime(timelist[i],
                                                         '%Y-%m-%d %H:%M:%S') and passtime < datetime.strptime(
                                timelist[i + 1], '%Y-%m-%d %H:%M:%S'):
                            # print(1)
                            car.append(
                                [id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection,
                                 uplane])
                        else:
                            row_num = row_num + len(car)
                            break
                    allcar.append(car)
                # for i in range(step):
                #     cursor.execute(a2 % (b, timelist[i], timelist[i + 1]))
                #     results = cursor.fetchall()
                #     print('第'+str(i+1)+"段数据读取完成")
                #     car = []
                #     for rowa in results:
                #         id = rowa[0]
                #         inteid = rowa[1]
                #         direction = rowa[2]
                #         lane = rowa[3]
                #         carplate = rowa[4]
                #         passtime = rowa[5]
                #         traveltime = rowa[6]
                #         upinteid = rowa[7]
                #         updirection = rowa[8]
                #         uplane = rowa[9]
                #         car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection,
                #                     uplane])
                #     allcar.append(car)
                return allcar, timelist

            # daycarlist=dayperiodreadlist('i056',2017,5,24,2017,5,25,30)
            # # print(daycarlist[0],daycarlist[len(daycarlist)-1])
            # print(" 读取路口当前时间段数据库完成 %s" % ctime())

            def getlanesid(a, b):  # 得到对应sid的direction和lane   a:渠化列表 b 路口sid
                k = [0, 0]
                d0 = []
                d2 = []
                d4 = []
                d6 = []
                for row in a:  # 得到各个direcition lane的个数
                    if row[2] == 0:
                        d0.append(row)
                    elif row[2] == 2:
                        d2.append(row)
                    elif row[2] == 4:
                        d4.append(row)
                    elif row[2] == 6:
                        d6.append(row)
                for row in a:
                    if row[0] == b:  # sid相等采匹配k[0]和k[1]
                        k[0] = row[2]  # direction
                        if k[0] == 6:
                            k[1] = row[0]  # lane
                        elif k[0] == 4:
                            k[1] = row[0] - len(d6)
                        elif k[0] == 2:
                            k[1] = row[0] - len(d6) - len(d4)
                        elif k[0] == 0:
                            k[1] = row[0] - len(d6) - len(d4) - len(d2)
                return k

            # 输出sid对应的direction和lane

            def laneclass(a, b, c):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
                p = []
                p = getlanesid(b, c)
                c = p[0]  # direction
                d = p[1]  # lane
                t = []
                for row in a:
                    if row[2] == c and row[3] == d:
                        t.append(row)
                return t

            # print(len(idtsclane))
            def automakesidlist(a, b):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
                sidlen = len(b)
                f = []
                for i in range(sidlen):
                    v = []
                    v = laneclass(a, b, i + 1)
                    f.append(v)
                return f

            def main_make(a, b, y, m, d, y1, m1, d1, t):
                idtsclane = []
                picture_makelist = []
                idtsclane = getidtsclane(tsclane, a)
                sql_insert = "insert into %s(id,intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values () "
                print(" 读取选择路口渠化信息完成 %s" % ctime())
                daycarlist, timelist = dayperiodreadlist(b, y, m, d, y1, m1, d1, t)
                print(" 读取路口当前时间段数据库完成 %s" % ctime())
                allsidlanelist = []
                for i in range(len(daycarlist)):
                    sidlanelist = []
                    sidlanelist = automakesidlist(daycarlist[i], idtsclane)  # sidlanelist是一个列表，长度是路口总id长度，里面包含了对应sid的列表
                    allsidlanelist.append(sidlanelist)

                name = str(y) + str(m) + str(d) + '_' + str(y1) + str(m1) + str(d1)+'_'+str(a)+'_'+str(t)
                sql_drop = "drop table if EXISTS %s"
                sql_maketable = "create table %s(id int(11) not null AUTO_INCREMENT,PRIMARY KEY (id),intersectionid int(11) not null,direction int(11) not null,lane int(11) not null,timequantum_start DATETIME NOT NULL,timequantum_end DATETIME NOT NULL,timequantum_lenth INT(11) NOT NULL)engine=innoDB"
                sql_maketable = "create table %s(id int(11) not null AUTO_INCREMENT,PRIMARY KEY (id),intersectionid int(11) not null,direction int(11) not null,lane int(11) not null,timequantum_start DATETIME ,timequantum_end DATETIME ,timequantum_lenth INT(11) NOT NULL)engine=innoDB"
                cursor.execute(sql_drop % (name))
                cursor.execute(sql_maketable % (name))
                print(" 当前时间段错误数据数据库生成完成 %s" % ctime())
                mistake_list = []
                mistake_id = 0
                i = 0
                # cursor.execute("insert into 2017524_2017525(id) VALUES(1)")
                # time_start1 = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')
                # time_end1 = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')


                sql_insert = "insert into 2017524_2017525(id,intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values(1,1,1,1,'%s','%s',1)"
                # cursor.execute(sql_insert)
                # cursor.execute(sql_insert % (time_start1,time_end1))
                # connect.commit()
                for row_time in allsidlanelist:
                    sid = 0

                    for row_sid in row_time:

                        sid = sid + 1
                        dirction_lane = getlanesid(idtsclane, sid)
                        if len(row_sid) == 0:
                            mistake_id = mistake_id + 1
                            mistake_list.append(
                                [mistake_id, a, dirction_lane[0], dirction_lane[1], timelist[i], timelist[i + 1], t])
                            time_start = datetime.strptime(timelist[i], '%Y-%m-%d %H:%M:%S')
                            time_end = datetime.strptime(timelist[i + 1], '%Y-%m-%d %H:%M:%S')
                            # print(time_start,time_end)
                            sql_insert = "insert into %s(intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values('%d','%d','%d','%s','%s','%d')"
                            cursor.execute(
                                sql_insert % (name, a, dirction_lane[0], dirction_lane[1], time_start, time_end, t))
                            connect.commit()
                            picture_makelist.append(0)
                        else:
                            picture_makelist.append(1)
                    i = i + 1

                return mistake_list, idtsclane, picture_makelist

            s = 'i0' + str(intersectionid)
            mistake_list, picture_idtsclane, picture_makelist = main_make(intersectionid, s, originyear, originmonth,
                                                                          originday, endyear, endmonth, endday,
                                                                          time_lenth)
            # print(mistake_list[len(mistake_list) - 1])
            print(len(mistake_list))
            connect.close()
            print("完成%s" % ctime())

            fig = plt.figure()
            fig.set_figheight(8)
            fig.set_figwidth(15)
            ax = fig.add_subplot(111)
            ax.set_xlim(0, 4)
            ax.set_ylim(0, 2)

            ax.set_yticks([])

            def pathmaker(a, b, c, d):  # a:点组，b：路劲组，c：颜色参数
                if len(a) != 0:
                    path = Path(a, b)
                    patch = patches.PathPatch(path, facecolor=c, alpha=0.8, edgecolor=d)
                    ax.add_patch(patch)

            def picture_make(t, a, b):  # t:监控时间范围，a：id渠化信息，b：颜色生成信息
                x_step = int(24 * 60 / t)
                y_step = len(a)
                # print(x_step*y_step)
                x_interval = round(2 / x_step, 2)
                x_interval = 4 / x_step
                y_interval = round(2 / y_step, 2)
                y_interval = 2 / y_step
                step = 0
                ax.set_xticks(np.linspace(0, 4,25))
                ax.set_yticks(np.linspace(0, 2, y_step + 1))
                xticklist = []
                yticklist = []
                for i in range(x_step + 1):
                    xticklist.append(str(i))
                ax.set_xticklabels(xticklist)
                for i in range(y_step):
                    yticklist.append(str(i + 1))
                ax.set_yticklabels(yticklist)
                for tick in ax.yaxis.get_majorticklabels():
                    tick.set_verticalalignment("bottom")
                color_list = ['gold','hotpink','firebrick','indianred','yellow','black','olive','darkseagreen','pink','tomato','lightcoral','orangered','palegreen','burlywood','black','fuchsia','papayawhip','orange','black','blue','brown','plum','cyan']
                for j in range(x_step):
                    for i in range(y_step):
                        pointpath = [(j * x_interval, i * y_interval), (j * x_interval, (i + 1) * y_interval),
                                     ((j + 1) * x_interval, (i + 1) * y_interval),
                                     ((j + 1) * x_interval, i * y_interval),
                                     (j * x_interval, i * y_interval)]
                        pointcodes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
                        if b[step] == 1:
                            pathmaker(pointpath, pointcodes, color_list[i], 'black')
                            step = step + 1
                        else:
                            pathmaker(pointpath, pointcodes, 'none', 'black')
                            step = step + 1

            picture_make(time_lenth, picture_idtsclane, picture_makelist)
            # plt.text(4,2,'横坐标：时间间隔'+'t',horizontalalignment='right',va='top')
            # plt.show()
            name = str(t.originyear) + str(t.originmonth) + str(t.originday) + '_' + str(t.endyear) + str(t.endmonth) + str(t.endday)+'_'+str(t.intersectionid)+'_'+str(t.time_lenth)
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
            plt.savefig(path+"\static\images\_datacheck\show/" + 'datacheck' +str(ran)+ '.jpg', dpi=300)
            plt.savefig(path+"\static\images\_datacheck\save/" + name + '.jpg', dpi=300)
            plt.close()

        # return render(resquest,'flowchart.html',{context})
    else:

        datapicture_form = datacheckForm();
        context['datapicture_form'] =datapicture_form;
    context['netpicture']='\static\images\_datacheck\show/' + 'datacheck' +str(ran)+ '.jpg'
    # n = chartdate.objects.get(id=1)
    # date = str(n.year) + '.' + str(n.month) + '.' + str(n.day)
    # id = n.direction
    # origin = n.Xaxisa
    # end = n.Xaxisb
    # perior = n.Yaxis
    # sid = str(n.Alane) + '.' + str(n.Blane) + '.' + str(n.Clane) + '.' + str(n.Dlane)
    # context['date'] = date
    # context['id'] = id
    # context['origin'] = origin
    # context['end'] = end
    # context['perior'] = perior
    # context['sid'] = sid
    return render(resquest, 'datacheck.html', context)

def phasecheck_GetData(resquest):
    context={}
    phasecheck_form =phasecheckFrom(data=resquest.POST, auto_id="%s")
    context['phasecheck_form'] = phasecheck_form
    print(phasecheck_form.is_valid())
    if phasecheck_form.is_valid():
        originyear = phasecheck_form.cleaned_data['originyear']
        originmonth = phasecheck_form.cleaned_data['originmonth']
        originday = phasecheck_form.cleaned_data['originday']
        intersectionid_s = phasecheck_form.cleaned_data['intersectionid_s']
        intersectionid_e = phasecheck_form.cleaned_data['intersectionid_e']

        t = phasecheck.objects.get(id=1)
        t.originyear = originyear
        t.originmonth = originmonth
        t.originday = originday
        t.intersectionid_s = intersectionid_s
        t.intersectionid_e = intersectionid_e
        t.save()
        sleep(5)
        context['conclusion1'] = "原相位差为0秒，相位差不合理"
        context['conclusion2'] = '参考优化结果：68秒'
    else:
        datapicture_form = datacheckForm();
        context['datapicture_form'] = datapicture_form;
        context['conclusion1']="相位差评价："
        context['conclusion2'] ='参考优化结果：'
    return render(resquest, 'phasecheck.html', context)


def datacheck_show(resquest):
    connect = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='8200506',
        db='test',
        charset='utf8'
    )
    cursor = connect.cursor()
    context = {}
    datapicture_form = datacheckForm();
    context['datapicture_form'] = datapicture_form;
    t = datacheck.objects.get(id=1)
    originyear= t.originyear
    originmonth = t.originmonth
    originday= t.originday
    endyear = t.endyear
    endmonth = t.endmonth
    endday = t.endday
    intersectionid=t.intersectionid
    time_lenth=t.time_lenth

    PictureData = [originyear,originmonth,originday,endyear,endmonth,endday,intersectionid,time_lenth]
    print(PictureData)

    def gettsclanelist():  # 读取渠化信息
        p = []
        results = Tsclane.objects.all()
        for row in results:
            if row.sid != 0:
                sid = row.sid
                movement = row.movement
                dircetion = row.direction
                intersectionld = row.intersectionid
                p.append([sid, movement, dircetion, intersectionld])
        return p

    tsclane = gettsclanelist()
    print("初始化完成 %s" % ctime())

    def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
        t = []
        for row in a:
            if row[3] == b:
                t.append(row)
        return t

    def dayperiodreadlist(b, y, m, d, y1, m1, d1, t):  # 读取路口数据存入列表 a b c年月日，t：时间间隔
        day = d
        step = int((d1 - d) * 24 * 60 / t)
        y = str(y)
        m = str(m)
        d = str(d)

        y1 = str(y1)
        m1 = str(m1)
        d1 = str(d1)

        t1 = y + '-' + m + '-' + d + ' ' + '0:0:0'
        t2 = y1 + '-' + m1 + '-' + d1 + ' ' + '0:0:0'

        print(t1)
        print(t2)

        allcar = []
        # a1="select * from %s WHERE passtime BETWEEN '20170526' and '20170527'"
        # a1 = "select * from %s WHERE passtime BETWEEN '2017-05-26 0:0:0' and '2017-05-26 23:59:59'"
        a2 = "select * from %s WHERE passtime BETWEEN '%s' and '%s'"

        hour = 0
        timelist = []
        for i in range(step + 1):
            min = i * t
            if min % 60 == 0 and min != 0:
                min = 0
                hour = hour + 1
            else:
                min = min - int(min / 60) * 60
            if hour % 24 == 0 and hour != 0:
                hour = 0
                day = day + 1
            time1 = y + '-' + m + '-' + str(day) + ' ' + str(hour) + ":" + str(min) + ":" + "0"
            timelist.append(time1)
        for i in range(step):
            cursor.execute(a2 % (b, timelist[i], timelist[i + 1]))
            results = cursor.fetchall()
            car = []
            for rowa in results:
                id = rowa[0]
                inteid = rowa[1]
                direction = rowa[2]
                lane = rowa[3]
                carplate = rowa[4]
                passtime = rowa[5]
                traveltime = rowa[6]
                upinteid = rowa[7]
                updirection = rowa[8]
                uplane = rowa[9]
                car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection, uplane])
            allcar.append(car)
        return allcar, timelist

    # daycarlist=dayperiodreadlist('i056',2017,5,24,2017,5,25,30)
    # # print(daycarlist[0],daycarlist[len(daycarlist)-1])
    # print(" 读取路口当前时间段数据库完成 %s" % ctime())

    def getlanesid(a, b):  # 得到对应sid的direction和lane   a:渠化列表 b 路口sid
        k = [0, 0]
        d0 = []
        d2 = []
        d4 = []
        d6 = []
        for row in a:  # 得到各个direcition lane的个数
            if row[2] == 0:
                d0.append(row)
            elif row[2] == 2:
                d2.append(row)
            elif row[2] == 4:
                d4.append(row)
            elif row[2] == 6:
                d6.append(row)
        for row in a:
            if row[0] == b:  # sid相等采匹配k[0]和k[1]
                k[0] = row[2]  # direction
                if k[0] == 6:
                    k[1] = row[0]  # lane
                elif k[0] == 4:
                    k[1] = row[0] - len(d6)
                elif k[0] == 2:
                    k[1] = row[0] - len(d6) - len(d4)
                elif k[0] == 0:
                    k[1] = row[0] - len(d6) - len(d4) - len(d2)
        return k

    # 输出sid对应的direction和lane

    def laneclass(a, b, c):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
        p = []
        p = getlanesid(b, c)
        c = p[0]  # direction
        d = p[1]  # lane
        t = []
        for row in a:
            if row[2] == c and row[3] == d:
                t.append(row)
        return t

    # print(len(idtsclane))
    def automakesidlist(a, b):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
        sidlen = len(b)
        f = []
        for i in range(sidlen):
            v = []
            v = laneclass(a, b, i + 1)
            f.append(v)
        return f

    def main_make(a, b, y, m, d, y1, m1, d1, t):
        idtsclane = []
        picture_makelist = []
        idtsclane = getidtsclane(tsclane, a)
        sql_insert = "insert into %s(id,intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values () "
        print(" 读取选择路口渠化信息完成 %s" % ctime())
        daycarlist, timelist = dayperiodreadlist(b, y, m, d, y1, m1, d1, t)
        print(" 读取路口当前时间段数据库完成 %s" % ctime())
        allsidlanelist = []
        for i in range(len(daycarlist)):
            sidlanelist = []
            sidlanelist = automakesidlist(daycarlist[i], idtsclane)  # sidlanelist是一个列表，长度是路口总id长度，里面包含了对应sid的列表
            allsidlanelist.append(sidlanelist)

        name = str(y) + str(m) + str(d) + '_' + str(y1) + str(m1) + str(d1)
        sql_drop = "drop table if EXISTS %s"
        sql_maketable = "create table %s(id int(11) not null AUTO_INCREMENT,PRIMARY KEY (id),intersectionid int(11) not null,direction int(11) not null,lane int(11) not null,timequantum_start DATETIME NOT NULL,timequantum_end DATETIME NOT NULL,timequantum_lenth INT(11) NOT NULL)engine=innoDB"
        sql_maketable = "create table %s(id int(11) not null AUTO_INCREMENT,PRIMARY KEY (id),intersectionid int(11) not null,direction int(11) not null,lane int(11) not null,timequantum_start DATETIME ,timequantum_end DATETIME ,timequantum_lenth INT(11) NOT NULL)engine=innoDB"
        cursor.execute(sql_drop % (name))
        cursor.execute(sql_maketable % (name))
        print(" 当前时间段错误数据数据库生成完成 %s" % ctime())
        mistake_list = []
        mistake_id = 0
        i = 0
        # cursor.execute("insert into 2017524_2017525(id) VALUES(1)")
        # time_start1 = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')
        # time_end1 = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')


        sql_insert = "insert into 2017524_2017525(id,intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values(1,1,1,1,'%s','%s',1)"
        # cursor.execute(sql_insert)
        # cursor.execute(sql_insert % (time_start1,time_end1))
        # connect.commit()
        for row_time in allsidlanelist:
            sid = 0

            for row_sid in row_time:

                sid = sid + 1
                dirction_lane = getlanesid(idtsclane, sid)
                if len(row_sid) == 0:
                    mistake_id = mistake_id + 1
                    mistake_list.append(
                        [mistake_id, a, dirction_lane[0], dirction_lane[1], timelist[i], timelist[i + 1], t])
                    time_start = datetime.strptime(timelist[i], '%Y-%m-%d %H:%M:%S')
                    time_end = datetime.strptime(timelist[i + 1], '%Y-%m-%d %H:%M:%S')
                    # print(time_start,time_end)
                    sql_insert = "insert into %s(intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values('%d','%d','%d','%s','%s','%d')"
                    cursor.execute(sql_insert % (name, a, dirction_lane[0], dirction_lane[1], time_start, time_end, t))
                    connect.commit()
                    picture_makelist.append(0)
                else:
                    picture_makelist.append(1)
            i = i + 1

        return mistake_list, idtsclane, picture_makelist
    s='i0'+str(intersectionid)
    mistake_list, picture_idtsclane, picture_makelist = main_make(intersectionid, s, originyear, originmonth, originday, endyear,endmonth, endday, time_lenth)
    #print(mistake_list[len(mistake_list) - 1])
    print(len(mistake_list))
    connect.close()
    print("完成%s" % ctime())

    fig = plt.figure()
    fig.set_figheight(8)
    fig.set_figwidth(15)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 2)

    ax.set_yticks([])

    def pathmaker(a, b, c, d):  # a:点组，b：路劲组，c：颜色参数
        if len(a) != 0:
            path = Path(a, b)
            patch = patches.PathPatch(path, facecolor=c, alpha=0.8, edgecolor=d)
            ax.add_patch(patch)

    def picture_make(t, a, b):  # t:监控时间范围，a：id渠化信息，b：颜色生成信息
        x_step = int(24 * 60 / t)
        y_step = len(a)
        # print(x_step*y_step)
        x_interval = round(2 / x_step, 2)
        x_interval = 4 / x_step
        y_interval = round(2 / y_step, 2)
        y_interval = 2 / y_step
        step = 0
        ax.set_xticks(np.linspace(0, 4, x_step + 1))
        ax.set_yticks(np.linspace(0, 2, y_step + 1))
        xticklist = []
        yticklist = []
        for i in range(x_step + 1):
            xticklist.append(str(i))
        ax.set_xticklabels(xticklist)
        for i in range(y_step):
            yticklist.append(str(i + 1))
        ax.set_yticklabels(yticklist)
        for tick in ax.yaxis.get_majorticklabels():
            tick.set_verticalalignment("bottom")
        color_list = ['gold', 'hotpink', 'firebrick', 'indianred', 'yellow', 'mistyrose', 'olive', 'darkseagreen',
                      'pink', 'tomato', 'lightcoral', 'orangered', 'palegreen', 'burlywood', 'seashell', 'fuchsia',
                      'papayawhip', 'orange', 'black', 'blue', 'brown', 'plum', 'cyan']
        for j in range(x_step):
            for i in range(y_step):
                pointpath = [(j * x_interval, i * y_interval), (j * x_interval, (i + 1) * y_interval),
                             ((j + 1) * x_interval, (i + 1) * y_interval), ((j + 1) * x_interval, i * y_interval),
                             (j * x_interval, i * y_interval)]
                pointcodes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
                if b[step] == 1:
                    pathmaker(pointpath, pointcodes, color_list[i], 'black')
                    step = step + 1
                else:
                    pathmaker(pointpath, pointcodes, 'none', 'black')
                    step = step + 1

    picture_make(time_lenth, picture_idtsclane, picture_makelist)
    # plt.text(4,2,'横坐标：时间间隔'+'t',horizontalalignment='right',va='top')
    # plt.show()
    plt.savefig("D:\pythonwork\jiaotongweb\chart\static/"+'datacheck'+'.jpg', dpi=300)
    return render(resquest, 'datacheckshow.html', context)

def detection_GetData(resquest):
    context = {}
    ran = random.randint(0, 50)
    # picturename=
    conclusion1=[]
    conclusion2=[]
    #conclusion1text="车道监测：\n"
    if resquest.method == "POST":
        connect = pymysql.Connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='8200506',
            db='test',
            charset='utf8'
        )
        cursor = connect.cursor()
        datapicture_form = datacheckForm(data=resquest.POST, auto_id="%s")
        context['datapicture_form'] = datapicture_form
        print(datapicture_form.is_valid())
        if datapicture_form.is_valid():
            originyear = datapicture_form.cleaned_data['originyear']
            originmonth = datapicture_form.cleaned_data['originmonth']
            originday = datapicture_form.cleaned_data['originday']
            #endyear = datapicture_form.cleaned_data['endyear']
            #endmonth = datapicture_form.cleaned_data['endmonth']
            #endday = datapicture_form.cleaned_data['endday']
            intersectionid = datapicture_form.cleaned_data['intersectionid']
            time_lenth = datapicture_form.cleaned_data['time_lenth']

            t = datacheck.objects.get(id=1)
            t.originyear = originyear
            t.originmonth = originmonth
            t.originday = originday
            t.endyear = originyear
            t.endmonth = originmonth
            t.endday = originday+1
            t.intersectionid = intersectionid
            t.time_lenth = time_lenth
            t.save()

            def gettsclanelist():  # 读取渠化信息
                p = []
                results = Tsclane.objects.all()
                for row in results:
                    if row.sid != 0:
                        sid = row.sid
                        movement = row.movement
                        dircetion = row.direction
                        intersectionld = row.intersectionid
                        p.append([sid, movement, dircetion, intersectionld])
                return p

            tsclane = gettsclanelist()
            print("初始化完成 %s" % ctime())

            def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
                t = []
                for row in a:
                    if row[3] == b:
                        t.append(row)
                return t

            def dayperiodreadlist(b, y, m, d, y1, m1, d1, t):  # 读取路口数据存入列表 a b c年月日，t：时间间隔
                day = d
                step = int((d1 - d) * 24 * 60 / t)
                y = str(y)
                m = str(m)
                d = str(d)

                y1 = str(y1)
                m1 = str(m1)
                d1 = str(d1)

                t1 = y + '-' + m + '-' + d + ' ' + '0:0:0'
                t2 = y1 + '-' + m1 + '-' + d1 + ' ' + '0:0:0'

                print(t1)
                print(t2)

                allcar = []
                # a1="select * from %s WHERE passtime BETWEEN '20170526' and '20170527'"
                # a1 = "select * from %s WHERE passtime BETWEEN '2017-05-26 0:0:0' and '2017-05-26 23:59:59'"
                a2 = "select * from %s WHERE passtime BETWEEN '%s' and '%s'"

                hour = 0
                timelist = []
                for i in range(step + 1):
                    min = i * t
                    if min % 60 == 0 and min != 0:
                        min = 0
                        hour = hour + 1
                    else:
                        min = min - int(min / 60) * 60
                    if hour % 24 == 0 and hour != 0:
                        hour = 0
                        day = day + 1
                    time1 = y + '-' + m + '-' + str(day) + ' ' + str(hour) + ":" + str(min) + ":" + "0"
                    timelist.append(time1)
                cursor.execute(a2 % (b, t1, t2))
                results = cursor.fetchall()
                row_num = 0;
                for i in range(step):

                    car = []

                    for j in range(len(results) - row_num):
                        id = results[j + row_num][0]
                        inteid = results[j + row_num][1]
                        direction = results[j + row_num][2]
                        lane = results[j + row_num][3]
                        carplate = results[j + row_num][4]
                        passtime = results[j + row_num][5]
                        traveltime = results[j + row_num][6]
                        upinteid = results[j + row_num][7]
                        updirection = results[j + row_num][8]
                        uplane = results[j + row_num][9]
                        if passtime >= datetime.strptime(timelist[i],
                                                         '%Y-%m-%d %H:%M:%S') and passtime < datetime.strptime(
                            timelist[i + 1], '%Y-%m-%d %H:%M:%S'):
                            # print(1)
                            car.append(
                                [id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection,
                                 uplane])
                        else:
                            row_num = row_num + len(car)
                            break
                    allcar.append(car)
                # for i in range(step):
                #     cursor.execute(a2 % (b, timelist[i], timelist[i + 1]))
                #     results = cursor.fetchall()
                #     print('第'+str(i+1)+"段数据读取完成")
                #     car = []
                #     for rowa in results:
                #         id = rowa[0]
                #         inteid = rowa[1]
                #         direction = rowa[2]
                #         lane = rowa[3]
                #         carplate = rowa[4]
                #         passtime = rowa[5]
                #         traveltime = rowa[6]
                #         upinteid = rowa[7]
                #         updirection = rowa[8]
                #         uplane = rowa[9]
                #         car.append([id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection,
                #                     uplane])
                #     allcar.append(car)
                return allcar, timelist

            # daycarlist=dayperiodreadlist('i056',2017,5,24,2017,5,25,30)
            # # print(daycarlist[0],daycarlist[len(daycarlist)-1])
            # print(" 读取路口当前时间段数据库完成 %s" % ctime())

            def getlanesid(a, b):  # 得到对应sid的direction和lane   a:渠化列表 b 路口sid
                k = [0, 0,0]
                d0 = []
                d2 = []
                d4 = []
                d6 = []
                for row in a:  # 得到各个direcition lane的个数
                    if row[2] == 0:
                        d0.append(row)
                    elif row[2] == 2:
                        d2.append(row)
                    elif row[2] == 4:
                        d4.append(row)
                    elif row[2] == 6:
                        d6.append(row)
                for row in a:
                    if row[0] == b:  # sid相等采匹配k[0]和k[1]
                        k[0] = row[2]  # direction
                        k[2] = row[1]
                        if k[0] == 6:
                            k[1] = row[0]  # lane
                        elif k[0] == 4:
                            k[1] = row[0] - len(d6)
                        elif k[0] == 2:
                            k[1] = row[0] - len(d6) - len(d4)
                        elif k[0] == 0:
                            k[1] = row[0] - len(d6) - len(d4) - len(d2)
                return k

            # 输出sid对应的direction和lane

            def laneclass(a, b, c):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
                p = []
                p = getlanesid(b, c)
                c = p[0]  # direction
                d = p[1]  # lane
                t = []
                for row in a:
                    if row[2] == c and row[3] == d:
                        t.append(row)
                return t

            # print(len(idtsclane))
            def automakesidlist(a, b):  # a daycarlist b选择路口的渠化信息 c路口sid  得到对应sid的列表
                sidlen = len(b)
                f = []
                for i in range(sidlen):
                    v = []
                    v = laneclass(a, b, i + 1)
                    f.append(v)
                return f

            def main_make(a, b, y, m, d, y1, m1, d1, t):
                idtsclane = []
                picture_makelist = []
                idtsclane = getidtsclane(tsclane, a)
                sql_insert = "insert into %s(id,intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values () "
                print(" 读取选择路口渠化信息完成 %s" % ctime())
                daycarlist, timelist = dayperiodreadlist(b, y, m, d, y1, m1, d1, t)
                print(" 读取路口当前时间段数据库完成 %s" % ctime())
                allsidlanelist = []
                for i in range(len(daycarlist)):
                    sidlanelist = []
                    sidlanelist = automakesidlist(daycarlist[i], idtsclane)  # sidlanelist是一个列表，长度是路口总id长度，里面包含了对应sid的列表
                    allsidlanelist.append(sidlanelist)

                name = str(y) + str(m) + str(d) + '_' + str(y1) + str(m1) + str(d1) + '_' + str(a) + '_' + str(t)
                sql_drop = "drop table if EXISTS %s"
                sql_maketable = "create table %s(id int(11) not null AUTO_INCREMENT,PRIMARY KEY (id),intersectionid int(11) not null,direction int(11) not null,lane int(11) not null,timequantum_start DATETIME NOT NULL,timequantum_end DATETIME NOT NULL,timequantum_lenth INT(11) NOT NULL)engine=innoDB"
                sql_maketable = "create table %s(id int(11) not null AUTO_INCREMENT,PRIMARY KEY (id),intersectionid int(11) not null,direction int(11) not null,lane int(11) not null,timequantum_start DATETIME ,timequantum_end DATETIME ,timequantum_lenth INT(11) NOT NULL)engine=innoDB"
                cursor.execute(sql_drop % (name))
                cursor.execute(sql_maketable % (name))
                print(" 当前时间段错误数据数据库生成完成 %s" % ctime())
                mistake_list = []
                mistake_id = 0
                i = 0
                # cursor.execute("insert into 2017524_2017525(id) VALUES(1)")
                # time_start1 = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')
                # time_end1 = datetime.strptime('2015-6-1 18:19:59', '%Y-%m-%d %H:%M:%S')


                sql_insert = "insert into 2017524_2017525(id,intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values(1,1,1,1,'%s','%s',1)"
                # cursor.execute(sql_insert)
                # cursor.execute(sql_insert % (time_start1,time_end1))
                # connect.commit()
                for row_time in allsidlanelist:
                    sid = 0

                    for row_sid in row_time:

                        sid = sid + 1
                        dirction_lane = getlanesid(idtsclane, sid)
                        if len(row_sid) == 0:
                            mistake_id = mistake_id + 1
                            mistake_list.append(
                                [mistake_id, a, dirction_lane[0], dirction_lane[1], timelist[i], timelist[i + 1], t])
                            time_start = datetime.strptime(timelist[i], '%Y-%m-%d %H:%M:%S')
                            time_end = datetime.strptime(timelist[i + 1], '%Y-%m-%d %H:%M:%S')
                            # print(time_start,time_end)
                            sql_insert = "insert into %s(intersectionid,direction,lane,timequantum_start,timequantum_end,timequantum_lenth) values('%d','%d','%d','%s','%s','%d')"
                            cursor.execute(
                                sql_insert % (name, a, dirction_lane[0], dirction_lane[1], time_start, time_end, t))
                            connect.commit()
                            picture_makelist.append(0)
                        else:
                            picture_makelist.append(1)
                    i = i + 1

                return mistake_list, idtsclane, picture_makelist

            s = 'i0' + str(intersectionid)
            mistake_list, picture_idtsclane, picture_makelist = main_make(intersectionid, s, originyear, originmonth,
                                                                          originday, originyear,originmonth, originday+1,
                                                                          time_lenth)
            # print(mistake_list[len(mistake_list) - 1])
            print(len(mistake_list))
            #connect.close()
            print("完成%s" % ctime())

            fig = plt.figure()
            fig.set_figheight(8)
            fig.set_figwidth(15)
            ax = fig.add_subplot(111)
            ax.set_xlim(0, 4)
            ax.set_ylim(0, 2)

            ax.set_yticks([])

            def pathmaker(a, b, c, d):  # a:点组，b：路劲组，c：颜色参数
                if len(a) != 0:
                    path = Path(a, b)
                    patch = patches.PathPatch(path, facecolor=c, alpha=0.8, edgecolor=d)
                    ax.add_patch(patch)

            def picture_make(t, a, b):  # t:监控时间范围，a：id渠化信息，b：颜色生成信息
                x_step = int(24 * 60 / t)
                y_step = len(a)
                # print(x_step*y_step)
                x_interval = round(2 / x_step, 2)
                x_interval = 4 / x_step
                y_interval = round(2 / y_step, 2)
                y_interval = 2 / y_step
                step = 0
                ax.set_xticks(np.linspace(0, 4, 25))
                ax.set_yticks(np.linspace(0, 2, y_step + 1))
                xticklist = []
                yticklist = []
                for i in range(x_step + 1):
                    xticklist.append(str(i))
                ax.set_xticklabels(xticklist)
                for i in range(y_step):
                    yticklist.append(str(i + 1))
                ax.set_yticklabels(yticklist)
                for tick in ax.yaxis.get_majorticklabels():
                    tick.set_verticalalignment("bottom")
                color_list = ['gold', 'hotpink', 'firebrick', 'indianred', 'yellow', 'black', 'olive', 'darkseagreen',
                              'pink', 'tomato', 'lightcoral', 'orangered', 'palegreen', 'burlywood', 'black', 'fuchsia',
                              'papayawhip', 'orange', 'black', 'blue', 'brown', 'plum', 'cyan']
                for j in range(x_step):
                    for i in range(y_step):
                        pointpath = [(j * x_interval, i * y_interval), (j * x_interval, (i + 1) * y_interval),
                                     ((j + 1) * x_interval, (i + 1) * y_interval),
                                     ((j + 1) * x_interval, i * y_interval),
                                     (j * x_interval, i * y_interval)]
                        pointcodes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
                        if b[step] == 1:
                            pathmaker(pointpath, pointcodes, color_list[i], 'black')
                            step = step + 1
                        else:
                            pathmaker(pointpath, pointcodes, 'none', 'black')
                            step = step + 1

            picture_make(time_lenth, picture_idtsclane, picture_makelist)
            # plt.text(4,2,'横坐标：时间间隔'+'t',horizontalalignment='right',va='top')
            # plt.show()
            name = str(t.originyear) + str(t.originmonth) + str(t.originday) + '_' + str(t.endyear) + str(
                t.endmonth) + str(t.endday) + '_' + str(t.intersectionid) + '_' + str(t.time_lenth)
            # plt.savefig(
            #     "D:\pythonwork\jiaotongweb\chart\static\images\_datacheck\show/" + 'datacheck' + str(ran) + '.jpg',
            #     dpi=300)
            # plt.savefig("D:\pythonwork\jiaotongweb\chart\static\images\_datacheck\save/" + name + '.jpg', dpi=300)
            plt.close()

            basisinfo = []
            def getbasisinfo(a, b):
                t = []
                cursor.execute(a % (b))
                results = cursor.fetchall()
                for row in results:
                    name = row[2]
                    sid = row[1]
                    ringdata = row[6]
                    # bytes.fromhex(ringdata).decode('utf8')
                    scheduleDate = row[7]

                    t.append([name, sid, ringdata, scheduleDate])
                return t

            sqlm = "select * from %s"
            basisinfo = getbasisinfo(sqlm, "basisinfo")
            print("初始化环数据完成 %s" % ctime())

            rd_raw = []
            sd_raw = []

            def rd_raw_int():

                a = []
                for i in range(len(basisinfo)):
                    t = []
                    for j in range(len(basisinfo[i][2])):
                        # print(basisinfo[i][2][j:j+1][0])
                        t.append(basisinfo[i][2][j:j + 1][0])

                    a.append([basisinfo[i][1], t])

                return a

            def sd_raw_int():
                a = []
                for i in range(len(basisinfo)):
                    t = []
                    for j in range(len(basisinfo[i][3])):
                        # print(basisinfo[i][3][j:j+1][0])
                        t.append(basisinfo[i][3][j:j + 1][0])

                    a.append([basisinfo[i][1], t])
                return a

            rd_raw = rd_raw_int()
            sd_raw = sd_raw_int()

            print("解环完成 %s" % ctime())

            def decodeRingdata(a):
                ringData = []
                ringData_end = []
                i = 0
                num_table = a[i]
                ringData_end.append(num_table)
                i = i + 1
                tables = []
                for i1 in range(num_table):
                    table_sid = a[i] + 256 * a[i + 1] + 256 * 256 * a[i + 2] + 256 * 256 * 256 * a[i + 3]
                    i = i + 4
                    i = i + 26
                    table_offset = a[i]
                    i = i + 1
                    table_num_ring = a[i]
                    i = i + 1
                    # tables.append(table_sid)
                    # tables.append(table_offset)
                    # tables.append(table_num_ring)
                    rings = []
                    for i2 in range(table_num_ring):

                        ring_num_phase = a[i]
                        # rings.append(ring_num_phase)
                        i = i + 1
                        phase = []
                        for i3 in range(ring_num_phase):
                            phase_num_lane = a[i]
                            i = i + 1
                            phase_laneID = []
                            if phase_num_lane == 0:
                                phase_laneID = []
                            else:
                                for i4 in range(phase_num_lane):
                                    # phase_laneID[i4]=a[i]+256*a[i+1]
                                    phase_laneID.append(a[i] + 256 * a[i + 1])
                                    i = i + 2
                            phase_greenTime = a[i]
                            i = i + 1
                            phase_yellowTime = a[i]
                            i = i + 1
                            phase_redTime = a[i]
                            i = i + 1
                            phase.append(
                                [phase_num_lane, phase_laneID, phase_greenTime, phase_yellowTime, phase_redTime])

                        rings.append([ring_num_phase, phase])
                    tables.append([table_sid, table_offset, table_num_ring, rings])
                    # ringData.append([table_sid,table_offset,table_num_ring,tables])
                ringData_end.append(tables)
                return ringData_end

            def decodeScheduledata(a):
                i = 0
                num_table = a[i]
                i = i + 1
                t = []
                scheduledata = []
                for i1 in range(num_table):
                    table_sid = a[i] + 256 * a[i + 1] + 256 * 256 * a[i + 2] + 256 * 256 * 256 * a[i + 3]
                    i = i + 4
                    table_month = a[i] + 256 * a[i + 1]
                    i = i + 2
                    table_week = a[i]
                    i = i + 1
                    table_day = a[i] + 256 * a[i + 1] + 256 * 256 * a[i + 2] + 256 * 256 * 256 * a[i + 3]
                    i = i + 4
                    table_timeslotTable_sid = a[i] + 256 * a[i + 1] + 256 * 256 * a[i + 2] + 256 * 256 * 256 * a[i + 3]
                    i = i + 4
                    t.append([table_sid, table_month, table_week, table_day, table_timeslotTable_sid])
                scheduledata.append(num_table)
                scheduledata.append(t)

                timeslotdata = []
                i = i + 4
                t_num_table = a[i]
                i = i + 1
                tables = []
                for i2 in range(t_num_table):
                    table_sid = a[i] + 256 * a[i + 1] + 256 * 256 * a[i + 2] + 256 * 256 * 256 * a[i + 3]
                    i = i + 4
                    i = i + 26
                    table_num_timeSlot = a[i]
                    i = i + 1
                    time_slots = []
                    for i3 in range(table_num_timeSlot):
                        timeslot_hour = a[i]
                        i = i + 1
                        timeslot_min = a[i]
                        i = i + 1
                        timeslot_ringTable_sid = a[i] + 256 * a[i + 1] + 256 * 256 * a[i + 2] + 256 * 256 * 256 * a[
                            i + 3]
                        i = i + 4
                        time_slots.append([timeslot_hour, timeslot_min, timeslot_ringTable_sid])
                    tables.append([table_sid, table_num_timeSlot, time_slots])
                timeslotdata.append(t_num_table)
                timeslotdata.append(tables)

                return scheduledata, timeslotdata

            def Get_Timingscheme(y, m, d, dir):  # type整年时间规划
                time_start = datetime.strptime(str(y) + '-' + str(m) + '-' + str(d), '%Y-%m-%d')
                t = time_start.strftime('%A')  # 星期的英文名
                t1 = time_start.weekday()  # 0-6 星期一-星期天
                cell_key = 0
                if dir == 75:
                    cell_key = 0
                elif dir == 56:
                    cell_key = 1
                elif dir == 23:
                    cell_key = 2
                elif dir == 77:
                    cell_key = 3
                elif dir == 24:
                    cell_key = 4
                elif dir == 89:
                    cell_key = 5
                elif dir == 58:
                    cell_key = 6
                elif dir == 55:
                    cell_key = 7
                elif dir == 57:
                    cell_key = 8
                ringdata = decodeRingdata(rd_raw[cell_key][1])
                scheduledata, timeslotdata = decodeScheduledata(sd_raw[cell_key][1])
                scheduledata_table_num = scheduledata[0]
                scheduledata_table_list = []  # 全部table计划
                timedata = []  # 当天计划
                for i in range(scheduledata_table_num):
                    scheduledata_table_list.append(scheduledata[1][i])

                for raw in scheduledata_table_list:
                    table_month = raw[1]
                    table_week = raw[2]
                    table_day = raw[3]
                    table_timeslotTablesid = raw[4]
                    table_month_two = bin(table_month).replace('0b', '')
                    table_week_two = bin(table_week).replace('0b', '')
                    table_day_two = bin(table_day).replace('0b', '')
                    table_day_two_str = str(table_day_two)
                    for i2 in range(30 - len(table_day_two_str)):
                        table_day_two_str = '0' + table_day_two_str

                    if table_month_two[12 - m] == '1':
                        if table_week != 0:
                            if table_week_two[7 - t1] == '1':  # 符合日期
                                for raw1 in timeslotdata[1]:
                                    if raw1[0] == table_timeslotTablesid:
                                        num_timeslot = raw1[1]
                                        for raw2 in raw1[2]:
                                            timedata.append([raw2[0], raw2[1], raw2[2]])
                        elif table_day != 0:
                            if table_day_two_str[30 - d] == '1':
                                for raw1 in timeslotdata[1]:
                                    if raw1[0] == table_timeslotTablesid:
                                        num_timeslot = raw1[1]
                                        for raw2 in raw1[2]:
                                            timedata.append([raw2[0], raw2[1], raw2[2]])
                                        break

                return timedata

            timingscheme_day = Get_Timingscheme(originyear, originmonth, originday, intersectionid)  # 当前路口当天的计划安排

            def Get_Timingtable(a, dir):
                if a:
                    ringdata123 = []
                    if len(a):
                        cell_key = 0
                        if dir == 75:
                            cell_key = 0
                        elif dir == 56:
                            cell_key = 1
                        elif dir == 23:
                            cell_key = 2
                        elif dir == 77:
                            cell_key = 3
                        elif dir == 24:
                            cell_key = 4
                        elif dir == 89:
                            cell_key = 5
                        elif dir == 58:
                            cell_key = 6
                        elif dir == 55:
                            cell_key = 7
                        elif dir == 57:
                            cell_key = 8
                        timingscheme = a
                        ringdata = decodeRingdata(rd_raw[cell_key][1])

                        table = []
                        offset = []
                        num_ring = []
                        for i in range(len(timingscheme) - 1):

                            timingscheme_sid = timingscheme[i][2]

                            for raw in ringdata[1]:
                                if raw[0] == timingscheme_sid:
                                    # offset=raw[1]
                                    # num_ring=raw[2]
                                    offset.append(raw[1])
                                    num_ring.append(raw[2])
                                    rings = raw[3]
                                    rings_list = []
                                    for raw1 in rings:
                                        num_phase = raw1[0]
                                        phases = raw1[1]
                                        phases_list = []
                                        for raw2 in phases:
                                            num_lane = raw2[0]
                                            laneID = raw2[1]
                                            greentime = raw2[2]
                                            yellowtime = raw2[3]
                                            redtime = raw2[4]
                                            phases_list.append([num_lane, laneID, greentime, yellowtime, redtime])
                                        rings_list.append([num_phase, phases_list])
                            table.append([str(timingscheme[i][0]) + ':' + str(timingscheme[i][1]),
                                          str(timingscheme[i + 1][0]) + ':' + str(timingscheme[i + 1][1]), offset[i],
                                          num_ring[i], rings_list])
                            # ringdata123.append(table)
                    return table

            ringdata = Get_Timingtable(timingscheme_day, intersectionid)

            # ringdata[0][4][0][1][0][2]

            print("当前路口当天计划安排解析完成 %s" % ctime())



            def Get_daydate(y, m, d, dir, ringdata):
                if ringdata:
                    y_str = str(y)
                    m_str = str(m)
                    d_str = str(d)
                    a2 = "select * from %s WHERE passtime BETWEEN '%s' and '%s'"
                    # timelist=[]
                    detectiontimelist = []
                    datalist = []
                    for i in range(len(ringdata)):
                        hms_s = ringdata[i][0]
                        hms_e = ringdata[i][1]
                        time1 = y_str + '-' + m_str + '-' + d_str + ' ' + hms_s + ":" + "1"
                        time2 = y_str + '-' + m_str + '-' + d_str + ' ' + hms_e + ":" + "0"
                        print(time1, time2)
                        detectiontimelist.append([datetime.strptime(
                            y_str + '-' + m_str + '-' + d_str + ' ' + hms_s + ":" + "0", '%Y-%m-%d %H:%M:%S'),
                                                  datetime.strptime(
                                                      y_str + '-' + m_str + '-' + d_str + ' ' + hms_e + ":" + "0",
                                                      '%Y-%m-%d %H:%M:%S')])
                        t='i0'+str(dir)
                        cursor.execute(a2 % (t, time1, time2))
                        results = cursor.fetchall()
                        car = []
                        for rowa in results:
                            id = rowa[0]
                            inteid = rowa[1]
                            direction = rowa[2]
                            lane = rowa[3]
                            carplate = rowa[4]
                            passtime = rowa[5]
                            traveltime = rowa[6]
                            upinteid = rowa[7]
                            updirection = rowa[8]
                            uplane = rowa[9]
                            car.append(
                                [id, inteid, direction, lane, carplate, passtime, traveltime, upinteid, updirection,
                                 uplane])
                        datalist.append(car)
                    return datalist, detectiontimelist

            datalist, detectiontimelist = Get_daydate(originyear, originmonth, originday, intersectionid, ringdata)  # 按配时方案时间段分成的数据集

            print("当前路口数据按当天计划时间段分离完成 %s" % ctime())

            def sid_Get_daydate(datalist):  # 将datalist每个时间段内按sid分开
                f = []
                for row in datalist:
                    f.append(automakesidlist(row, picture_idtsclane))
                return f

            sid_datalist = sid_Get_daydate(datalist)
            print("当前路口数据按当天计划时间段按sid分离完成 %s" % ctime())

            def pointlistmaker(a, b, offset):  # a为指定列表 b为周期
                t = [[], []]
                for row in a:

                    x = (row[5].hour + row[5].minute / 60 + row[5].second / 3600)  # 横坐标
                    y = (row[5].hour * 3600 + row[5].minute * 60 + row[5].second) % b - offset
                    if y < 0:
                        y = y + b
                    t[0].append(x)
                    t[1].append(y)

                return t

            def autopointlistmaker(a, b, offset):  # a sidlanelist b 周期
                t = []
                for row in a:  # 每一个row都是一个列表
                    u = []
                    u = pointlistmaker(row, b, offset)
                    t.append(u)
                return t

            def sid_pointmaker(sid_datalist, ringdata):
                i = -1
                allsid_point = []
                for row in sid_datalist:
                    i = i + 1
                    period = 0
                    offset = ringdata[i][2]
                    for j in range(ringdata[i][4][0][0]):
                        period = period + ringdata[i][4][0][1][j][2] + ringdata[i][4][0][1][j][3]
                    if row:
                        sid_point = autopointlistmaker(row, period, offset)
                    allsid_point.append(sid_point)
                return allsid_point

            allsid_point = sid_pointmaker(sid_datalist, ringdata)

            # def picturemaker(a,e,f):#a sid编号 b周期 c d时间区间 e为点阵 f：点的颜色
            #     if a!=-999:      # plt.plot(pointlist[0][i][0],pointlist[0][i][1],color='red',marker='.')
            #         plt.scatter(e[a-1][0], e[a-1][1], s=0.2 * 10, c=f);
            #         # plt.xlabel('周期')
            #         # plt.ylabel('时间')
            #         # plt.xlim(0,24)
            #
            #
            # def autopicturemaker(a,b,c,d,e,f,g,h): #avcd 4路编号 e周期 f,g时间区间，h点阵
            #     plt.figure(figsize=(12, 6))
            #     picturemaker(a,h,"red")
            #     picturemaker(b,h,"b")
            #     picturemaker(c,h,"g")
            #     picturemaker(d,h,'y')
            #     plt.ylim(0, e)
            #     plt.xlim(f, g)
            #     plt.xticks(np.linspace(f, g, g - f + 1, endpoint=True))
            #     plt.yticks(np.linspace(0, e, e / 10 + 1, endpoint=True))
            #     #plt.savefig("examples.eps",dpi=300)
            #     #shutil.copy("F:\pythonwork\zhinengjiaotong\picture\examples.eps","F:\pythonwork\zhinengjiaotong\web")
            #     print(" 图片生成完成 %s" % ctime())
            #     plt.show()
            #
            # autopicturemaker(-999,2,-999,-999,130,19,22,allsid_point[7]) #红 蓝 绿 黄

            def detection(t):
                detectiondata = []
                #global conclusion1text
                for di in range(len(allsid_point)):
                    detactiondatamid = []
                    for dj in range(len(allsid_point[di])):
                        detactiondatamid.append([])
                    detectiondata.append(detactiondatamid)
                for i in range(len(allsid_point)):  # d第i个时间段
                    timelenthsteplist = []
                    for j in range(len(allsid_point[i])):  # 第几个sid
                        # timelenth=detectiontimelist[i][1].hour*60+detectiontimelist[i][1].minute-detectiontimelist[i][0].hour*60+detectiontimelist[i][0].minute
                        # timelenthstep=int(timelenth/t)
                        # timelenthsteplist.append(timelenthstep)
                        # step = 24 * 60 / t
                        # sid_datamistake=[]
                        # for t in range(timelenthstep):
                        #     if i==0:
                        #          if picture_makelist[j+t*len(allsid_point[i])]==1:
                        #             sid_datamistake.append(1)
                        #     else:
                        #         if picture_makelist[timelenthsteplist[i-1]*len(allsid_point[i])+j+t*len(allsid_point[i])]==1:
                        #             sid_datamistake.append(1)
                        dirction_lane = getlanesid(picture_idtsclane, j + 1)
                        # print(dirction_lane)
                        timelenth = (detectiontimelist[i][1].hour * 60 + detectiontimelist[i][1].minute) - (
                        detectiontimelist[i][0].hour * 60 + detectiontimelist[i][0].minute)
                        timelenthsecond = (
                                          detectiontimelist[i][1].hour * 3600 + detectiontimelist[i][1].minute * 60) - (
                                          detectiontimelist[i][0].hour * 3600 + detectiontimelist[i][0].minute * 60)
                        timelenthstep = int(timelenth / t)
                        sid_datamistake = []
                        for row in mistake_list:
                            if row[2] == dirction_lane[0] and row[3] == dirction_lane[1] and datetime.strptime(row[4],
                                                                                                               '%Y-%m-%d %H:%M:%S') >= \
                                    detectiontimelist[i][0] and datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S') <= \
                                    detectiontimelist[i][1]:
                                sid_datamistake.append(1)
                        if len(sid_datamistake) > math.ceil(timelenthstep / 2):
                            detectiondata[i][j] = -1  # 数据缺失异常
                            print('时间段%s-%s第%d路口数据缺失异常' % (ringdata[i][0], ringdata[i][1], j + 1))
                            conclusion1.append('时间段%s-%s第%d路口数据缺失异常\n' % (ringdata[i][0], ringdata[i][1], j + 1))
                            #conclusion1text=conclusion1text+'时间段%s-%s第%d路口数据缺失异常\n' % (ringdata[i][0], ringdata[i][1], j + 1)
                        else:  # 数据完整
                            period = 0
                            greentime = 0
                            yellotime = 0
                            selftime = 0
                            flag = 0
                            offset = ringdata[i][2]
                            for k in range(ringdata[i][4][0][0]):
                                period = period + ringdata[i][4][0][1][k][2] + ringdata[i][4][0][1][k][3]
                            for row in ringdata[i][4]:  # 有几个环
                                if flag == 0:

                                    for l in range(row[0]):  # 有几个相位
                                        flag1 = 0
                                        if flag == 0:
                                            for l1 in range(row[1][l][0]):  # 该相位有几个路口
                                                if row[1][l][1][l1] == j + 1:
                                                    selftime = row[1][l][2] + row[1][l][3]  # 找到对应路口则记录所包含的时间
                                                    flag = 1
                                            if flag == 0 and flag1 == 0:
                                                greentime = greentime + row[1][l][2]
                                                yellotime = yellotime + row[1][l][3]
                                                flag1 = 1
                                if flag == 0:
                                    greentime = 0
                                    yellotime = 0
                                    selftime = 0
                            greentimelist = []
                            redpointlist = []
                            for row in allsid_point[i][j][1]:
                                if row <= greentime + yellotime or row > greentime + yellotime + selftime:
                                    redpointlist.append(1)
                                    # if row>greentime+yellotime and row<=greentime+yellotime+selftime:
                                    #     greentimelist.append(1)
                            period_num = int(timelenthsecond / period)
                            redpointmeannum = len(redpointlist) / period_num
                            # print(len(allsid_point[i][j][1]),len(redpointlist),redpointlist,len(greentimelist),greentimelist)
                            if redpointmeannum >= 3 and dirction_lane[2] != 3:
                                detectiondata[i][j] = -2  # 红灯通行异常
                                print('时间段%s-%s第%d路口红灯通行异常,每个周期平均红灯过车%d辆' % (
                                ringdata[i][0], ringdata[i][1], j + 1, redpointmeannum))
                                conclusion1.append('时间段%s-%s第%d路口红灯通行异常,每个周期平均红灯过车%d辆\n' % (
                                ringdata[i][0], ringdata[i][1], j + 1, redpointmeannum))
                                # #conclusion1text=conclusion1text+'时间段%s-%s第%d路口红灯通行异常,每个周期平均红灯过车%d辆\n' % (
                                # ringdata[i][0], ringdata[i][1], j + 1, redpointmeannum)
                            else:
                                # print('时间段%s-%s第%d路口数据正常' % (ringdata[i][0], ringdata[i][1], j + 1))
                                step = int((selftime - 3) / 3)
                                starttime = selftime + greentime + yellotime - 3
                                flow = []
                                flow_normal = []
                                # flow2=[]
                                for p in range(step):
                                    num = []
                                    for row in allsid_point[i][j][1]:

                                        timestart = starttime - (p + 1) * 3
                                        timeend = starttime - p * 3
                                        # print(row)
                                        if row > timestart and row <= timeend:
                                            num.append(0)
                                    flow.append(len(num) * 3600 / (3 * period_num))
                                    flow_normal.append(len(num) * 3600 / (3 * period_num))

                                count = len(flow)
                                for fi in range(count):
                                    key = flow[fi]
                                    fj = fi - 1
                                    while fj >= 0:
                                        if flow[fj] > key:
                                            flow[fj + 1] = flow[fj]
                                            flow[fj] = key
                                        fj -= 1
                                # print(flow)
                                mean_flow = 0
                                for mi in range(3):
                                    mean_flow = mean_flow + flow[len(flow) - mi - 1]
                                mean_flow = mean_flow / 3
                                # print(mean_flow)

                                secondthreshold = 0.4 * mean_flow
                                greenflag = 0
                                if secondthreshold < 350:
                                    secondthreshold = 350
                                # print(flow_normal)
                                # print(mean_flow,secondthreshold,selftime-3)

                                for gi in range(len(flow_normal)):
                                    if flow_normal[gi] >= secondthreshold:
                                        break
                                    else:
                                        greenflag = greenflag + 1

                                # print(greenflag)
                                if greenflag == 0:
                                    detectiondata[i][j] = [0, selftime - 3, selftime - 3]  # 数据正常
                                    print('时间段%s-%s第%d路口绿灯时间正常' % (ringdata[i][0], ringdata[i][1], j + 1))
                                    conclusion1.append('时间段%s-%s第%d路口绿灯时间正常\n' % (ringdata[i][0], ringdata[i][1], j + 1))
                                    #conclusion1text=conclusion1text+'时间段%s-%s第%d路口绿灯时间正常\n' % (ringdata[i][0], ringdata[i][1], j + 1)
                                else:
                                    flag2 = 1
                                    ovremoregreentime = greenflag * 3
                                    newgreentime = selftime - 3 - ovremoregreentime
                                    if newgreentime < 10:
                                        newgreentime = 10
                                        flag2 = 0
                                    detectiondata[i][j] = [ovremoregreentime, selftime - 3, newgreentime]
                                    if flag2 == 1:
                                        print('时间段%s-%s第%d路口绿灯时间冗余%d秒,原时间为%d秒,调整为%d秒' % (
                                        ringdata[i][0], ringdata[i][1], j + 1, ovremoregreentime, selftime - 3,
                                        newgreentime))
                                        conclusion1.append('时间段%s-%s第%d路口绿灯时间冗余%d秒,原时间为%d秒,调整为%d秒\n' % (
                                        ringdata[i][0], ringdata[i][1], j + 1, ovremoregreentime, selftime - 3,
                                        newgreentime))
                                        # conclusion1text=conclusion1text+'时间段%s-%s第%d路口绿灯时间冗余%d秒,原时间为%d秒,调整为%d秒\n' % (
                                        # ringdata[i][0], ringdata[i][1], j + 1, ovremoregreentime, selftime - 3,
                                        # newgreentime)
                                    elif flag2 == 0:
                                        print('时间段%s-%s第%d路口绿灯时间冗余%d秒,原时间为%d秒,调整为最小绿灯时间%d秒' % (
                                        ringdata[i][0], ringdata[i][1], j + 1, ovremoregreentime, selftime - 3,
                                        newgreentime))
                                        conclusion1.append('时间段%s-%s第%d路口绿灯时间冗余%d秒,原时间为%d秒,调整为最小绿灯时间%d秒' % (
                                        ringdata[i][0], ringdata[i][1], j + 1, ovremoregreentime, selftime - 3,
                                        newgreentime)+'\n')
                                        # #conclusion1text=conclusion1text+'时间段%s-%s第%d路口绿灯时间冗余%d秒,原时间为%d秒,调整为最小绿灯时间%d秒\n' % (
                                        # ringdata[i][0], ringdata[i][1], j + 1, ovremoregreentime, selftime - 3,
                                        # newgreentime)
                return detectiondata

            detetiondata_temp = detection(time_lenth)
            def conclusion1save(a):
                path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
                f=open(path+'\static/text/detection.txt','wb')
                for row in a:
                    t=str.encode(row)
                    f.write(t)
                f.close()
            conclusion1save(conclusion1)
            def Get_Rold():
                R_old = []
                for di in range(len(ringdata)):
                    R_oldmid = []
                    for dj in range(ringdata[di][3]):
                        R_oldmid.append([])
                    R_old.append(R_oldmid)
                for i in range(len(ringdata)):
                    for j in range(ringdata[i][3]):
                        R_oldmid1 = []
                        for R_num in range(ringdata[i][4][j][0]):
                            greentime = ringdata[i][4][j][1][R_num][2]
                            R_oldmid1.append(greentime)
                        R_old[i][j] = R_oldmid1
                return R_old

            R_old = Get_Rold()

            def Get_Rtemp(detetiondata_temp):
                table_data = []
                for di in range(len(detetiondata_temp)):
                    detactiondatamid = []
                    for dj in range(ringdata[di][3]):
                        detactiondatamid.append([])
                    table_data.append(detactiondatamid)
                for i in range(len(detetiondata_temp)):
                    for table_num in range(ringdata[i][3]):
                        ring_data = []
                        for R_num in range(ringdata[i][4][table_num][0]):
                            R_data = []
                            for lane_num in range(ringdata[i][4][table_num][1][R_num][0]):
                                lane_name = ringdata[i][4][table_num][1][R_num][1][lane_num]
                                datatemp = detetiondata_temp[i][lane_name - 1]
                                R_data.append(datatemp)
                            # print(R_data)
                            green_data = []
                            for row in R_data:
                                if row != -1 and row != -2:
                                    green_data.append(row[2])
                            if green_data:
                                max_time = max(green_data)
                            else:
                                max_time = -1
                            ring_data.append(max_time)
                        table_data[i][table_num] = ring_data
                        # print(ring_data)
                return table_data

            R_temp = Get_Rtemp(detetiondata_temp)

            def flagmake(a):
                if a > 0:
                    return 1
                elif a < 0:
                    return -1
                elif a == 0:
                    return 0

            def myround(n1, n2):

                if isinstance(n1, float) and isinstance(n2, float):
                    if n1 % 1 == 0.5:
                        n2 = int(n2 + 0.5)
                        n1 = round(n1)
                        return n1, n2
                    else:
                        n1 = round(n1)
                        n2 = round(n2)
                        return n1, n2

                else:
                    return n1, n2

            # print(R_temp)
            def Get_Rnew(R_temp):
                Rnew = []
                for di in range(len(R_temp)):
                    Rnewmid = []
                    for dj in range(len(R_temp[di])):
                        Rnewmid.append([])
                    Rnew.append(Rnewmid)

                for i in range(len(R_temp)):
                    data = R_temp[i]
                    mistake = []
                    if data[0][0] != -1:
                        r11t = data[0][0]
                    else:
                        mistake.append(-1)
                    if data[0][1] != -1:
                        r12t = data[0][1]
                    else:
                        mistake.append(-2)
                    if data[0][2] != -1:
                        r13t = data[0][2]
                    else:
                        mistake.append(-3)
                    if data[0][3] != -1:
                        r14t = data[0][3]
                    else:
                        mistake.append(-4)
                    if data[1][0] != -1:
                        r21t = data[1][0]
                    else:
                        mistake.append(-5)
                    if data[1][1] != -1:
                        r22t = data[1][1]
                    else:
                        mistake.append(-6)
                    if data[1][2] != -1:
                        r23t = data[1][2]
                    else:
                        mistake.append(-7)
                    if data[1][3] != -1:
                        r24t = data[1][3]
                    else:
                        mistake.append(-8)
                    for j in range(len(R_temp[i])):
                        if mistake:
                            Rnew[i][j] = mistake
                        else:
                            if r11t + r12t >= r21t + r22t:
                                b1n = r11t + r12t
                                r11n = r11t
                                r12n = r12t
                                r21n = r21t * b1n / (r21t + r22t)
                                r22n = r22t * b1n / (r21t + r22t)
                            else:
                                b1n = r21t + r22t
                                r11n = r11t * b1n / (r11t + r12t)
                                r12n = r12t * b1n / (r11t + r12t)
                                r21n = r21t
                                r22n = r22t
                            if r13t + r14t >= r23t + r24t:
                                b2n = r13t + r14t
                                r13n = r13t
                                r14n = r14t
                                r23n = r23t * b2n / (r23t + r24t)
                                r24n = r24t * b2n / (r23t + r24t)
                            else:
                                b2n = r23t + r24t
                                r13n = r13t * b2n / (r13t + r14t)
                                r14n = r14t * b2n / (r13t + r14t)
                                r23n = r23t
                                r24n = r24t
                            r11n, r12n = myround(r11n, r12n)
                            r13n, r14n = myround(r13n, r14n)
                            r21n, r22n = myround(r21n, r22n)
                            r23n, r24n = myround(r23n, r24n)
                            Rnew[i][0] = [r11n, r12n, r13n, r14n]
                            Rnew[i][1] = [r21n, r22n, r23n, r24n]
                            # Rnew[i][0]=[round(r11n),round(r12n),round(r13n),round(r14n)]
                            # Rnew[i][1]=[round(r21n),round(r22n),round(r23n),round(r24n)]
                            # print(r11n,r12n,r13n,r14n)
                            # print(r21n,r22n,r23n,r24n)
                return Rnew

            R_new = Get_Rnew(R_temp)

            def R_nameget(a, b):
                d = '西'
                m = '左'
                if a == 0:
                    d = '北'
                elif a == 2:
                    d = '东'
                elif a == 4:
                    d = '南'
                elif a == 6:
                    d = '西'
                if b == 1:
                    m = '右'
                elif b == 2:
                    m = '直'
                elif b == 3:
                    m = '左'
                elif b == 4:
                    m = '直-右'
                elif b == 5:
                    m = '直-左-右'
                elif b == 6:
                    m = '直-左'
                elif b == 7:
                    m = '左-掉头'
                elif b == 8:
                    m = '右-左'
                elif b == 9:
                    m = '掉头'
                return d + m

            def plancheck(R_new, R_temp, R_old):
                for i in range(len(R_new)):
                    if R_new[i][0][0] < 0:
                        print('时间段%s-%s相位数据缺失异常，无法进行分析' % (ringdata[i][0], ringdata[i][1]))
                        conclusion2.append('时间段%s-%s相位数据缺失异常，无法进行分析\n' % (ringdata[i][0], ringdata[i][1]))
                        for mistake_num in range(len(R_new[i][0])):
                            mistake_R = 0 - R_new[i][0][mistake_num]
                            table_num = int(math.ceil(mistake_R / 4))
                            R_num = int(mistake_R - (table_num - 1) * 4)
                            lane_list = ringdata[i][4][table_num - 1][1][R_num - 1][1]
                            dirction_lane = getlanesid(picture_idtsclane, lane_list[0])
                            R_name = R_nameget(dirction_lane[0], dirction_lane[2])
                            print('其中第%d环第%d相位%s数据,车道%s完全缺失' % (table_num, R_num, R_name, lane_list))
                            conclusion2.append('其中第%d环第%d相位%s数据,车道%s完全缺失\n' % (table_num, R_num, R_name, lane_list))
                    else:
                        Cnew1 = 0
                        Cnew2 = 0
                        for row in R_new[i][0]:
                            Cnew1 = Cnew1 + row + 3
                        for row in R_new[i][1]:
                            Cnew2 = Cnew2 + row + 3
                        if Cnew1 != Cnew2:
                            print('时间段%s-%s新方案两环周期不等' % (ringdata[i][0], ringdata[i][1]))
                            conclusion2.append('时间段%s-%s新方案两环周期不等\n' % (ringdata[i][0], ringdata[i][1]))
                        else:
                            Cnew = Cnew1
                            Cold = 0
                            for row in R_old[i][0]:
                                Cold = Cold + row + 3
                            # print(Cnew1,Cold)
                            flag_C = Cnew - Cold
                            if flag_C == 0:
                                print('时间段%s-%s方案周期合理' % (ringdata[i][0], ringdata[i][1]))
                                conclusion2.append('时间段%s-%s方案周期合理\n' % (ringdata[i][0], ringdata[i][1]))
                            elif flag_C < 0:
                                print('时间段%s-%s方案周期过大，应减少%d秒' % (ringdata[i][0], ringdata[i][1], 0 - flag_C))
                                conclusion2.append(
                                    '时间段%s-%s方案周期过大，应减少%d秒\n' % (ringdata[i][0], ringdata[i][1], 0 - flag_C))
                            flag_P1 = [flagmake(R_old[i][0][0] - R_old[i][1][0]),
                                       flagmake(R_new[i][0][0] - R_new[i][1][0])]
                            flag_P2 = [flagmake(R_old[i][0][2] - R_old[i][1][2]),
                                       flagmake(R_new[i][0][2] - R_new[i][1][2])]
                            flag_P1mid = 0
                            flag_P2mid = 0
                            if flag_P1 == [-1, -1] or flag_P1 == [0, 0] or flag_P1 == [1, 1]:
                                flag_P1mid = 1
                            if flag_P2 == [-1, -1] or flag_P2 == [0, 0] or flag_P2 == [1, 1]:
                                flag_P2mid = 1
                            if flag_P1mid == 1 and flag_P2mid == 1:
                                print('时间段%s-%s相位序列合理，对相位序列无建议' % (ringdata[i][0], ringdata[i][1]))
                                conclusion2.append('时间段%s-%s相位序列合理，对相位序列无建议\n' % (ringdata[i][0], ringdata[i][1]))
                            else:
                                if flag_P1 == [-1, 0]:
                                    print(
                                        '时间段%s-%s不需要搭接相位[R12,R21]，应取消搭接相位[R12,R21]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s不需要搭接相位[R12,R21]，应取消搭接相位[R12,R21]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P1 == [1, 0]:
                                    print(
                                        '时间段%s-%s不需要搭接相位[R11,R22]，应取消搭接相位[R11,R22]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s不需要搭接相位[R11,R22]，应取消搭接相位[R11,R22]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P1 == [0, -1]:
                                    print('时间段%s-%s需要搭接相位[R12,R21]，应增加接相位[R12,R21]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append(
                                        '时间段%s-%s需要搭接相位[R12,R21]，应增加接相位[R12,R21]\n' % (ringdata[i][0], ringdata[i][1]))
                                elif flag_P1 == [0, 1]:
                                    print('时间段%s-%s需要搭接相位[R11,R22]，应增加搭接相位[R11,R22]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append(
                                        '时间段%s-%s需要搭接相位[R11,R22]，应增加搭接相位[R11,R22]\n' % (ringdata[i][0], ringdata[i][1]))
                                elif flag_P1 == [-1, 1]:
                                    print('时间段%s-%s搭接相位[R12,R21]不合理，应将搭接相位[R12,R21]替换为[R11,R22]' % (
                                        ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s搭接相位[R12,R21]不合理，应将搭接相位[R12,R21]替换为[R11,R22]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P1 == [1, -1]:
                                    print('时间段%s-%s搭接相位[R11,R22]不合理，应将搭接相位[R11,R22]替换为[R12,R21]' % (
                                        ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s搭接相位[R11,R22]不合理，应将搭接相位[R11,R22]替换为[R12,R21]\n' % (
                                        ringdata[i][0], ringdata[i][1]))

                                if flag_P2 == [-1, 0]:
                                    print(
                                        '时间段%s-%s不需要搭接相位[R14,R23]，应取消搭接相位[R14,R23]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s不需要搭接相位[R14,R23]，应取消搭接相位[R14,R23]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P2 == [1, 0]:
                                    print(
                                        '时间段%s-%s不需要搭接相位[R13,R24]，应取消搭接相位[R13,R24]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s不需要搭接相位[R13,R24]，应取消搭接相位[R13,R24]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P2 == [0, -1]:
                                    print('时间段%s-%s需要搭接相位[R14,R23]，应增加搭接相位[R14,R23]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s不需要搭接相位[R13,R24]，应取消搭接相位[R13,R24]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P2 == [0, 1]:
                                    print('时间段%s-%s需要搭接相位[R13,R24]，应增加搭接相位[R13,R24]' % (ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append(
                                        '时间段%s-%s需要搭接相位[R13,R24]，应增加搭接相位[R13,R24]\n' % (ringdata[i][0], ringdata[i][1]))
                                elif flag_P2 == [-1, 1]:
                                    print('时间段%s-%s搭接相位[R14,R23]不合理，应将搭接相位[R14,R23]替换为[R13,R24]' % (
                                        ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s搭接相位[R14,R23]不合理，应将搭接相位[R14,R23]替换为[R13,R24]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                                elif flag_P2 == [1, -1]:
                                    print('时间段%s-%s搭接相位[R13,R24]不合理，应将搭接相位[R13,R24]替换为[R14,R23]' % (
                                        ringdata[i][0], ringdata[i][1]))
                                    conclusion2.append('时间段%s-%s搭接相位[R13,R24]不合理，应将搭接相位[R13,R24]替换为[R14,R23]\n' % (
                                        ringdata[i][0], ringdata[i][1]))
                            flag_R11 = [flagmake(R_new[i][0][0] - R_temp[i][0][0]),
                                        flagmake(R_new[i][0][0] - R_old[i][0][0]),
                                        flagmake(R_temp[i][0][0] - R_old[i][0][0])]
                            # print(R_new[i][0][0],R_temp[i][0][0],R_old[i][0][0])
                            flag_R12 = [flagmake(R_new[i][0][1] - R_temp[i][0][1]),
                                        flagmake(R_new[i][0][1] - R_old[i][0][1]),
                                        flagmake(R_temp[i][0][1] - R_old[i][0][1])]

                            flag_R13 = [flagmake(R_new[i][0][2] - R_temp[i][0][2]),
                                        flagmake(R_new[i][0][2] - R_old[i][0][2]),
                                        flagmake(R_temp[i][0][2] - R_old[i][0][2])]

                            flag_R14 = [flagmake(R_new[i][0][3] - R_temp[i][0][3]),
                                        flagmake(R_new[i][0][3] - R_old[i][0][3]),
                                        flagmake(R_temp[i][0][3] - R_old[i][0][3])]

                            flag_R21 = [flagmake(R_new[i][1][0] - R_temp[i][1][0]),
                                        flagmake(R_new[i][1][0] - R_old[i][1][0]),
                                        flagmake(R_temp[i][1][0] - R_old[i][1][0])]

                            flag_R22 = [flagmake(R_new[i][1][1] - R_temp[i][1][1]),
                                        flagmake(R_new[i][1][1] - R_old[i][1][1]),
                                        flagmake(R_temp[i][1][1] - R_old[i][1][1])]

                            flag_R23 = [flagmake(R_new[i][1][2] - R_temp[i][1][2]),
                                        flagmake(R_new[i][1][2] - R_old[i][1][2]),
                                        flagmake(R_temp[i][1][2] - R_old[i][1][2])]

                            flag_R24 = [flagmake(R_new[i][1][3] - R_temp[i][1][3]),
                                        flagmake(R_new[i][1][3] - R_old[i][1][3]),
                                        flagmake(R_temp[i][1][3] - R_old[i][1][3])]
                            flag_R = [flag_R11, flag_R12, flag_R13, flag_R14, flag_R21, flag_R22, flag_R23, flag_R24]
                            for p in range(len(flag_R)):

                                table_num = int(math.ceil((p + 1) / 4))
                                R_num = int((p + 1) - (table_num - 1) * 4)
                                dirction_lane = getlanesid(picture_idtsclane,
                                                           ringdata[i][4][table_num - 1][1][R_num - 1][1][0])
                                # print(dirction_lane[0],dirction_lane[2])
                                R_name = R_nameget(dirction_lane[0], dirction_lane[2])
                                if flag_R[p][0] == 0:
                                    if flag_R[p][1] == 0:
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间合理' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name))
                                        conclusion2.append('时间段%s-%s第%d环第%d相位%s绿灯时间合理\n' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name))
                                    elif flag_R[p][1] == -1:
                                        t = abs(R_new[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t))
                                        conclusion2.append('时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒\n' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t))
                                    elif flag_R[p][1] == 1:
                                        t = abs(R_new[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间不足，应该减少%d秒' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t))
                                        conclusion2.append('时间段%s-%s第%d环第%d相位%s绿灯时间不足，应该减少%d秒\n' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t))
                                elif flag_R[p][0] == 1:
                                    if flag_R[p][1] == -1 and flag_R[p][2] == -1:
                                        t = abs(
                                            R_temp[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        t1 = abs(
                                            R_new[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒,但因相位序列约束，只能减少%d秒，该相位的绿灯时间依然有一定浪费' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t, t1))
                                        conclusion2.append(
                                            '时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒,但因相位序列约束，只能减少%d秒，该相位的绿灯时间依然有一定浪费\n' % (
                                                ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t, t1))
                                    elif flag_R[p][1] == 0 and flag_R[p][2] == -1:
                                        t = abs(
                                            R_temp[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒,但因相位序列约束，绿灯时间不能改变，该相位的绿灯时间依然浪费' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t))
                                        conclusion2.append(
                                            '时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒,但因相位序列约束，绿灯时间不能改变，该相位的绿灯时间依然浪费\n' % (
                                                ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t))
                                    elif flag_R[p][1] == 1 and flag_R[p][2] == -1:
                                        t = abs(
                                            R_temp[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        t1 = abs(
                                            R_new[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒,但因相位序列约束，必须增加%d秒，该相位的绿灯时间依然浪费' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t, t1))
                                        conclusion2.append(
                                            '时间段%s-%s第%d环第%d相位%s绿灯时间浪费，应该减少%d秒,但因相位序列约束，必须增加%d秒，该相位的绿灯时间依然浪费\n' % (
                                                ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t, t1))
                                    elif flag_R[p][1] == 1 and flag_R[p][2] == 0:
                                        t1 = abs(
                                            R_new[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间合理,绿灯时间不应改变，但因相位序列约束，必须增加%d秒，该相位的绿灯时间会浪费' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t1))
                                        conclusion2.append(
                                            '时间段%s-%s第%d环第%d相位%s绿灯时间合理,绿灯时间不应改变，但因相位序列约束，必须增加%d秒，该相位的绿灯时间会浪费\n' % (
                                                ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t1))
                                    elif flag_R[p][1] == 1 and flag_R[p][2] == 1:
                                        t = abs(
                                            R_temp[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        t1 = abs(
                                            R_new[i][table_num - 1][R_num - 1] - R_old[i][table_num - 1][R_num - 1])
                                        print('时间段%s-%s第%d环第%d相位%s绿灯时间不足,应该增加%d秒，但因相位序列约束，应该增加%d秒，该相位的绿灯时间依然有一定浪费' % (
                                            ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t, t1))
                                        conclusion2.append(
                                            '时间段%s-%s第%d环第%d相位%s绿灯时间不足,应该增加%d秒，但因相位序列约束，应该增加%d秒，该相位的绿灯时间依然有一定浪费\n' % (
                                                ringdata[i][0], ringdata[i][1], table_num, R_num, R_name, t, t1))

                                        # pointpath123 = [(0, 0), (1, 1), (3, 3)]
                                        # pointcodes123 = [Path.MOVETO, Path.LINETO, Path.LINETO]
                                        # pathmaker(pointpath123, pointcodes123, 'black', 'black')
                                        # plt.savefig('fuck', dpi=100)

            def planpicturemaker(R_new):
                for i in range(len(R_new)):
                    fig1 = plt.figure()
                    fig1.set_figheight(1.8)
                    fig1.set_figwidth(5)
                    ax1 = fig1.add_subplot(111)
                    ax1.set_xlim(0, 2)
                    ax1.set_ylim(0, 1)
                    ax1.set_xticks([])
                    ax1.set_yticks([])
                    if R_new[i][0][0] < 0:

                        plt.text(1, 0.5, '数据缺失无法分析', horizontalalignment='center', va='center', fontsize=10)
                        name = 'planchek%d' % (i + 1) + '_' + str(ran)
                        # name = name + '.jpg'
                        # plt.savefig(name, dpi=100)
                        ax1.set_title('时间段%s-%s' % (ringdata[i][0], ringdata[i][1]), fontsize=12)
                        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
                        plt.savefig(path + "\static\images\_detection/" + name + '.jpg',
                                    dpi=500)
                        # plt.close()
                    else:
                        pointpath1 = []
                        pointcodes1 = []
                        pointpath2 = []
                        pointcodes2 = []
                        long = 0
                        yellowred = 3
                        offset = 0.55
                        long1 = 0
                        offset1 = 0.1
                        lenth = 60.000

                        # print(len(R_new[i][0])/2)

                        for j in range(len(R_new[i][0])):
                            pointpath = [(long / lenth, offset), (long / lenth, 0.2 + offset),
                                         ((R_new[i][0][j] + long) / lenth, 0.2 + offset),
                                         ((R_new[i][0][j] + long) / lenth, 0 + offset), (long / lenth, 0 + offset)]
                            dirction_lane = getlanesid(picture_idtsclane, ringdata[i][4][0][1][j][1][0])
                            # print(dirction_lane[0],dirction_lane[2])
                            R_name = R_nameget(dirction_lane[0], dirction_lane[2])
                            Rname = 'R1' + "_" + '%d' % (j + 1) + ":" + '%d' % (R_new[i][0][j]) + "秒"
                            Rname = R_name + ":" + '%d' % (R_new[i][0][j])
                            plt.text(long / lenth, 0.3 + offset, Rname, horizontalalignment='left', va='center',
                                     fontsize=6)
                            long = long + R_new[i][0][j]
                            pointcodes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]

                            path1 = Path(pointpath, pointcodes)
                            patch1 = patches.PathPatch(path1, facecolor='chartreuse', alpha=1, edgecolor='black')
                            ax1.add_patch(patch1)

                            pointpath2 = [(long / lenth, 0 + offset), (long / lenth, 0.2 + offset),
                                          ((long + yellowred) / lenth, 0.2 + offset),
                                          ((long + yellowred) / lenth, 0 + offset), (long / lenth, 0 + offset)]

                            pointcodes2 = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
                            path2 = Path(pointpath2, pointcodes2)
                            patch2 = patches.PathPatch(path2, facecolor='yellow', alpha=1, edgecolor='black')
                            ax1.add_patch(patch2)
                            long = long + yellowred

                        for j in range(len(R_new[i][1])):
                            pointpath = [(long1 / lenth, 0 + offset1), (long1 / lenth, 0.2 + offset1),
                                         ((R_new[i][1][j] + long1) / lenth, 0.2 + offset1),
                                         ((R_new[i][1][j] + long1) / lenth, 0 + offset1), (long1 / lenth, 0 + offset1)]
                            dirction_lane = getlanesid(picture_idtsclane, ringdata[i][4][1][1][j][1][0])
                            # print(dirction_lane[0],dirction_lane[2])
                            R_name = R_nameget(dirction_lane[0], dirction_lane[2])
                            Rname = 'R2' + "_" + '%d' % (j + 1) + ":" + '%d' % (R_new[i][1][j]) + "秒"
                            Rname = R_name + ":" + '%d' % (R_new[i][1][j])
                            plt.text(long1 / lenth, 0.3 + offset1, Rname, horizontalalignment='left', va='center',
                                     fontsize=6)
                            long1 = long1 + R_new[i][1][j]
                            pointcodes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
                            # pointpath123=[(0,0),(1,1),(3,3)]
                            # pointcodes123=[Path.MOVETO,Path.LINETO,Path.LINETO]
                            path1 = Path(pointpath, pointcodes)
                            patch1 = patches.PathPatch(path1, facecolor='chartreuse', alpha=1, edgecolor='black')
                            ax1.add_patch(patch1)

                            pointpath2 = [(long1 / lenth, 0 + offset1), (long1 / lenth, 0.2 + offset1),
                                          ((long1 + yellowred) / lenth, 0.2 + offset1),
                                          ((long1 + yellowred) / lenth, 0 + offset1), (long1 / lenth, 0 + offset1)]

                            pointcodes2 = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
                            path2 = Path(pointpath2, pointcodes2)
                            patch2 = patches.PathPatch(path2, facecolor='yellow', alpha=1, edgecolor='black')
                            ax1.add_patch(patch2)
                            long1 = long1 + yellowred

                            # pathmaker(pointpath123,pointcodes123, 'black','black')
                        # plt.text(2, 1, 'what', horizontalalignment='center', va='center')
                        ax1.set_title('时间段%s-%s' % (ringdata[i][0], ringdata[i][1]), fontsize=12)
                        name = 'planchek%d' % (i + 1) + '_' + str(ran)
                        # name = name
                        # plt.savefig(name, dpi=100)
                        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
                        plt.savefig(path + "\static\images\_detection/" + name + '.jpg',
                                    dpi=500)
                        # plt.show()
                        # plt.close()

            plancheck(R_new, R_temp, R_old)

            planpicturemaker(R_new)

            def conclusion2save(a):
                path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\chart'
                f = open(path + '\static/text/detection_c.txt', 'wb')
                for row in a:
                    t = str.encode(row)
                    f.write(t)
                f.close()

            conclusion2save(conclusion2)
            # return render(resquest,'flowchart.html',{context})
    else:

        datapicture_form = datacheckForm();
        context['datapicture_form'] = datapicture_form;
    # f1=open('F:\pythonwork\jiaotongweb\chart\static/text/detection.txt','r')
    # text1=f1.read()
    # f1.close()
    # print(text1)
    t1='车道监测结果：\n'
    #print(type(t1))
    for row in conclusion1:
        #print(type(row))
        t1=t1+str(row)
    t2='相位评价及优化：\n'
    for row in conclusion2:
        #print(type(row))
        t2=t2+str(row)

    context['conclusion1'] = t1
    context['conclusion2'] = t2
    context['netpicture1'] = '\static\images\_detection/' + 'planchek1_'+str(ran) + '.jpg'
    context['netpicture2'] = '\static\images\_detection/' + 'planchek2_' + str(ran) + '.jpg'
    context['netpicture3'] = '\static\images\_detection/' + 'planchek3_' + str(ran) + '.jpg'
    context['netpicture4'] = '\static\images\_detection/' + 'planchek4_' + str(ran) + '.jpg'
    context['netpicture5'] = '\static\images\_detection/' + 'planchek5_' + str(ran) + '.jpg'
    context['netpicture6'] = '\static\images\_detection/' + 'planchek6_' + str(ran) + '.jpg'
    context['netpicture7'] = '\static\images\_detection/' + 'planchek7_' + str(ran) + '.jpg'
    context['netpicture8'] = '\static\images\_detection/' + 'planchek8_' + str(ran) + '.jpg'

    return render(resquest, 'detection.html', context)