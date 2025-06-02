from django import forms
from .models import Project
from django.utils import timezone

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'budget', 'deadline', 'skills_required']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline < timezone.now().date():
            raise forms.ValidationError("La date limite ne peut pas être dans le passé.")
        return deadline