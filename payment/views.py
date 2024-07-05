from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.shortcuts import get_object_or_404
from .paytm import generate_checksum, verify_checksum
from django.contrib.auth.models import User
from courses.models import CourseModel
from .models import Payment
from django.views.decorators.csrf import csrf_exempt

def initiate_payment(request, user_id, course_id):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=user_id)
        course = get_object_or_404(CourseModel, pk=course_id)
        amount = course.price


        # Create a Payment object
        payment = Payment.objects.create(user=user, course=course, amount=amount)
        merchant_key = settings.PAYTM_SECRET_KEY

        # Construct Paytm parameters
        params = (
            ('MID', settings.PAYTM_MERCHANT_ID),
            ('ORDER_ID', str(payment.order_id)),  # Use a unique identifier for ORDER_ID
            ('CUST_ID', str(payment.user)),
            ('TXN_AMOUNT', (payment.amount)),
            ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
            ('WEBSITE', settings.PAYTM_WEBSITE),
            ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
            ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        )

        paytm_params = dict(params)
        checksum = generate_checksum(paytm_params, merchant_key)

        payment.checksum = checksum
        payment.save()

        paytm_params['CHECKSUMHASH'] = checksum
        print('SENT:', checksum)
        return render(request, 'redirect.html', context=paytm_params)
    else:
       
        return render(request, 'users/payment_details.html')
    












    

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


