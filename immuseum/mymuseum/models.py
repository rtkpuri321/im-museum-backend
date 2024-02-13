from django.db import models

class UserDetails(models.Model):
    id = models.AutoField(primary_key=True)
    mobile_no = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, unique=True)  # Add email field
    account_no = models.CharField(max_length=50, null=True)
    ifsc = models.CharField(max_length=20, null=True)
    vpa = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=255)  # Adjust max_length as needed

    def __str__(self):
        return f"User ID: {self.id}, Mobile No: {self.mobile_no}"
