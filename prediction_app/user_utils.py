from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_data(user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'last_searched_stock': user.last_searched_stock,
            # Add other user data fields here
        }
        return user_data
    except User.DoesNotExist:
        print("User does not exist")
        return None
