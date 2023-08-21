from django.db import models

# Create your models here.
class MetaInfo(models.Model):
    theme_id = models.AutoField(primary_key=True)
    theme_name = models.CharField(max_length=255)
    rsv_url = models.CharField(max_length=511)
    store_name = models.CharField(max_length=63)
    store_url = models.CharField(max_length=511)
    loc_1 = models.CharField(max_length=31)
    loc_2 = models.CharField(max_length=31)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class ScoreInfo(models.Model):
    theme = models.ForeignKey(MetaInfo, on_delete=models.CASCADE)
    check_date = models.DateField(db_index=True)
    total_review = models.IntegerField(default=0)
    recommend_ratio = models.FloatField()
    difficulty_score = models.FloatField()
    satisfy_score = models.FloatField()
    story_score = models.FloatField()
    direction_score = models.FloatField()
    interior_score = models.FloatField()
    problem_score = models.FloatField()
    activity_score = models.FloatField()
    fear_score = models.FloatField()
    prev_1d_reservation_rate = models.FloatField(default=0.0, help_text="하루 전 예약률")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class ReserveInfo(models.Model):
    theme = models.ForeignKey(MetaInfo, on_delete=models.CASCADE)
    check_date_hour = models.DateTimeField(db_index=True)
    rsv_datetime = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

