from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.contrib import messages
from django.core.paginator import Paginator
import csv
import json

from .models import Idea, Quadrante, Settore, TecnologiaAI, Like, User
from .forms import IdeaForm, IdeaFilterForm, UserRegistrationForm

def home(request):
    """Vista per la homepage con visualizzazione a cluster per quadranti"""
    quadranti = Quadrante.objects.all()
    for quadrante in quadranti:
        quadrante.idee_count = quadrante.idee.count()
        quadrante.idee_top = quadrante.idee.annotate(likes_count=Count('likes')).order_by('-likes_count')[:3]
    
    return render(request, 'ideas/home.html', {'quadranti': quadranti})

def idea_list(request):
    """Vista per l'elenco delle idee con filtri e ordinamento"""
    ideas = Idea.objects.all().annotate(likes_count=Count('likes'))
    
    # Applicazione filtri
    filter_form = IdeaFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['target']:
            ideas = ideas.filter(target=filter_form.cleaned_data['target'])
        if filter_form.cleaned_data['settore']:
            ideas = ideas.filter(settori=filter_form.cleaned_data['settore'])
        if filter_form.cleaned_data['tecnologia']:
            ideas = ideas.filter(tecnologie=filter_form.cleaned_data['tecnologia'])
        if filter_form.cleaned_data['min_fattibilita']:
            ideas = ideas.filter(fattibilita_tecnica__gte=filter_form.cleaned_data['min_fattibilita'])
        if filter_form.cleaned_data['min_monetizzazione']:
            ideas = ideas.filter(potenziale_monetizzazione__gte=filter_form.cleaned_data['min_monetizzazione'])
        
        # Ordinamento
        if filter_form.cleaned_data['ordinamento']:
            order_by = filter_form.cleaned_data['ordinamento']
            if order_by == 'likes':
                # Già annotato con likes_count
                ideas = ideas.order_by('-likes_count')
            elif order_by == 'data_creazione':
                ideas = ideas.order_by('-data_creazione')
            else:
                # Per altri campi, ordina in modo decrescente se sono valutazioni
                if order_by in ['fattibilita_tecnica', 'potenziale_monetizzazione', 'competitivita_mercato', 'impatto_utente']:
                    ideas = ideas.order_by(f'-{order_by}')
                else:
                    ideas = ideas.order_by(order_by)
    
    # Paginazione
    paginator = Paginator(ideas, 10)  # 10 idee per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ideas/idea_list.html', {
        'page_obj': page_obj,
        'filter_form': filter_form
    })

def idea_detail(request, pk):
    """Vista per i dettagli di un'idea"""
    idea = get_object_or_404(Idea, pk=pk)
    
    # Controlla se l'utente ha messo like
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(utente=request.user, idea=idea).exists()
    
    # Idee simili (stesso quadrante o settori)
    idee_simili = Idea.objects.filter(quadrante=idea.quadrante).exclude(pk=idea.pk)[:3]
    
    return render(request, 'ideas/idea_detail.html', {
        'idea': idea,
        'user_liked': user_liked,
        'idee_simili': idee_simili
    })

@login_required
def idea_create(request):
    """Vista per la creazione di una nuova idea"""
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.creatore = request.user
            idea.is_originale = False  # Nuove idee aggiunte dagli utenti
            idea.save()
            
            # Salva le relazioni many-to-many
            form.save_m2m()
            
            messages.success(request, 'Idea creata con successo!')
            return redirect('ideas:idea_detail', pk=idea.pk)
    else:
        form = IdeaForm()
    
    return render(request, 'ideas/idea_form.html', {'form': form})

@login_required
def idea_like(request, pk):
    """Vista per mettere/togliere like a un'idea"""
    idea = get_object_or_404(Idea, pk=pk)
    user = request.user
    
    # Controlla se l'utente ha già messo like
    like_exists = Like.objects.filter(utente=user, idea=idea).exists()
    
    if request.method == 'POST':
        if like_exists:
            # Rimuovi il like
            Like.objects.filter(utente=user, idea=idea).delete()
            user.likes_disponibili += 1
            user.save()
            messages.success(request, 'Like rimosso con successo!')
        else:
            # Controlla se l'utente ha like disponibili
            if user.likes_disponibili > 0:
                # Aggiungi il like
                Like.objects.create(utente=user, idea=idea)
                user.likes_disponibili -= 1
                user.save()
                messages.success(request, 'Like aggiunto con successo!')
            else:
                messages.error(request, 'Hai esaurito i like disponibili (massimo 5)!')
        
        # Se è una richiesta AJAX, restituisci JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'likes_count': idea.likes.count(),
                'user_liked': not like_exists if user.likes_disponibili > 0 else like_exists,
                'likes_disponibili': user.likes_disponibili
            })
        
        return redirect('ideas:idea_detail', pk=idea.pk)
    
    # Se non è POST, reindirizza alla pagina di dettaglio
    return redirect('ideas:idea_detail', pk=idea.pk)

def quadrante_list(request):
    """Vista per l'elenco dei quadranti"""
    quadranti = Quadrante.objects.all()
    for quadrante in quadranti:
        quadrante.idee_count = quadrante.idee.count()
    
    return render(request, 'ideas/quadrante_list.html', {'quadranti': quadranti})

def quadrante_detail(request, pk):
    """Vista per i dettagli di un quadrante e le sue idee"""
    quadrante = get_object_or_404(Quadrante, pk=pk)
    ideas = quadrante.idee.all().annotate(likes_count=Count('likes'))
    
    # Paginazione
    paginator = Paginator(ideas, 10)  # 10 idee per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ideas/quadrante_detail.html', {
        'quadrante': quadrante,
        'page_obj': page_obj
    })

@login_required
def export_ideas(request):
    """Vista per esportare le idee selezionate in CSV"""
    if request.method == 'POST':
        idea_ids = request.POST.getlist('idea_ids')
        ideas = Idea.objects.filter(id__in=idea_ids)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="idee_startup_ai.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nome', 'Descrizione', 'Problema Risolto', 'Target', 'UVP', 
                         'Settori', 'Tecnologie', 'Modello Revenue', 'Tempo MVP',
                         'Fattibilità Tecnica', 'Potenziale Monetizzazione', 
                         'Competitività Mercato', 'Impatto Utente', 'Quadrante'])
        
        for idea in ideas:
            writer.writerow([
                idea.nome,
                idea.descrizione,
                idea.problema_risolto,
                idea.get_target_display(),
                idea.unique_value_proposition,
                ', '.join(s.nome for s in idea.settori.all()),
                ', '.join(t.nome for t in idea.tecnologie.all()),
                idea.modello_revenue,
                idea.tempo_mvp,
                idea.fattibilita_tecnica,
                idea.potenziale_monetizzazione,
                idea.competitivita_mercato,
                idea.impatto_utente,
                str(idea.quadrante)
            ])
        
        return response
    
    # Se non è POST, mostra la pagina di selezione delle idee
    ideas = Idea.objects.all().annotate(likes_count=Count('likes')).order_by('-likes_count')
    return render(request, 'ideas/export_ideas.html', {'ideas': ideas})

@login_required
def user_profile(request):
    """Vista per il profilo utente"""
    user = request.user
    liked_ideas = Idea.objects.filter(likes__utente=user)
    
    return render(request, 'ideas/user_profile.html', {
        'user': user,
        'liked_ideas': liked_ideas
    })

def register(request):
    """Vista per la registrazione di un nuovo utente"""
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Crea un nuovo oggetto utente ma non lo salva ancora
            new_user = user_form.save(commit=False)
            # Imposta la password
            new_user.set_password(user_form.cleaned_data['password'])
            # Salva l'oggetto User
            new_user.save()
            
            messages.success(request, 'Registrazione completata con successo! Ora puoi accedere.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'user_form': user_form})
