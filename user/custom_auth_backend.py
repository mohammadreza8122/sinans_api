from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class NumberAndOTPAuthBackend(ModelBackend):
    def authenticate(self, request, number=None, otp=None, password=None, **kwargs):
        User = get_user_model()
        if otp:
            try:
                user = User.objects.get(number=number, otp=otp)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(number=number)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None

        # Perform additional checks if needed before authenticating the user
        # ...

        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
