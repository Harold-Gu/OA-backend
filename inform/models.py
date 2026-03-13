from django.db import models
from oaauth.models import OAUser, OADepartment


class Inform(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    # If the department_ids uploaded at the front end contain the number 0, such as [0], then it is considered that this notification is visible to all departments.
    public = models.BooleanField(default=False)
    author = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='informs', related_query_name='informs')
    # departments: Used during serialization. When uploading from the front end, the department ID is provided. We obtain it through department_ids.
    departments = models.ManyToManyField(OADepartment, related_name='informs', related_query_name='informs')

    class Meta:
        ordering = ('-create_time', )


class InformRead(models.Model):
    inform = models.ForeignKey(Inform, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    user = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    read_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # The combined data of "inform" and "user" must be unique.
        unique_together = ('inform', 'user')
