from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Idea, Settore, TecnologiaAI

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Conferma password', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'nome', 'cognome', 'email']
        
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Le password non corrispondono.')
        return cd['password2']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email già in uso. Utilizzare un\'altra email.')
        return email

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['nome', 'descrizione', 'problema_risolto', 'target', 
                  'unique_value_proposition', 'settori', 'tecnologie', 
                  'modello_revenue', 'tempo_mvp', 'quadrante',
                  'fattibilita_tecnica', 'potenziale_monetizzazione', 
                  'competitivita_mercato', 'impatto_utente']
        widgets = {
            'descrizione': forms.Textarea(attrs={'rows': 4}),
            'problema_risolto': forms.Textarea(attrs={'rows': 4}),
            'unique_value_proposition': forms.Textarea(attrs={'rows': 4}),
            'modello_revenue': forms.Textarea(attrs={'rows': 3}),
            'settori': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'tecnologie': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'fattibilita_tecnica': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'potenziale_monetizzazione': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'competitivita_mercato': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'impatto_utente': forms.Select(choices=[(i, i) for i in range(1, 6)]),
        }

class IdeaFilterForm(forms.Form):
    target = forms.ChoiceField(
        choices=[('', 'Tutti')] + Idea.TARGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    settore = forms.ModelChoiceField(
        queryset=Settore.objects.all(),
        required=False,
        empty_label="Tutti i settori",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tecnologia = forms.ModelChoiceField(
        queryset=TecnologiaAI.objects.all(),
        required=False,
        empty_label="Tutte le tecnologie",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_fattibilita = forms.ChoiceField(
        choices=[('', 'Qualsiasi')] + [(i, i) for i in range(1, 6)],
        required=False,
        label="Fattibilità tecnica minima",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_monetizzazione = forms.ChoiceField(
        choices=[('', 'Qualsiasi')] + [(i, i) for i in range(1, 6)],
        required=False,
        label="Potenziale di monetizzazione minimo",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_originale = forms.ChoiceField(
        choices=[('', 'Tutte'), ('True', 'Solo originali'), ('False', 'Solo nuove')],
        required=False,
        label="Tipo di idea",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ordinamento = forms.ChoiceField(
        choices=[
            ('nome', 'Nome (A-Z)'),
            ('-nome', 'Nome (Z-A)'),
            ('-likes_count', 'Più popolari'),
            ('-fattibilita_tecnica', 'Più fattibili'),
            ('-potenziale_monetizzazione', 'Maggior potenziale di monetizzazione'),
            ('-impatto_utente', 'Maggior impatto per l\'utente')
        ],
        required=False,
        initial='-likes_count',
        label="Ordina per",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
