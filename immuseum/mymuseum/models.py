from django.db import models

class AdminImmuseum(models.Model):
    admin_id = models.AutoField(primary_key=True)
    mobile_no = models.CharField(max_length=20, null=True)
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True)
    status_flag = models.IntegerField(default=1)

class UserDetails(models.Model):
    id = models.AutoField(primary_key=True)
    mobile_no = models.CharField(max_length=20, null=True)
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True)
    account_no = models.CharField(max_length=50, null=True)
    ifsc = models.CharField(max_length=20, null=True)
    vpa = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=255)
    subscribers = models.ManyToManyField(
        'self',
        through='Subscribers',
        through_fields=('creator', 'subscribers'),
        related_name='subscriptions_to',
        symmetrical=False,
        blank=True
    )
    subscribed_to = models.ManyToManyField(
        'self',
        through='Subscribers',
        through_fields=('creator', 'subscribed_to'),
        related_name='subscribers_of',
        symmetrical=False,
        blank=True
    )
    subscribers_count = models.IntegerField(null=True)
    status_flag = models.IntegerField(default=1)

    def __str__(self):
        return f"User ID: {self.id}, Mobile No: {self.mobile_no}"

    
class UserImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    image = models.ImageField()
    user_details = models.ManyToManyField(UserDetails, related_name='images')
    image_desc = models.TextField(null=True)
    image_likes = models.IntegerField(null=True)
    status_flag = models.IntegerField(default=1)

class UserComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    image_id = models.ForeignKey(UserImages, on_delete=models.CASCADE)
    commenter_user_id = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    status_flag = models.IntegerField(default=1)

class Subscribers(models.Model):
    subscription_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(UserDetails, related_name='creator_subscriptions', on_delete=models.CASCADE)
    subscribers = models.ForeignKey(UserDetails, related_name='subscriber_subscriptions', on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(UserDetails, related_name='subscriber_to_subscriptions', on_delete=models.CASCADE)
    status_flag = models.IntegerField(default=1)
