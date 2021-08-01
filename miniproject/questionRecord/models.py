from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# Create your models here.

###one concept belongs to exactly one unit
##单元里包含概念
class Unit(models.Model):
    unitID = models.AutoField(primary_key=True)
    unitName = models.TextField()

    # 一个unit有多个concept,一个concept只在一个unit

    def __str__(self):
        return "Unit:" + str(self.unitID) + str(self.unitName)

    class Meta:
        db_table = "Unit"


class Concept(models.Model):
    conceptID = models.AutoField(primary_key=True)
    conceptName = models.CharField(unique=False, max_length=100, null=False, blank=False)
    unit = models.ForeignKey(Unit, related_name="concept", null=True, on_delete=models.CASCADE)
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


class Example(models.Model):
    unit = models.ForeignKey(Unit, related_name="unit", null=True, on_delete=models.CASCADE)

    concept = models.ForeignKey(Concept, related_name="concept", null=True, on_delete=models.CASCADE)
    subConcept1 = models.ForeignKey(SubConcept, related_name="Example1", null=True, on_delete=models.CASCADE)
    subConcept2 = models.ForeignKey(SubConcept, related_name="Example2", null=True, on_delete=models.CASCADE)
    exampleID = models.CharField(max_length=20, primary_key=True)
    example = models.TextField()  ##example的具体内容
    meaning = models.TextField()
    translation = models.TextField()
    # add questionlevel attribute
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


### two types of choice questions: Level2 and Level3

### add Level2 Table

## Level2: what's the concept of '(the example sentence or phrases)'?
# one correct concept that the example belongs to, three other wrong
class Level2(models.Model):
    questionID = models.CharField(max_length=20, primary_key=True)  # L2....
    example = models.OneToOneField(Example, related_name="Level2", null=False, blank=False, on_delete=models.CASCADE)
    question = models.TextField(null=False, blank=False)
    # three misleading choices(similar concepts in the same unit?)
    op1 = models.TextField(null=False, blank=False)
    op2 = models.TextField(null=False, blank=False)
    op3 = models.TextField(null=False, blank=False)

    def __str__(self):
        return "Level2Question:" + str(self.questionID)

    class Meta:
        db_table = "Level2"
        verbose_name = "Level2Questions"
        verbose_name_plural = verbose_name


## add Level3 Table
## Level3: what's the meaning of '(the example sentence or phrases)'?
# one correct english meaning that the example indicates, three other wrong
class Level3(models.Model):
    questionID = models.CharField(max_length=20, primary_key=True)  # L3...
    example = models.OneToOneField(Example, related_name="Level3", null=False, blank=False, on_delete=models.CASCADE)
    question = models.TextField(null=False, blank=False)
    # three misleading choices
    op1 = models.TextField(null=False, blank=False)
    op2 = models.TextField(null=False, blank=False)
    op3 = models.TextField(null=False, blank=False)

    def __str__(self):
        return "Level3Question:" + str(self.questionID)

    class Meta:
        db_table = "Level3"
        verbose_name = "Level3Questions"
        verbose_name_plural = verbose_name


class Level4(models.Model):
    questionID = models.CharField(max_length=20, primary_key=True)  # L4...
    example = models.OneToOneField(Example, related_name="Level4", null=False, blank=False, on_delete=models.CASCADE)
    question = models.TextField(null=False, blank=False)

    def __str__(self):
        return "Level4Question:" + str(self.questionID)

    class Meta:
        db_table = "Level4"
        verbose_name = "Level4Questions"
        verbose_name_plural = verbose_name


##分组
class Groups(models.Model):
    groupID = models.AutoField(primary_key=True)
    groupName = models.TextField()

    def __str__(self):
        return "Group:" + str(self.groupID)

    class Meta:
        db_table = "Groups"
        verbose_name = "Groups"
        verbose_name_plural = verbose_name


#### Wait for confirmation incomplete
class CommonUser(models.Model):
    commonUserID = models.CharField(max_length=225, primary_key=True)
    commonUserName = models.CharField(max_length=25)
    group = models.OneToOneField(Groups, related_name="CommonUser", on_delete=models.CASCADE, null=True, unique=False)
    level = models.CharField(max_length=20, null=False, blank=False, choices=[(1,"Level1"),(2, "Level2")
        , (3,"Level3"),(4,"Level4")],
                             default="Level1")
    imageLocation=models.TextField()
    # conSign=models.IntegerField(null=False, blank=False,default=0)
    continueCheckDays = models.IntegerField(null=False, blank=False, default=0)
    lastCheckDate = models.DateField()
    # level2Lock = models.BooleanField(null=False, default=True)
    # level3Lock = models.BooleanField(null=False,default=True)
    # level4Lock = models.BooleanField(null=False, default=True)
    meta = {'strict': False}
    def __str__(self):
        return "User:" + str(self.commonUserID)

    class Meta:
        db_table = "CommonUser"
        verbose_name = "CommonUsers"
        verbose_name_plural = verbose_name


###收藏夹
class NotesCollection(models.Model):
    commonUser = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, null=False, blank=False,choices=[(1,"Level1"),(2, "Level2")
        , (3,"Level3"),(4,"Level4")],
                             default="Level1")
    questionID = models.CharField(max_length=25, blank=False, null=False)

    def __str__(self):
        return "NotesCollection:" + str(self.commonUser.commonUserID) +" Question:"+str(self.questionID)

    class Meta:
        db_table = "NotesCollection"
        verbose_name = "NotesCollections"
        verbose_name_plural = verbose_name


##每日任务
class DailyTask(models.Model):
    commonUserID = models.OneToOneField(CommonUser, related_name='DailyTask', null=False, blank=False,
                                     on_delete=models.CASCADE)
    dailyGoalNum = models.IntegerField()

    def __str__(self):
        return "DailyTask:" + str(self.commonUserID) +" DailyTask:"+str(self.dailyGoalNum)

    class Meta:
        db_table = "DailyTask"
        verbose_name = "DailyTasks"
        verbose_name_plural = verbose_name


##做题历史记录
class History(models.Model):
    commonUser = models.ForeignKey(CommonUser, related_name='History', on_delete=models.CASCADE)
    level = models.CharField(max_length=20, null=False, blank=False, choices=[(1,"Level1"),(2, "Level2")
        , (3,"Level3"),(4,"Level4")],
                             default="Level1")
    questionID = models.CharField(max_length=25, blank=False, null=False)

    def __str__(self):
        return "History:" + str(self.commonUser.commonUserID) + " Question:" + str(self.questionID)

    class Meta:
        db_table = "History"
        verbose_name = "Histories"
        verbose_name_plural = verbose_name


##进度：做题量跟积分
class Progress(models.Model):
    commonUser = models.OneToOneField(CommonUser, related_name='Progress', on_delete=models.CASCADE)
    qstNum = models.IntegerField()  ##做过的题数
    cumScore = models.IntegerField()

    def __str__(self):
        return "Progress:" + str(self.commonUser.commonUserID)

    class Meta:
        db_table = "Progress"
        verbose_name = "Progresses"
        verbose_name_plural = verbose_name


# 错题
class Wrong(models.Model):
    commonUser = models.ForeignKey(CommonUser, on_delete=models.CASCADE)  # user id must be unique
    level = models.CharField(max_length=20, null=False, blank=False, choices=[(1,"Level1"),(2, "Level2")
        , (3,"Level3"),(4,"Level4")],
                             default="Level1")
    questionID = models.CharField(max_length=25, blank=False, null=False)
    createTime = models.DateTimeField(default=timezone.now)  # 首次错误时间
    updateTime = models.DateTimeField(auto_now=True)  # keep updated 以最新错误时间为准
    count = models.IntegerField(null=False,default=1)  # error times can be null

    def __str__(self):
        return "User:" + str(self.commonUser.commonUserID) + " Question:" + str(
            self.questionID)  # return primary key

    class Meta:
        db_table = "Wrong"

# ALTER TABLE Example MODIFY COLUMN translation longtext
#     CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;
# ALTER TABLE Level4 MODIFY COLUMN question longtext
#     CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;
# ALTER TABLE CommonUser MODIFY COLUMN commonUserName varchar(25)
#     CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;
