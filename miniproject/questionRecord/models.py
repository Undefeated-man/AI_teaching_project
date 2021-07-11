from django.db import models

from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Concept(models.Model):
    conceptID = models.AutoField(primary_key=True)
    conceptName = models.CharField(unique=True, max_length=100, null=False, blank=False)

    ###new here, add description attribute
    conceptDescription = models.TextField()

    def __str__(self):
        return "Concept:" + str(self.conceptName)

    class Meta:
        db_table = "Concept"


class SubConcept(models.Model):
    subConceptID = models.AutoField(primary_key=True)
    subConceptName = models.CharField(unique=True, max_length=100, null=False, blank=False)

    def __str__(self):
        return "subConceptName:" + str(self.subConceptID)

    class Meta:
        db_table = "SubConcept"


###new here, one concept belongs to exactly one unit, 11 units in total
class Unit(models.Model):
    UnitID = models.AutoField(primary_key=True)
    UnitName = models.TextField()
    conceptID = models.ForeignKey(Concept, related_name="concept", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "UnitID:" + str(self.UnitID)

    class Meta:
        db_table = "Unit"


# ###new here, delete Question table and add Example Table


# class Question(models.Model):
#     questionID = models.AutoField(primary_key=True)
#     concept = models.ForeignKey(Concept,related_name="question",null=True,on_delete=models.CASCADE)
#     subConcept1 = models.ForeignKey(SubConcept,related_name="question1",null=True,on_delete=models.CASCADE)
#     subConcept2 = models.ForeignKey(SubConcept,related_name="question2",null=True,on_delete=models.CASCADE)
#     example = models.TextField()
#     meaning = models.TextField()
#     translation = models.TextField()
#     ###new here, add questionlevel attribute
#     questionLevel = models.TextField(default='1') #default in level 1
#
#     def __str__(self):
#         return "Question:" + str(self.questionID)
#
#     class Meta:
#         db_table = "Question"
#         verbose_name = "Questions"
#         verbose_name_plural = verbose_name


class Example(models.Model):
    exampleID = models.AutoField(primary_key=True)
    conceptID = models.ForeignKey(Concept, related_name="concept", null=True, on_delete=models.CASCADE)
    subConcept1 = models.ForeignKey(SubConcept, related_name="subconcept1", null=True, on_delete=models.CASCADE)
    subConcept2 = models.ForeignKey(SubConcept, related_name="subconcept2", null=True, on_delete=models.CASCADE)
    example = models.TextField()
    meaning = models.TextField()
    translation = models.TextField()
    ###new here, add questionlevel attribute
    level = models.IntegerField(default='1')  # default in level 1

    def __str__(self):
        return "Example:" + str(self.exampleID)

    class Meta:
        db_table = "Example"
        verbose_name = "Examples"
        verbose_name_plural = verbose_name


class Wrong(models.Model):
    uerID = models.IntegerField(primary_key=True)  # user id must be unique
    question = models.ForeignKey(Example, related_name="wrong", null=False, blank=False, on_delete=models.CASCADE)
    createTime = models.DateTimeField(default=timezone.now)
    updateTime = models.DateTimeField(auto_now=True)  # keep updated
    count = models.CharField(max_length=100, default='0')  # error times can be null

    def __str__(self):
        return "User:" + str(self.uerID) + " Example:" + str(self.example.exampleID)  # return primary key

    class Meta:
        db_table = "Wrong"


### two types of choice questions: Level2 and Level3

###new here, add Level2 Table

##Level2: what's the concept of '(the example sentence or phrases)'?
# one correct concept that the example belongs to, three other wrong
class Level2(models.Model):
    exampleID = models.AutoField(primary_key=True)
    conceptID = models.ForeignKey(Example, related_name="concept", null=False, blank=False, on_delete=models.CASCADE)
    # three misleading choices
    op1 = models.TextField()
    op2 = models.TextField()
    op3 = models.TextField()

    def __str__(self):
        return "Level2Question:" + str(self.exampleID)

    class Meta:
        db_table = "Level2"
        verbose_name = "Level2Questions"
        verbose_name_plural = verbose_name


###new here, add Level3 Table
##Level3: what's the meaning of '(the example sentence or phrases)'?
# one correct english meaning that the example indicates, three other wrong
class Level3(models.Model):
    exampleID = models.AutoField(primary_key=True)
    meaning = models.ForeignKey(Example, related_name="meaning", null=False, blank=False, on_delete=models.CASCADE)
    # three misleading choices
    op1 = models.TextField()
    op2 = models.TextField()
    op3 = models.TextField()

    def __str__(self):
        return "Level3Question:" + str(self.exampleID)

    class Meta:
        db_table = "Level3"
        verbose_name = "Level3Questions"
        verbose_name_plural = verbose_name


#### Wait for confirmation incomplete
class CommonUser(AbstractUser):
    commonUserID = models.TextField(primary_key=True)
    groupsID = models.IntegerField()
    nickname = models.CharField(max_length=225, verbose_name="昵称", default="")
    avatar_url = models.CharField(max_length=225, verbose_name="头像", default="")
    session_key = models.CharField(max_length=225, verbose_name="session_key", default="")
    mobilePhoneNumber = models.CharField(max_length=225, verbose_name="手机号码", default="")
    def __str__(self):
        return "User:" + str(self.commonUserID)

    class Meta:
        db_table = "CommonUser"
        verbose_name = "CommonUsers"
        verbose_name_plural = verbose_name


###new here, group table
class Groups(models.Model):
    groupsID = models.IntegerField(primary_key=True)
    groupsName = models.TextField()

    def __str__(self):
        return "Group:" + str(self.groupsID)

    class Meta:
        db_table = "Groups"
        verbose_name = "Groups"
        verbose_name_plural = verbose_name
