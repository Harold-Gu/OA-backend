from django.db import models
from django.contrib.auth import get_user_model

OAUser = get_user_model()


class AbsentStatusChoices(models.IntegerChoices):
    # in examination and approval
    AUDITING = 1
    # pass the audit
    PASS = 2
    # Audit rejection
    REJECT = 3


class AbsentType(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)


class Absent(models.Model):
    # 1. title
    title = models.CharField(max_length=200)
    # 2. Details of the leave application
    request_content = models.TextField()
    # 3. Type of leave (sick leave, marriage leave)
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE, related_name='absents', related_query_name='absents')
    # If in a model, there are multiple fields that reference the same model through foreign keys, then the related_name attribute must be specified with different values.
    # 4. initiator
    requester = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='my_absents', related_query_name='my_absents')
    # 5. Approver (can be empty)
    responder = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='sub_absents', related_query_name='sub_absents', null=True)
    # 6. status
    status = models.IntegerField(choices=AbsentStatusChoices, default=AbsentStatusChoices.AUDITING)
    # 7. Start date of leave application
    start_date = models.DateField()
    # 8. End date of leave application
    end_date = models.DateField()
    # 9. Leave application submission time
    create_time = models.DateTimeField(auto_now_add=True)
    # 10. Approval response content
    response_content = models.TextField(blank=True)

    class Meta:
        ordering = ('-create_time', )