from django.db import models
from django.contrib.postgres.fields import ArrayField

COLOR_CHOICES = {
    0: "black",
    1: "blue",
    2: "brown",
    3: "climber",
    4: "cream",
    5: "going down",
    6: "green",
    7: "orange",
    8: "pink",
    9: "purple",
    10: "red",
    11: "white",
    12: "yellow",
}

# Create your models here.
class Page(models.Model):
    date = models.DateField(auto_now_add=True)
    bouldering_clear_color = ArrayField(models.IntegerField(choices=COLOR_CHOICES), verbose_name="bcc")
    endurance_clear_color = ArrayField(models.IntegerField(choices=COLOR_CHOICES), verbose_name="ecc")
    climbing_center_name = models.CharField(max_length=20, verbose_name="name")
    start_time = models.TimeField(blank=True, null=True, verbose_name="start")
    end_time = models.TimeField(blank=True, null=True, verbose_name="end")

class Clip(models.Model):
    page_id = models.ForeignKey(Page, related_name="page", on_delete=models.CASCADE)
    checkpoint1 = models.TimeField(blank=True, null=True, verbose_name="cp1")
    checkpoint2 = models.TimeField(blank=True, null=True, verbose_name="cp2")
    totaltime = models.TimeField(blank=True, null=True, verbose_name="tt")
    succes_check = models.BooleanField(default=False, verbose_name="check")

class Frame(models.Model):
    image = models.ImageField()

class Hold(models.Model):
    color = ArrayField(models.IntegerField(choices=COLOR_CHOICES))
    is_top = models.BooleanField(default=False, verbose_name="top")
    x1 = models.FloatField()
    x2 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    frame_id = models.ForeignKey(Frame, related_name="frame", on_delete=models.CASCADE)