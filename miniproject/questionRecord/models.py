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


###one concept belongs to exactly one unit
##单元里包含概念
class Unit(models.Model):
    unitID = models.AutoField(primary_key=True)
    unitName = models.TextField()
    concept = models.ForeignKey(Concept, related_name="concept", null=True, on_delete=models.CASCADE)
    #一个unit有多个concept,一个concept只在一个unit

    def __str__(self):
        return "Unit:" + str(self.unitID) + str(self.unitName)

    class Meta:
        db_table = "Unit"


# delete Question table and add Example Table

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

#delete LevelList and use 0/1 to mark the level

# #等级表 为了Level跟Example多对多而设
# class LevelList(models.Model):
#     levelId = models.IntegerField(primary_key=True)
#     levelName = models.TextField(default="Level") ##无用属性
#     def __str__(self):
#         return "LevelList:" + str(self.levelId)
#
#     class Meta:
#         db_table = "LevelList"
#         verbose_name = "LevelLists"
#         verbose_name_plural = verbose_name

class Example(models.Model):
    unit = models.ForeignKey(Unit, related_name="unit", null=True, on_delete=models.CASCADE)

    conceptID = models.ForeignKey(Concept, related_name="concept", null=True, on_delete=models.CASCADE)
    subConcept1id = models.ForeignKey(SubConcept, related_name="subconcept1", null=True, on_delete=models.CASCADE)
    subConcept2id = models.ForeignKey(SubConcept, related_name="subconcept2", null=True, on_delete=models.CASCADE)
    exampleID = models.AutoField(primary_key=True)
    example = models.TextField() ##example的具体内容
    meaning = models.TextField()
    translation = models.TextField()
    #add questionlevel attribute
    level1Mode = models.BooleanField(default=1)
    level2Mode = models.BooleanField(default=1)
    level3Mode = models.BooleanField(default=1)
    level4Mode = models.BooleanField(default=1)
    level5Mode = models.BooleanField(default=0)
    level6Mode = models.BooleanField(default=0)

    # level =  models.ManyToManyField(LevelList) #多对多

    def __str__(self):
        return "Example:" + str(self.exampleID)

    class Meta:
        db_table = "Example"
        verbose_name = "Examples"
        verbose_name_plural = verbose_name

#错题
class Wrong(models.Model):
    uerID = models.IntegerField(primary_key=True)  # user id must be unique
    question = models.ForeignKey(Example, related_name="wrong", null=False, blank=False, on_delete=models.CASCADE)
    createTime = models.DateTimeField(default=timezone.now) #首次错误时间
    updateTime = models.DateTimeField(auto_now=True)  # keep updated 以最新错误时间为准
    count = models.CharField(max_length=100, default='0')  # error times can be null

    def __str__(self):
        return "User:" + str(self.uerID) + " Example:" + str(self.example.exampleID)  # return primary key

    class Meta:
        db_table = "Wrong"


### two types of choice questions: Level2 and Level3

### add Level2 Table

## Level2: what's the concept of '(the example sentence or phrases)'?
# one correct concept that the example belongs to, three other wrong
class Level2(models.Model):
    qstID = models.TextField() #L2....
    conceptID = models.ForeignKey(Example, related_name="conceptL2", null=False, blank=False, on_delete=models.CASCADE)
    # three misleading choices(similar concepts in the same unit?)
    op1 = models.TextField()
    op2 = models.TextField()
    op3 = models.TextField()

    def __str__(self):
        return "Level2Question:" + str(self.qstID)

    class Meta:
        db_table = "Level2"
        verbose_name = "Level2Questions"
        verbose_name_plural = verbose_name


## add Level3 Table
## Level3: what's the meaning of '(the example sentence or phrases)'?
# one correct english meaning that the example indicates, three other wrong
class Level3(models.Model):
    qstID = models.AutoField(primary_key=True) #L3...
    meaning = models.ForeignKey(Example, related_name="meaningL3", null=False, blank=False, on_delete=models.CASCADE)
    # three misleading choices
    op1 = models.TextField()
    op2 = models.TextField()
    op3 = models.TextField()

    def __str__(self):
        return "Level3Question:" + str(self.qstID)

    class Meta:
        db_table = "Level3"
        verbose_name = "Level3Questions"
        verbose_name_plural = verbose_name

class Level4(models.Model):
    qstID = models.AutoField(primary_key=True) #L4...
    translation = models.ForeignKey(Example, related_name="chineseMeaningL4", null=False, blank=False, on_delete=models.CASCADE)


    def __str__(self):
        return "Level4Question:" + str(self.qstID)

    class Meta:
        db_table = "Level4"
        verbose_name = "Level4Questions"
        verbose_name_plural = verbose_name



#### Wait for confirmation incomplete
class CommonUser(models.Model):
    commonUserID = models.CharField(max_length=225,primary_key=True)
    groupsID = models.IntegerField()
    session_key = models.CharField(max_length=225, verbose_name="session_key", default="")

    def __str__(self):
        return "User:" + str(self.commonUserID)

    class Meta:
        db_table = "CommonUser"
        verbose_name = "CommonUsers"
        verbose_name_plural = verbose_name


##分组
class Groups(models.Model):
    gID = models.IntegerField(primary_key=True)
    gName = models.TextField()

    def __str__(self):
        return "Group:" + str(self.gID)

    class Meta:
        db_table = "Groups"
        verbose_name = "Groups"
        verbose_name_plural = verbose_name


###收藏夹
class NotesCollection(models.Model):
    uerId = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    collectExampleID = models.ManyToManyField(Example)

    def __str__(self):
        return "NotesCollection:" + str(self.uerID) + str(self.collectExampleID)

    class Meta:
        db_table = "NotesCollection"
        verbose_name = "NotesCollections"
        verbose_name_plural = verbose_name


##每日任务
class DailyTask(models.Model):
    uerId = models.ForeignKey(CommonUser, related_name='uerID', null=False, blank=False, on_delete=models.CASCADE)
    dailyGoalNum = models.IntegerField()

    def __str__(self):
        return "DailyTask:" + str(self.uerID) + str(self.dailyGoalNum)

    class Meta:
        db_table = "DailyTask"
        verbose_name = "DailyTasks"
        verbose_name_plural = verbose_name

##做题历史记录
class History(models.Model):
    uerId = models.ForeignKey(CommonUser, related_name='uerIDhist')
    eId = models.TextField() ##所有做过的题的exampleID

    def __str__(self):
        return "History:" + str(self.uerId) + str(self.eID)

    class Meta:
        db_table = "History"
        verbose_name = "Histories"
        verbose_name_plural = verbose_name



##进度：做题量跟积分
class Progress(models.Model):
    uerId = models.ForeignKey(CommonUser, related_name='uerIDprogress')
    qstNum = models.TextField()  ##做过的题数
    cumScore = models.TextField()

    def __str__(self):
        return "Progress:" + str(self.uerId) + str(self.qstNum) + str(self.cumScore)

    class Meta:
        db_table = "Progress"
        verbose_name = "Progresses"
        verbose_name_plural = verbose_name

##排位对照表
class RankScale(models.Model):
    ranking = models.TextField()
    score = models.TextField()
    def __str__(self):
        return "RankScale:" + str(self.score) + str(self.ranking)

    class Meta:
        db_table = "RankScale"
        verbose_name = "RankScales"
        verbose_name_plural = verbose_name