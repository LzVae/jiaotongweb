# 交通大数据网站

## 1.数据监测

![数据监测结果](D:\jiaotongweb\readme\数据监测结果.jpg)



纵坐标代表时间，横坐标代表路口点，有颜色代表该时间段内有车辆通过，白色则代表没有

---



## 2.交叉口双时域图分析

![交叉口双时域图分析结果](D:\jiaotongweb\readme\交叉口双时域图分析结果.jpg)

横坐标代表时间，纵坐标代表在它所在周期里的位置，就是绝对时间除以周期的余数

---



## 3.交叉口流量分析

![交叉口流量分析结果](D:\jiaotongweb\readme\交叉口流量分析结果.jpg)

扇形边缘的黑色代表进入的流量，灰色代表出去的流量，扇形颜色代表流量的方向

```properties
绿色 : 由北面进入的流量
粉色 : 由南面进入的流量
蓝色 : 由西面进入的流量
橙色 : 由东面进入的流量
```

扇形的角度大小代表了流量的相对大小

---



编写sql语句查看到底有多少条数据

```mysql
select count(*) as 'table1',
		count(*) as 'table2',
		count(*) as 'table3',
			from 2017524_2013525_58_10,
					2017524_2014525_58_10,
					2017524_2017225_58_10
						order by count(*);
	   
```

