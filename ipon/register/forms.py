from django import forms
from .models import Ride

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