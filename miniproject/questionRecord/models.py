from django.db import models

from django.utils import timezone


# Create your models here.

class Concept(models.Model):
    conceptID=models.AutoField(primary_key=True)
    conceptName=models.CharField(unique=True,max_length=100,null=False,blank=False)

    def __str__(self):
        return "Concept:" + str(self.conceptName)

    class Meta:
        db_table = "Concept"


class SubConcept(models.Model):
    subConceptID=models.AutoField(primary_key=True)
    subConceptName=models.CharField(unique=True,max_length=100,null=False,blank=False)

    def __str__(self):
        return "subConceptName:" + str(self.subConceptID)

    class Meta:
        db_table = "SubConcept"


class Question(models.Model):
    questionID = models.AutoField(primary_key=True)
    concept = models.ForeignKey(Concept,related_name="question",null=True,on_delete=models.CASCADE)
    subConcept1 = models.ForeignKey(SubConcept,related_name="question1",null=True,on_delete=models.CASCADE)
    subConcept2 = models.ForeignKey(SubConcept,related_name="question2",null=True,on_delete=models.CASCADE)
    example = models.CharField(max_length=100)
    meaning = models.CharField(max_length=100)
    translation = models.CharField(max_length=500)

    def __str__(self):
        return "Question:" + str(self.questionID)

    class Meta:
        db_table = "Question"
        verbose_name = "Questions"
        verbose_name_plural = verbose_name


class Wrong(models.Model):
    uerID = models.IntegerField(primary_key=True)  # user id must be unique
    question = models.ForeignKey(Question,related_name="wrong",null=False,blank=False,on_delete=models.CASCADE)
    createTime = models.DateTimeField(default=timezone.now)
    updateTime = models.DateTimeField(auto_now=True)  # keep updated
    count = models.CharField(max_length=100, default='0')  # error times can be null

    def __str__(self):
        return "User:" + str(self.uerID) + " Question:" + str(self.question.questionID)  # return primary key

    class Meta:
        db_table = "Wrong"

