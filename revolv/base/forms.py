import time
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError

from models import RevolvUserProfile


class SignupForm(UserCreationForm):
    """
    Form for a user to sign up for an account. Note that we manually clean
    and save the first and last name of the user and their email, since
    django.contrib.auth.forms.UserCreationForm does not do that by default.
    """
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")
    subscribed_to_newsletter = forms.BooleanField(initial=True, required=False, label="Subscribe me to the RE-volv Newsletter.", help_text="Subscribe me to the RE-volv Newsletter")
    zipcode = forms.CharField(label="Zipcode", max_length=5)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields.pop("username")

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("This email already used")
        return data


    def save(self, commit=True):
        """
        On save of the form, update the associated user profile with first and
        last names.
        """
        user = super(SignupForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.username = user.first_name[0:15] + user.last_name[0:1] + str(int(time.time() * 1000))[6:13]
        if commit:
            user.save()
            user.revolvuserprofile.subscribed_to_newsletter = self.cleaned_data["subscribed_to_newsletter"]
            user.revolvuserprofile.zipcode = self.cleaned_data["zipcode"]
            user.revolvuserprofile.save()
        return user

    def ensure_authenticated_user(self):
        """
        Return the User model related to this valid form, or raise an
        IntegrityError if it does not exist (because it should).
        """
        username = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password2')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            return user
        raise IntegrityError(
            "User model could not be saved during signup process."
        )


class RevolvUserProfileForm(forms.ModelForm):
    class Meta:
        model = RevolvUserProfile
        fields = ['subscribed_to_newsletter', 'subscribed_to_updates','subscribed_to_repayment_notifications']


class UpdateUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")


class SignInForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")

