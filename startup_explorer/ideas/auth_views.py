from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm

def register_view(request):
    """Vista migliorata per la registrazione degli utenti"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Crea un nuovo utente ma non lo salva ancora
            new_user = form.save(commit=False)
            # Imposta la password
            new_user.set_password(form.cleaned_data['password'])
            # Salva l'utente
            new_user.save()
            
            # Autenticazione automatica dopo la registrazione
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Benvenuto, {user.nome}! La tua registrazione è stata completata con successo.')
                return redirect('ideas:home')
            else:
                messages.success(request, 'Registrazione completata con successo! Ora puoi accedere.')
                return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'user_form': form})

def login_view(request):
    """Vista migliorata per il login degli utenti"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Benvenuto, {user.nome}! Hai effettuato l\'accesso con successo.')
                # Redirect alla pagina richiesta o alla home
                next_page = request.GET.get('next', 'ideas:home')
                return redirect(next_page)
            else:
                messages.error(request, 'Username o password non validi.')
        else:
            messages.error(request, 'Si è verificato un errore durante l\'accesso. Riprova.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})
