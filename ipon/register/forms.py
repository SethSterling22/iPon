from django import forms
from .models import Ride
from .models import User
from .models import Payment

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['Start_location', 'End_location', 'Date_Start', 'Date_End']  # Adjust as needed
        widgets = {
            'Date_Start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'Date_End': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_location = cleaned_data.get("Start_location")
        end_location = cleaned_data.get("End_location")
        
        if start_location == end_location:
            raise forms.ValidationError("Start and end locations cannot be the same.")
        
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['License_number', 'Car_Brand', 'Car_Model', 'Car_Year', 'License_plate']
        widgets = {
            'License_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your License Number',
                'id': 'License_number',
                'required': 'required'
            }),
            'Car_Brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Brand',
                'id': 'Car_Brand',
                'required': 'required'
            }),
            'Car_Model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Model',
                'id': 'Car_Model',
                'required': 'required'
            }),
            'Car_Year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the year',
                'id': 'Car_Year',
                'required': 'required'
            }),
            'License_plate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the License plate',
                'id': 'License_plate',
                'required': 'required'
            }),
            'Is_driver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RatingCommentForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = ['Rate', 'comment']  