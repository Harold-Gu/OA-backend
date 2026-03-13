from django.core.management.base import BaseCommand
from absent.models import AbsentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        absent_types = ["Personal leave", "sick leave", "work-related injury leave", "marriage leave", "bereavement leave", "maternity leave", "family visit leave", "official leave", "annual leave"]
        absents = []
        for absent_type in absent_types:
            absents.append(AbsentType(name=absent_type))
        AbsentType.objects.bulk_create(absents)
        self.stdout.write('Attendance type data initialization successful!')