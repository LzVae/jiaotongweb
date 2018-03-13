from django import  forms
from django.forms import Form, fields, widgets
from django.conf import settings
from chart.models import chartdate,sectordiagram,datacheck,Tsclane,phasecheck
import django.views
from django.forms import fields
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.forms import  ModelForm



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


def getidtsclane(a, b):  # 得到对应路口的渠化信息  a:渠化列表 b 路口id
    t = []
    for row in a:
        if row[3] == b:
            t.append(row)
    return t


t=chartdate.objects.get(id=1)
g=datacheck.objects.get(id=1)
k1=phasecheck.objects.get(id=1)

class ChartForm(forms.ModelForm):

    year = forms.IntegerField(label='year',required=True,error_messages={'required':'非空'},initial=t.year,widget=forms.TextInput(attrs={'placeholder':'年'}))
    month = forms.IntegerField(label='month',required=True,error_messages={'required':'非空'},initial=t.month,widget=forms.TextInput(attrs={'placeholder':'月'}))
    day = forms.IntegerField(label='day',required=True,error_messages={'required':'非空'},initial=t.day,widget=forms.TextInput(attrs={'placeholder':'日'}))
    #direction = forms.IntegerField(label='direction',required=True,error_messages={'required':'非空'},initial=t.direction,widget=forms.TextInput(attrs={'placeholder':'路口'}))
    direction_choices=[
        (23,u'23'),(24,u'24'),(55, u'55'),(56, u'56'),(57, u'57'),(58, u'58'),(75, u'75'),(77, u'77'),(89, u'89'),
    ]

    direction = forms.IntegerField(label='direction', required=True, error_messages={'required': '非空'}, widget=forms.Select(attrs={'placeholder': '路口'},choices=direction_choices))
    Xaxisa = forms.IntegerField(label='Xaxisa',required=True,error_messages={'required':'非空'},initial=t.Xaxisa,widget=forms.TextInput(attrs={'placeholder':'起点'}))
    Xaxisb = forms.IntegerField(label='Xaxisb',required=True,error_messages={'required':'非空'},initial=t.Xaxisb,widget=forms.TextInput(attrs={'placeholder':'重点'}))
    Yaxis = forms.IntegerField(label='Yaxis',required=True,error_messages={'required':'非空'},initial=t.Yaxis,widget=forms.TextInput(attrs={'placeholder':'周期'}))
    Alane = forms.IntegerField(label='Alane', required=True, error_messages={'required': '非空'}, initial=t.Alane,
                               widget=forms.Select(attrs={'placeholder': 'Asid'}))
    Blane = forms.IntegerField(label='Blane', required=True, error_messages={'required': '非空'}, initial=t.Blane,
                               widget=forms.Select(attrs={'placeholder': 'Asid'}))
    Clane = forms.IntegerField(label='Clane', required=True, error_messages={'required': '非空'}, initial=t.Clane,
                               widget=forms.Select(attrs={'placeholder': 'Asid'}))
    Dlane = forms.IntegerField(label='Dlane', required=True, error_messages={'required': '非空'}, initial=t.Dlane,
                               widget=forms.Select(attrs={'placeholder': 'Asid'}))
   #  lane_choices=[
   #      (1,u'1'),(2,u'2'),(3,u'3'),(4,u'4'),(5,u'5'),(6,u'6'),(7,u'7'),(8,u'8'),(9,u'9'),(10,u'10'),
   #      (11,u'11'),(12,u'12'),(13,u'13'),(14,u'14'),(15,u'15'),(16,u'16'),(17,u'17'),(18,u'18'),(19,u'19'),(20,u'20'),(-999,u'无'),
   # ]



    class Meta:
        model=chartdate

        fields=["year","month","day","direction","Xaxisa","Xaxisb","Yaxis","Alane","Blane","Clane","Dlane"]

    def __init__(self, *args, **kwargs):
        
        super(ChartForm, self).__init__(*args, **kwargs)
        print('init1')
        f = chartdate.objects.get(id=1)
        print("heihei"+str(f.direction))
        idtsclane = getidtsclane(tsclane, f.direction)
        num = len(idtsclane)
        #print(num)
        lane_choices = []
        for i in range(num):
            lane_choices.append(((i + 1),  str(i + 1)))
        lane_choices.append((-999, u'无'))
        print(lane_choices)


        self.fields['year'].initial=f.year
        self.fields['month'].initial = f.month
        self.fields['day'].initial = f.day
        self.fields['direction'].initial = f.direction
        self.fields['Xaxisa'].initial = f.Xaxisa
        self.fields['Xaxisb'].initial = f.Xaxisb
        self.fields['Yaxis'].initial = f.Yaxis
        self.fields['Alane'].initial = f.Alane
        self.fields['Blane'].initial = f.Blane
        self.fields['Clane'].initial = f.Clane
        self.fields['Dlane'].initial = f.Dlane
        self.fields['Alane'].widget.choices=lane_choices

        self.fields['Blane'].widget.choices = lane_choices
        self.fields['Clane'].widget.choices = lane_choices
        self.fields['Dlane'].widget.choices = lane_choices


        # fields = ["year", "month", "day"]

# class ChartForm(ModelForm):
#     class Meta:
#         model=chartdate
#         fields=['year',"month","day","direction","Xaxisa","Xaxisb","Yaxis","Alane","Blane","Clane","Dlane"]

k=sectordiagram.objects.get(id=1)




class SectordiagramForm(forms.ModelForm):
    originyear = forms.IntegerField(label='originyear', required=True, error_messages={'required': '非空'}, initial=k.originyear,widget=forms.TextInput(attrs={'placeholder': '年'}))
    originmonth = forms.IntegerField(label='originmonth', required=True, error_messages={'required': '非空'},initial=k.originmonth, widget=forms.TextInput(attrs={'placeholder': '月'}))
    originday = forms.IntegerField(label='originday', required=True, error_messages={'required': '非空'},initial=k.originday, widget=forms.TextInput(attrs={'placeholder': '日'}))
    originhour=forms.IntegerField(label='originhour', required=True, error_messages={'required': '非空'},initial=k.originhour, widget=forms.TextInput(attrs={'placeholder': '小时'}))
    min_choices=(
        (0, u'0'),(15, u'15'),(30, u'30'),(45, u'45'),
    )
    originmin = forms.IntegerField(label='originmin ', required=True, error_messages={'required': '非空'},initial=k.originmin, widget=forms.Select(attrs={'placeholder': '分钟'},choices=min_choices))

    endyear = forms.IntegerField(label='endyear', required=True, error_messages={'required': '非空'},initial=k.endyear, widget=forms.TextInput(attrs={'placeholder': '年'}))
    endmonth = forms.IntegerField(label='endmonth', required=True, error_messages={'required': '非空'},initial=k.endmonth, widget=forms.TextInput(attrs={'placeholder': '月'}))
    endday = forms.IntegerField(label='endday', required=True, error_messages={'required': '非空'}, initial=k.endday,widget=forms.TextInput(attrs={'placeholder': '日'}))
    endhour=forms.IntegerField(label='endhour', required=True, error_messages={'required': '非空'}, initial=k.endhour,widget=forms.TextInput(attrs={'placeholder': '小时'}))
    min_choices = (
        (0, u'0'), (15, u'15'), (30, u'30'), (45, u'45'),
    )
    endmin = forms.IntegerField(label='endmin ', required=True, error_messages={'required': '非空'}, initial=k.endmin,widget=forms.Select(attrs={'placeholder': '分钟'}, choices=min_choices))

    class Meta:
        model=sectordiagram
        fields=['originyear','originmonth','originday','originhour','originmin','endyear','endmonth','endday','endhour','endmin']
    def __init__(self, *args, **kwargs):
        super(SectordiagramForm, self).__init__(*args, **kwargs)
        print('init2')
        f=sectordiagram.objects.get(id=1)
        self.fields['originyear'].initial=f.originyear
        self.fields['originmonth'].initial = f.originmonth
        self.fields['originday'].initial = f.originday
        self.fields['originhour'].initial = f.originhour
        self.fields['originmin'].initial = f.originmin
        self.fields['endyear'].initial = f.endyear
        self.fields['endmonth'].initial = f.endmonth
        self.fields['endday'].initial = f.endday
        self.fields['endhour'].initial = f.endhour
        self.fields['endmin'].initial = f.endmin






class datacheckForm(forms.ModelForm):
    originyear = forms.IntegerField(label='originyear', required=True, error_messages={'required': '非空'},
                                    initial=g.originyear, widget=forms.TextInput(attrs={'placeholder': '年'}))
    originmonth = forms.IntegerField(label='originmonth', required=True, error_messages={'required': '非空'},
                                     initial=g.originmonth, widget=forms.TextInput(attrs={'placeholder': '月'}))
    originday = forms.IntegerField(label='originday', required=True, error_messages={'required': '非空'},
                                   initial=g.originday, widget=forms.TextInput(attrs={'placeholder': '日'}))
    endyear = forms.IntegerField(label='endyear', required=False, error_messages={'required': '非空'},initial=g.endyear, widget=forms.TextInput(attrs={'placeholder': '年'}))
    endmonth = forms.IntegerField(label='endmonth', required=False, error_messages={'required': '非空'},initial=g.endmonth, widget=forms.TextInput(attrs={'placeholder': '月'}))
    endday = forms.IntegerField(label='endday', required=False, error_messages={'required': '非空'}, initial=g.endday,widget=forms.TextInput(attrs={'placeholder': '日'}))
    direction_choices=(
        (23,u'23'),(24,u'24'),(55, u'55'),(56, u'56'),(57, u'57'),(58, u'58'),(75, u'75'),(77, u'77'),(89, u'89'),
    )
    direction_choices123 = (
        (55, u'55市府大道-白云山南路'), (58, u'58市府大道-机场路'),
    )
    intersectionid = forms.IntegerField(label='intersectionid', required=True, error_messages={'required': '非空'},initial=g.intersectionid, widget=forms.Select(attrs={'placeholder': '路口'},choices=direction_choices123))
    time_lenth = forms.IntegerField(label='time_lenth', required=True, error_messages={'required': '非空'}, initial=g.time_lenth,
                                widget=forms.TextInput(attrs={'placeholder': '时间间隔'}))
    class Meta:
        model=datacheck
        fields=['originyear','originmonth','originday','endyear','endmonth','endday','intersectionid','time_lenth']

    def __init__(self, *args, **kwargs):
        super(datacheckForm, self).__init__(*args, **kwargs)
        print('init3')
        f = datacheck.objects.get(id=1)
        self.fields['originyear'].initial = f.originyear
        self.fields['originmonth'].initial = f.originmonth
        self.fields['originday'].initial = f.originday
        self.fields['endyear'].initial = f.endyear
        self.fields['endmonth'].initial = f.endmonth
        self.fields['endday'].initial = f.endday
        self.fields['intersectionid'].initial = f.intersectionid
        self.fields['time_lenth'].initial = f.time_lenth


class phasecheckFrom(forms.ModelForm):
    originyear = forms.IntegerField(label='originyear', required=True, error_messages={'required': '非空'},
                                    initial=k1.originyear, widget=forms.TextInput(attrs={'placeholder': '年'}))
    originmonth = forms.IntegerField(label='originmonth', required=True, error_messages={'required': '非空'},
                                     initial=k1.originmonth, widget=forms.TextInput(attrs={'placeholder': '月'}))
    originday = forms.IntegerField(label='originday', required=True, error_messages={'required': '非空'},
                                   initial=k1.originday, widget=forms.TextInput(attrs={'placeholder': '日'}))
    direction_choices123 = (
        (23, u'23东环大道-枫南路'), (75, u'75东环大道-开元路'),
    )
    intersectionid_s = forms.IntegerField(label='intersectionid', required=True, error_messages={'required': '非空'},
                                        initial=k1.intersectionid_s,
                                        widget=forms.Select(attrs={'placeholder': '路口'}, choices=direction_choices123))
    intersectionid_e = forms.IntegerField(label='intersectionid', required=True, error_messages={'required': '非空'},
                                        initial=k1.intersectionid_e,
                                        widget=forms.Select(attrs={'placeholder': '路口'}, choices=direction_choices123))

    class Meta:
        model = phasecheck
        fields = ['originyear', 'originmonth', 'originday', 'intersectionid_s',
                  'intersectionid_e']

    def __init__(self, *args, **kwargs):
        super(phasecheckFrom, self).__init__(*args, **kwargs)
        #print('init3')
        f = phasecheck.objects.get(id=1)
        self.fields['originyear'].initial = f.originyear
        self.fields['originmonth'].initial = f.originmonth
        self.fields['originday'].initial = f.originday
        self.fields['intersectionid_s'].initial = f.intersectionid_s
        self.fields['intersectionid_e'].initial = f.intersectionid_e
