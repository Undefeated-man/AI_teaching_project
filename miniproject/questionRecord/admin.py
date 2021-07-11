from django.contrib import admin
from .models import *
# Register your models here.

admin.register(Concept)
admin.register(SubConcept)
admin.register(Unit)
admin.register(Example)
admin.register(Wrong)
admin.register(Level2)
admin.register(Level3)
admin.register(CommonUser)
admin.register(Group)

