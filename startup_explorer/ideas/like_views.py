from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Idea, Like, User

@login_required
def like_idea(request, pk):
    """
    Vista per gestire i like alle idee.
    Ogni utente può mettere massimo 5 like totali.
    Un utente può mettere un solo like per idea.
    """
    idea = get_object_or_404(Idea, id=pk)
    user = request.user
    
    # Verifica se l'utente ha già messo like a questa idea
    like_exists = Like.objects.filter(utente=user, idea=idea).exists()
    
    if like_exists:
        # Se l'utente ha già messo like, lo rimuove
        Like.objects.filter(utente=user, idea=idea).delete()
        user.likes_disponibili += 1
        user.save()
        message = f'Like rimosso da "{idea.nome}"'
        user_liked = False
    else:
        # Se l'utente non ha ancora messo like, verifica se ha like disponibili
        if user.likes_disponibili > 0:
            # Crea un nuovo like
            Like.objects.create(utente=user, idea=idea)
            user.likes_disponibili -= 1
            user.save()
            message = f'Like aggiunto a "{idea.nome}"'
            user_liked = True
        else:
            # L'utente ha esaurito i like disponibili
            message = 'Hai esaurito i tuoi 5 like disponibili'
            user_liked = False
    
    # Se la richiesta è AJAX, restituisce una risposta JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'likes_count': idea.likes.count(),
            'user_liked': user_liked,
            'likes_disponibili': user.likes_disponibili,
            'message': message
        })
    
    # Altrimenti, mostra un messaggio e reindirizza
    if user_liked:
        messages.success(request, message)
    else:
        messages.info(request, message)
    
    # Reindirizza alla pagina di dettaglio dell'idea o alla pagina precedente
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('ideas:idea_detail', pk=idea.id)
