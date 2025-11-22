from allauth.account.forms import SignupForm
from django import forms

class SignupWithPhoneForm(SignupForm):
    phone = forms.CharField(max_length=40, required=False, label="Telefon")

    def save(self, request):
        user = super().save(request)
        # spremi u profil
        prof = user.profile  # thanks to signal
        prof.phone = self.cleaned_data.get("phone","")
        prof.save()
        return user
