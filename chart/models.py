from django.db import models
class chartdate(models.Model):
    year=models.IntegerField()
    month=models.IntegerField()
    day=models.IntegerField()
    direction=models.IntegerField()
    Xaxisa=models.IntegerField()
    Xaxisb=models.IntegerField()
    Yaxis=models.IntegerField()
    Alane=models.IntegerField()
    Blane=models.IntegerField()
    Clane=models.IntegerField()
    Dlane=models.IntegerField()

    # def __str__(self):
    #     return self.title

class sectordiagram(models.Model):
    originyear=models.IntegerField()
    originmonth = models.IntegerField()
    originday = models.IntegerField()
    originhour = models.IntegerField()
    originmin=models.IntegerField()
    endyear = models.IntegerField()
    endmonth = models.IntegerField()
    endday = models.IntegerField()
    endhour = models.IntegerField()
    endmin=models.IntegerField()
    class Meta:
        managed=False
        db_table='sectordiagram'

class datacheck(models.Model):
    originyear = models.IntegerField()
    originmonth = models.IntegerField()
    originday = models.IntegerField()
    endyear = models.IntegerField()
    endmonth = models.IntegerField()
    endday = models.IntegerField()
    intersectionid= models.IntegerField()
    time_lenth=models.IntegerField()
    class Meta:
        managed=False
        db_table='datacheck'

class phasecheck(models.Model):
    originyear = models.IntegerField()
    originmonth = models.IntegerField()
    originday = models.IntegerField()
    intersectionid_s = models.IntegerField()
    intersectionid_e = models.IntegerField()
    class Meta:
        managed=False
        db_table='phasecheck'





class Tsclane(models.Model):
    sid = models.IntegerField(blank=True, null=True)
    feature = models.IntegerField(blank=True, null=True)
    attribute = models.IntegerField(blank=True, null=True)
    movement = models.IntegerField(blank=True, null=True)
    detector = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    intersectionid = models.IntegerField(db_column='intersectionId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tsclane'



class I023(models.Model):
    id = models.IntegerField(primary_key=True)
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i023'

class I024(models.Model):
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i024'

class I055(models.Model):
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i055'

class I056(models.Model):
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i056'

class I057(models.Model):
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i057'

class I058(models.Model):
    id = models.IntegerField(primary_key=True)
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i058'

class I075(models.Model):
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i075'

class I077(models.Model):
    id = models.IntegerField(primary_key=True)
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i077'

class I089(models.Model):
    id = models.IntegerField(primary_key=True)
    inteid = models.IntegerField(blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    carplate = models.CharField(max_length=11, blank=True, null=True)
    passtime = models.DateTimeField(blank=True, null=True)
    traveltime = models.IntegerField(blank=True, null=True)
    upinteid = models.IntegerField(blank=True, null=True)
    updirection = models.IntegerField(blank=True, null=True)
    uplane = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'i089'

# Create your models here.
