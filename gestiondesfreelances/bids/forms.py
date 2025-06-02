from django import forms
from .models import Bid

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'delivery_time', 'proposal']
        widgets = {
            'proposal': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Décrivez votre approche pour ce projet...'
            }),
            'amount': forms.NumberInput(attrs={
                'min': 0,
                'step': 0.01
            }),
            'delivery_time': forms.NumberInput(attrs={
                'min': 1
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.freelancer = kwargs.pop('freelancer', None)
        super().__init__(*args, **kwargs)
        
        if self.project and self.project.budget:
            self.fields['amount'].widget.attrs['max'] = self.project.budget * 2
            self.fields['amount'].help_text = f"Budget client: {self.project.budget} €"
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.project and amount > self.project.budget * 2:
            raise forms.ValidationError(
                f"Le montant ne peut pas dépasser le double du budget client ({self.project.budget * 2} €)"
            )
        return amount
    
    def clean_delivery_time(self):
        delivery_time = self.cleaned_data.get('delivery_time')
        if delivery_time < 1:
            raise forms.ValidationError("Le délai doit être d'au moins 1 jour")
        return delivery_time

class BidStatusForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('accept', 'Accepter'),
            ('reject', 'Rejeter')
        ],
        widget=forms.RadioSelect
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Message optionnel...'
        })
    )