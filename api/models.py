from django.db import models

from django.contrib.auth.models import User


class JobCard(models.Model):

    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobcard")

    customer_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    email = models.CharField(max_length=200, null=True, blank=True)

    vehicle_num = models.CharField(max_length=200)

    kilometers = models.CharField(max_length=100)

    status_options = (
        ("Open", "Open"),
        ("Completed", "Complete"),
        ("Cancelled", "Cancelled")
    )   

    status = models.CharField(max_length=100, choices=status_options, default="Open")

    remark = models.CharField(max_length=250, null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.advisor.first_name


class Job(models.Model):

    job_card_object = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name="job")

    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="advisor")
    
    title = models.CharField(max_length=200)

    description = models.TextField(null=True)

    amount = models.PositiveIntegerField()

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.advisor.first_name

    