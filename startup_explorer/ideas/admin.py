from django.contrib import admin
from .models import User, Quadrante, Settore, TecnologiaAI, Idea, Like

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'cognome', 'email', 'likes_disponibili')
    search_fields = ('username', 'nome', 'cognome', 'email')

@admin.register(Quadrante)
class QuadranteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'asse_x', 'asse_y')
    list_filter = ('asse_x', 'asse_y')

@admin.register(Settore)
class SettoreAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(TecnologiaAI)
class TecnologiaAIAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'target', 'quadrante', 'fattibilita_tecnica', 'potenziale_monetizzazione', 'is_originale')
    list_filter = ('target', 'quadrante', 'is_originale', 'settori', 'tecnologie')
    search_fields = ('nome', 'descrizione', 'problema_risolto')
    filter_horizontal = ('settori', 'tecnologie')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('utente', 'idea', 'data_creazione')
    list_filter = ('data_creazione',)
