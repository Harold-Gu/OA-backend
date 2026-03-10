from django.core.management.base import BaseCommand
from oaauth.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        # init data of department
        boarder = OADepartment.objects.create(name = 'Board Department', intro = 'Board Department')
        developer = OADepartment.objects.create(name = 'product development department', intro = 'Product design, technology development')
        operator = OADepartment.objects.create(name = 'operational department', intro = 'Customer operation, product operation')
        saler = OADepartment.objects.create(name = 'saler department', intro = 'promoting products')
        hr = OADepartment.objects.create(name = 'HR department', intro = 'Employee recruitment, employee training, employee assessment')
        finance = OADepartment.objects.create(name = 'finance department', intro = 'Financial statements, financial auditing')
        self.stdout.write('Department data initialization was successful.')

