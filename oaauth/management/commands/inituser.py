from django.core.management.base import BaseCommand
from django.db.migrations import SeparateDatabaseAndState
from django.db.models import manager

from oaauth.models import OAUser, OADepartment


class Command(BaseCommand):
    def handle(self, *args, **options):
        boarder = OADepartment.objects.get(name = 'Board Department')
        developer = OADepartment.objects.get(name = 'product development department')
        operator = OADepartment.objects.get(name = 'operational department')
        saler = OADepartment.objects.get(name = 'saler department')
        hr = OADepartment.objects.get(name = 'HR department',)
        finance = OADepartment.objects.get(name = 'finance department')


        # All the members of the board of directors are considered superusers.
        Tom = OAUser.objects.create_superuser(email = 'Tom@gmail.com' , realname = 'Tom', password = '111111',department = boarder)
        #jack
        Jack = OAUser.objects.create_superuser(email = 'Jack@gmail.com' , realname = 'Jack', password = '111111',department = boarder)
        #David
        David = OAUser.objects.create_user(email='David@gmail.com', realname='David', password='111111',department=developer)
        #Sean
        Sean = OAUser.objects.create_user(email='Sean@gmail.com', realname='Sean', password='111111',department= operator)
        #Bob
        Bob = OAUser.objects.create_user(email='Bob@gmail.com', realname='Bob', password='111111',department=hr)
        #John
        John = OAUser.objects.create_user(email='John@gmail.com', realname='John', password='111111',department=finance)
        # Tim
        Tim = OAUser.objects.create_user(email='Tim@gmail.com', realname='Tim', password='111111',department=saler)

        # Assign a leader and manager to the department
        #Tom:boarder  operator saler
        #Jack:hr finance
        boarder.leader=Tom
        boarder.manager=None

        developer.leader=David
        developer.manager=Tom

        operator.leader=Sean
        operator.manager=Tom

        saler.leader=Tim
        saler.manager=Tom

        hr.leader=John
        hr.manager=Jack

        finance.leader=Bob
        finance.manager=Jack

        boarder.save()
        developer.save()
        operator.save()
        saler.save()
        hr.save()
        finance.save()

        self.stdout.write("Initial user creation was successful.")



