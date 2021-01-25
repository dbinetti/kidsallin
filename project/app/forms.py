# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.core.exceptions import ValidationError

# Local
from .models import Account
from .models import School
from .models import User


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )

class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required fields override
        # self.fields['address'].required = True

    class Meta:
        model = Account
        fields = [
            'name',
            'phone',
            'email',
            'is_public',
            'is_teacher',
            'is_medical',
            'comments',
            'notes',
        ]
        labels = {
            "is_public": "Please Make My Name Public",
            "is_teacher": "I'm an Educator/Staff",
            "is_medical": "I'm a Physician",
        }
        widgets = {
            'comments': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Any respectful, on-topic comments to share publicly? (Optional, Name Must Be Public)',
                    'rows': 5,
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Anything else we should know? (Optional, Private)',
                    'rows': 5,
                }
            )
        }
        help_texts = {
            'name': "Please provide your real name.  Feel free to include your \
            spouse to show your support as a family.  Note that all your information \
            remains private unless you explicity ask to be Public below.",
            'is_public': "Showing your support publicly carries more weight, and \
            encourages others to join.",
            'is_teacher': "This is only shared if you make your name public.",
            'is_medical': "This is only shared if you make your name public.",
        }


    def clean(self):
        cleaned_data = super().clean()
        is_public = cleaned_data.get("is_public")
        comments = cleaned_data.get("comments")

        if comments and not is_public:
            raise ValidationError(
                "Comments are only shared if you make your name public."
            )



class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            'name',
            'nces_id',
            'phone',
            'lat',
            'lon',
        ]


class UserCreationForm(UserCreationFormBase):
    """
    Custom user creation form for Auth0
    """

    # Bypass password requirement
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            'username',
        ]


class UserChangeForm(UserChangeFormBase):
    """
    Custom user change form for Auth0
    """

    class Meta:
        model = User
        fields = [
            'username',
        ]
