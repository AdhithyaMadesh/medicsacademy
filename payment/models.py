from django.db import models
from django.contrib.auth.models import User 
from courses .models import CourseModel 
# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel,on_delete=models.CASCADE)
    payment_made_on = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)
    


    def save(self, *args, **kwargs):
        if self.order_id is None and self.payment_made_on and self.id:
            self.order_id = self.payment_made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
    
