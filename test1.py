import streamlit as st
from streamlit_echarts import st_pyecharts
import pandas as pd
import numpy as np
import datetime
from pyecharts import options as opts
from pyecharts.charts import Pie,Page,Calendar,Bar,Line
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from lxml import etree
import csv

st.set_page_config(layout="wide",page_title="数据平台")

sidebar = st.sidebar.radio(
    "功能选择",
    ("查看历史数据", "自主上传文件")
)

@st.cache
def spider():
    def getWeather(url):
        weather_info = []
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
        }
        resp = requests.get(url,headers = headers)
        resp_html = etree.HTML(resp.text)
        resp_list = resp_html.xpath("//ul[@class='thrui']/li")

        for li in resp_list:
            day_weather_info = {}
            day_weather_info['date_time'] = li.xpath('./div[1]/text()')[0].split(' ')[0]
            high = li.xpath("./div[2]/text()")[0]
            day_weather_info['high'] = high[:high.find('℃')]
            low = li.xpath("./div[3]/text()")[0]
            day_weather_info['low'] = low[:low.find('℃')]
            day_weather_info['weather'] = li.xpath("./div[4]/text()")[0]
            day_weather_info['wind'] = li.xpath('./div[5]/text()')[0].split(' ')[1]
            weather_info.append(day_weather_info)
        return weather_info

    weathers = []
    for year in range(2017,2022):
        for month in range(1,13):
            if month < 10:
                weather_time = str(year) + ('0'+str(month))
            else:
                weather_time = str(year) + str(month)
            url = f'http://lishi.tianqi.com/shanghai/{weather_time}.html'
            weather = getWeather(url)
            weathers.append(weather)

    with open('wea111.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date','HighTem','LowTem','Weather','Wind'])
        list_year = []
        for month_weather in weathers:
            for day_weather_dict in month_weather:
                list_year.append(list(day_weather_dict.values()))
        writer.writerows(list_year)
spider()

if sidebar == "查看历史数据":

    st.title("查看历史数据")
    year = st.selectbox(
        "请选择年份",
        ('2021', '2020', '2019','2018','2017')
    )

    data = pd.read_csv('D:\\python_work\\shanghai-air-quality.csv',encoding='gb18030')
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').sort_index(ascending=True)
    data = data['2017-01-01':'2021-12-31']
    data = data.replace(' ',np.NaN)
    data = data.fillna(method='pad')
    data.to_csv('count1.csv')
    data = pd.read_csv('D:\\python_work\\count1.csv')
    def calculate(pm25):
        if pm25<=35:
            aqi = 50/35*pm25
        elif pm25>35 and pm25<=75:
            aqi = 50/40*(pm25-35)+50
        elif pm25>75 and pm25<=115:
            aqi = 50/30*(pm25-75)+100
        elif pm25>115 and pm25<=150:
            aqi = 50/35*(pm25-115)+150
        else:
            aqi = pm25+50
        return aqi
    aqi1 = round(data['pm25'].apply(calculate))
    def calculate(pm10):
        if pm10<=50:
            aqi = pm10
        elif pm10>50 and pm10<=350:
            aqi = 0.5*pm10+25
        elif pm10>350 and pm10<=420:
            aqi = 100/70*(pm10-350)+200
        else:
            aqi = 100/80*(pm10-420)+300
        return aqi
    aqi2 = round(data['pm10'].apply(calculate))
    def calculate(co):
        if co<=4:
            aqi = 25*co
        elif co>4 and co<=14:
            aqi = 5*co+80
        else:
            aqi = 5*co+80
        return aqi
    aqi3 = round(data['co'].apply(calculate))
    def calculate(no2):
        if no2<=80:
            aqi = 50/40*no2
        elif no2>80 and no2<=180:
            aqi = 0.5*no2+60
        return aqi
    aqi4 = round(data['no2'].apply(calculate))
    def calculate(so2):
        if so2<=50:
            aqi = so2
        elif so2>50 and so2<=150:
            aqi = 0.5*so2+25
        return aqi
    aqi5 = round(data['so2'].apply(calculate))
    def calculate(o3):
        if o3<=100:
            aqi = 0.5*o3
        else:
            aqi = 50/60*(o3-100)+50
        return aqi
    aqi6 = round(data['o3'].apply(calculate))
    aqi_1 = aqi1.values.flatten().tolist()
    aqi_2 = aqi2.values.flatten().tolist()
    aqi_3 = aqi3.values.flatten().tolist()
    aqi_4 = aqi4.values.flatten().tolist()
    aqi_5 = aqi5.values.flatten().tolist()
    aqi_6 = aqi6.values.flatten().tolist()
    aqi = [max(aqi_1[i], aqi_2[i], aqi_3[i], aqi_4[i], aqi_5[i], aqi_6[i]) for i in range(len(aqi_1))]
    data['AQI'] = aqi
    data['AQI'] = data['AQI'].apply(lambda x : int(x))
    def value_to_level(AQI):
        if AQI>=0 and AQI<=50:
            return '优'
        elif AQI>=51 and AQI<=100:
            return '良'
        elif AQI>=101 and AQI<=150:
            return '轻度污染'
        elif AQI>=151 and AQI<=200:
            return '中度污染'
        elif AQI>=201 and AQI<=300:
            return '重度污染'
        else:
            return '严重污染'
    level = data['AQI'].apply(value_to_level)
    data['level'] = level
    data.to_csv('calculate.csv',index=False)

    dz = pd.read_csv('wea111.csv',encoding='gb18030')
    dz['Wind'] = dz['Wind'].replace(['微风'],'1级')
    dz['Wind'] = dz['Wind'].str.extract('(\d+)')
    dz['Weather'] = dz['Weather'].replace(['小雨','小雨到中雨','小雨到大雨','阴转小雨','小雨转阴','中雨',
                                                '阴到小雨','晴转小雨','大雨','阵雨','雷阵雨','多云转雨','小雨到中雨转雨',
                                                '阴转雨','小雨转雨','中雨转雨','晴转雨','大雨转雨','小雨到暴雨','暴雨转雨',
                                                '多云转小雨','中雨到大雨','风转小雨'],'雨')
    dy = pd.read_csv('calculate.csv')
    dy['date'] = dy['date']
    dy['pm10'] = dy['pm10']
    dy['pm25'] = dy['pm25']
    dy['o3'] = dy['o3']
    dy['no2'] = dy['no2']
    dy['co'] = dy['co']
    dy['so2'] = dy['so2']
    dy['AQI'] = dy['AQI']
    dy['level'] = dy['level']
    dy['HighTem'] = dz['HighTem']
    dy['LowTem'] = dz['LowTem']
    dy['Weather'] = dz['Weather']
    dy['Wind'] = dz['Wind']
    dy.to_csv('fin.csv',index=False)


    data = pd.read_csv('D:\\python_work\\fin.csv')
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').sort_index(ascending=True)

    if year == "2021":    
        data = data['2021-01-01':'2021-12-31']
        def calendar():
            global data
            data = data.reset_index()
            date = pd.to_datetime(data['date']).tolist()
            aqi = data['AQI'].values.tolist()
            cal = Calendar()
            cal.add("",[z for z in zip(date,aqi)],
                calendar_opts=opts.CalendarOpts(
                    pos_top="100",pos_left="30",pos_right="30",pos_bottom='80',range_="2021",
                    daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn")),
            )
            cal.set_global_opts(
                title_opts=opts.TitleOpts(pos_top="25", pos_left="center", title="空气质量日历",title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                visualmap_opts=opts.VisualMapOpts(
                    max_=500, min_=0, orient="horizontal", is_piecewise=True,pos_top="350",pos_left="center",
                    pieces=[{"min":0,"max":50,"label":'优','color':'#008000'},
                            {"min":50,"max":100,"label":'良','color':'#FFFF00'},
                            {"min":100,"max":150,"label":'轻度污染','color':'#FFA500'},
                            {"min":150,"max":200,"label":'中度污染','color':'#FF0000'},
                            {"min":200,"max":300,"label":'重度污染','color':'#9932CC'},
                            {"min":300,"max":500,"label":'严重污染','color':'#800080'},],),
            )                       
            st_pyecharts(cal,width='800px', height='400px')
        calendar()
    elif year == "2020":
        data = data['2020-01-01':'2020-12-31']
        def calendar():
            global data
            data = data.reset_index()
            date = pd.to_datetime(data['date']).tolist()
            aqi = data['AQI'].values.tolist()
            cal = Calendar()
            cal.add("",[z for z in zip(date,aqi)],
                calendar_opts=opts.CalendarOpts(
                    pos_top="100",pos_left="30",pos_right="30",pos_bottom='80',range_="2020",
                    daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn")),
            )
            cal.set_global_opts(
                title_opts=opts.TitleOpts(pos_top="25", pos_left="center", title="空气质量日历",title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                visualmap_opts=opts.VisualMapOpts(
                    max_=500, min_=0, orient="horizontal", is_piecewise=True,pos_top="350",pos_left="center",
                    pieces=[{"min":0,"max":50,"label":'优','color':'#008000'},
                            {"min":50,"max":100,"label":'良','color':'#FFFF00'},
                            {"min":100,"max":150,"label":'轻度污染','color':'#FFA500'},
                            {"min":150,"max":200,"label":'中度污染','color':'#FF0000'},
                            {"min":200,"max":300,"label":'重度污染','color':'#9932CC'},
                            {"min":300,"max":500,"label":'严重污染','color':'#800080'},],),
            )                       
            st_pyecharts(cal,width='800px', height='400px')
        calendar()       
    elif year == "2019":
        data = data['2019-01-01':'2019-12-31']
        def calendar():
            global data
            data = data.reset_index()
            date = pd.to_datetime(data['date']).tolist()
            aqi = data['AQI'].values.tolist()
            cal = Calendar()
            cal.add("",[z for z in zip(date,aqi)],
                calendar_opts=opts.CalendarOpts(
                    pos_top="100",pos_left="30",pos_right="30",pos_bottom='80',range_="2019",
                    daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn")),
            )
            cal.set_global_opts(
                title_opts=opts.TitleOpts(pos_top="25", pos_left="center", title="空气质量日历",title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                visualmap_opts=opts.VisualMapOpts(
                    max_=500, min_=0, orient="horizontal", is_piecewise=True,pos_top="350",pos_left="center",
                    pieces=[{"min":0,"max":50,"label":'优','color':'#008000'},
                            {"min":50,"max":100,"label":'良','color':'#FFFF00'},
                            {"min":100,"max":150,"label":'轻度污染','color':'#FFA500'},
                            {"min":150,"max":200,"label":'中度污染','color':'#FF0000'},
                            {"min":200,"max":300,"label":'重度污染','color':'#9932CC'},
                            {"min":300,"max":500,"label":'严重污染','color':'#800080'},],),
            )                       
            st_pyecharts(cal,width='800px', height='400px')
        calendar()       
    elif year == "2018":
        data = data['2018-01-01':'2018-12-31'] 
        def calendar():
            global data
            data = data.reset_index()
            date = pd.to_datetime(data['date']).tolist()
            aqi = data['AQI'].values.tolist()
            cal = Calendar()
            cal.add("",[z for z in zip(date,aqi)],
                calendar_opts=opts.CalendarOpts(
                    pos_top="100",pos_left="30",pos_right="30",pos_bottom='80',range_="2018",
                    daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn")),
            )
            cal.set_global_opts(
                title_opts=opts.TitleOpts(pos_top="25", pos_left="center", title="空气质量日历",title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                visualmap_opts=opts.VisualMapOpts(
                    max_=500, min_=0, orient="horizontal", is_piecewise=True,pos_top="350",pos_left="center",
                    pieces=[{"min":0,"max":50,"label":'优','color':'#008000'},
                            {"min":50,"max":100,"label":'良','color':'#FFFF00'},
                            {"min":100,"max":150,"label":'轻度污染','color':'#FFA500'},
                            {"min":150,"max":200,"label":'中度污染','color':'#FF0000'},
                            {"min":200,"max":300,"label":'重度污染','color':'#9932CC'},
                            {"min":300,"max":500,"label":'严重污染','color':'#800080'},],),
            )                       
            st_pyecharts(cal,width='800px', height='400px')
        calendar()     
    elif year == "2017":
        data = data['2017-01-01':'2017-12-31'] 
        def calendar():
            global data
            data = data.reset_index()
            date = pd.to_datetime(data['date']).tolist()
            aqi = data['AQI'].values.tolist()
            cal = Calendar()
            cal.add("",[z for z in zip(date,aqi)],
                calendar_opts=opts.CalendarOpts(
                    pos_top="100",pos_left="30",pos_right="30",pos_bottom='80',range_="2017",
                    daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn")),
            )
            cal.set_global_opts(
                title_opts=opts.TitleOpts(pos_top="25", pos_left="center", title="空气质量日历",title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
                visualmap_opts=opts.VisualMapOpts(
                    max_=500, min_=0, orient="horizontal", is_piecewise=True,pos_top="350",pos_left="center",
                    pieces=[{"min":0,"max":50,"label":'优','color':'#008000'},
                            {"min":50,"max":100,"label":'良','color':'#FFFF00'},
                            {"min":100,"max":150,"label":'轻度污染','color':'#FFA500'},
                            {"min":150,"max":200,"label":'中度污染','color':'#FF0000'},
                            {"min":200,"max":300,"label":'重度污染','color':'#9932CC'},
                            {"min":300,"max":500,"label":'严重污染','color':'#800080'},],),
            )                       
            st_pyecharts(cal,width='800px', height='400px')
        calendar()      

    def rose():  
        count = data['level'].value_counts().rename_axis('level').reset_index(name='count')
        a = count['level'].values.tolist()
        b = count['count'].values.tolist()
        pie = Pie()  
        pie.add("",[list(z) for z in zip(a,b)], 
            radius=["45%", "95%"],center=["50%", "50%"],
            rosetype="area"
        )
        pie.set_global_opts(title_opts=opts.TitleOpts(title='空气质量分级',title_textstyle_opts=opts.TextStyleOpts(font_size=20,color= '#40E0D0'),
                            pos_right= 'center',pos_left= 'center',pos_top= '47%',pos_bottom='center'),
                            legend_opts=opts.LegendOpts(is_show=False)
        )
        pie.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", font_size=15,
                                                    formatter="{b}:{c}天", font_style="italic",
                                                    font_weight="bold", font_family="Microsoft YaHei")
        ) 
        st_pyecharts(pie,width='600px', height='500px')
    rose()

    def line():
        global data
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date').sort_index(ascending=True)
        p1 = data['pm25'].resample('m').mean().round()
        p2 = data['pm10'].resample('m').mean().round()
        p3 = data['o3'].resample('m').mean().round()
        p4 = data['no2'].resample('m').mean().round()
        p5 = data['so2'].resample('m').mean().round()
        p6 = data['co'].resample('m').mean().round()
        x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        line = Line(init_opts=opts.InitOpts(width='900px', height='600px'))
        line.add_xaxis(xaxis_data=x_data)
        line.add_yaxis("月均pm25",p1,label_opts=opts.LabelOpts(is_show=False))
        line.add_yaxis("月均pm10",p2,label_opts=opts.LabelOpts(is_show=False))
        line.add_yaxis("月均o3",p3,label_opts=opts.LabelOpts(is_show=False))
        line.add_yaxis("月均no2",p4,label_opts=opts.LabelOpts(is_show=False))
        line.add_yaxis("月均so2",p5,label_opts=opts.LabelOpts(is_show=False))
        line.add_yaxis("月均co",p6,label_opts=opts.LabelOpts(is_show=False))
        line.set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(min_=0,max_=150,interval=15,
            axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        st_pyecharts (line,width='600px', height='400px')
    line()

    def line1():
        c = data['AQI'].resample('m').mean().round()
        c = c.values.tolist()
        x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        line1 = Line()
        line1.add_xaxis(xaxis_data=x_data)
        line1.add_yaxis("月均AQI",c,label_opts=opts.LabelOpts(is_show=False))
        line1.set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(min_=0,max_=150,interval=15,
            axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        st_pyecharts (line1,width='600px', height='400px') 
    line1() 

    fig = plt.figure(figsize=(20,10))
    ax = sns.heatmap(data.corr(), cmap=plt.cm.RdYlBu_r, annot=True, fmt='.2f')
    st.pyplot(fig)  

    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(data)

    st.download_button(
         label="Download data as CSV",
         data=csv,
         file_name='air_quality.csv',
         mime='text/csv',
    )  

elif sidebar == "自主上传文件":
    st.title("自主上传文件")
    uploaded_file = st.file_uploader("选择文件")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        #st.write(data)

        def value_to_level(AQI):
            if AQI>=0 and AQI<=50:
                return '优'
            elif AQI>=51 and AQI<=100:
                return '良'
            elif AQI>=101 and AQI<=150:
                return '轻度污染'
            elif AQI>=151 and AQI<=200:
                return '中度污染'
            elif AQI>=201 and AQI<=300:
                return '重度污染'
            else:
                return '严重污染'
        level = data['AQI'].apply(value_to_level)
        data['level'] = level

        def rose():  
            count = data['level'].value_counts().rename_axis('level').reset_index(name='count')
            a = count['level'].values.tolist()
            b = count['count'].values.tolist()
            pie = Pie()  
            pie.add("",[list(z) for z in zip(a,b)], 
                radius=["45%", "95%"],center=["50%", "50%"],
                rosetype="area"
            )
            pie.set_global_opts(title_opts=opts.TitleOpts(title='空气质量分级',title_textstyle_opts=opts.TextStyleOpts(font_size=20,color= '#40E0D0'),
                                pos_right= 'center',pos_left= 'center',pos_top= '47%',pos_bottom='center'),
                                legend_opts=opts.LegendOpts(is_show=False)
            )
            pie.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", font_size=15,
                                                        formatter="{b}:{c}天", font_style="italic",
                                                        font_weight="bold", font_family="Microsoft YaHei")
            ) 
            st_pyecharts(pie,width='600px', height='400px')
        rose()

        def line():
            global data
            data['date'] = pd.to_datetime(data['date'])
            data = data.set_index('date').sort_index(ascending=True)
            p1 = data['pm25'].resample('m').mean().round()
            p2 = data['pm10'].resample('m').mean().round()
            p3 = data['o3'].resample('m').mean().round()
            p4 = data['no2'].resample('m').mean().round()
            p5 = data['so2'].resample('m').mean().round()
            p6 = data['co'].resample('m').mean().round()
            x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
            line = Line(init_opts=opts.InitOpts(width='900px', height='600px'))
            line.add_xaxis(xaxis_data=x_data)
            line.add_yaxis("月均pm25",p1,label_opts=opts.LabelOpts(is_show=False))
            line.add_yaxis("月均pm10",p2,label_opts=opts.LabelOpts(is_show=False))
            line.add_yaxis("月均o3",p3,label_opts=opts.LabelOpts(is_show=False))
            line.add_yaxis("月均no2",p4,label_opts=opts.LabelOpts(is_show=False))
            line.add_yaxis("月均so2",p5,label_opts=opts.LabelOpts(is_show=False))
            line.add_yaxis("月均co",p6,label_opts=opts.LabelOpts(is_show=False))
            line.set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(min_=0,max_=150,interval=15,
                axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
            st_pyecharts (line,width='600px', height='400px')
        line()

        def line1():
            c = data['AQI'].resample('m').mean().round()
            c = c.values.tolist()
            x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
            line1 = Line()
            line1.add_xaxis(xaxis_data=x_data)
            line1.add_yaxis("月均AQI",c,label_opts=opts.LabelOpts(is_show=False))
            line1.set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(min_=0,max_=150,interval=15,
                axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
            st_pyecharts (line1,width='600px', height='400px') 
        line1()

        fig = plt.figure(figsize=(20,10))
        ax = sns.heatmap(data.corr(), cmap=plt.cm.RdYlBu_r, annot=True, fmt='.2f')
        st.pyplot(fig)