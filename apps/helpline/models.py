from django.db import models
from apps.mauth.models import CustomUser as User

# Create your models here.

class Complaint(models.Model):
    NATURE_CHOICES = (('WITHDRAW', 'WITHDRAW'), ('REPAYMENT', 'REPAYMENT'), ('COMMISSION', 'COMMISSION'))
    STATUS_CHOICES = (('REGISTERED', 'REGISTERED'), ('RESOLVED', 'RESOLVED'))
    MEDIUM_CHOICES = (('EMAIL', 'EMAIL'), ('CALL', 'CALL'))

    def upload_image(instance, filename):
        return f'Complaint/{filename}'

    id = models.AutoField(primary_key=True)
    complaint_id = models.CharField(max_length=255, unique=True, null=True)
    complainant = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    nature = models.CharField(max_length=255, choices=NATURE_CHOICES)
    body = models.CharField(max_length=1000, null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=upload_image, blank=True, null=True)
    medium = models.CharField(max_length=255, choices=MEDIUM_CHOICES, default=MEDIUM_CHOICES[1][1])
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def save(self, *args, **kwargs):
        if Complaint.objects.all().count() == 0:
            self.complaint_id = f'COMPLAINT1'
        else:
            last_object = Complaint.objects.latest('id')#all().order_by('-id')[0]
            self.complaint_id = f'COMPLAINT{last_object + 1}'
        super(Complaint, self).save(*args, **kwargs)
