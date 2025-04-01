from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_registrazione = models.DateTimeField(auto_now_add=True)
    likes_disponibili = models.IntegerField(default=5)  # Ogni utente ha 5 like disponibili
    
    def __str__(self):
        return f"{self.nome} {self.cognome}"

class Quadrante(models.Model):
    ASSE_X_CHOICES = [
        ('automazione', 'Automazione e orchestrazione'),
        ('creazione', 'Creazione e interazione'),
    ]
    
    ASSE_Y_CHOICES = [
        ('pratico', 'Pratico e utilitaristico'),
        ('sperimentale', 'Sperimentale e creativo'),
    ]
    
    asse_x = models.CharField(max_length=20, choices=ASSE_X_CHOICES)
    asse_y = models.CharField(max_length=20, choices=ASSE_Y_CHOICES)
    nome = models.CharField(max_length=100)
    descrizione = models.TextField()
    
    class Meta:
        unique_together = ('asse_x', 'asse_y')
    
    def __str__(self):
        return f"{self.get_asse_x_display()} / {self.get_asse_y_display()}"

class Settore(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descrizione = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class TecnologiaAI(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descrizione = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class Idea(models.Model):
    TARGET_CHOICES = [
        ('B2B', 'B2B'),
        ('B2C', 'B2C'),
        ('B2B/B2C', 'B2B/B2C'),
    ]
    
    nome = models.CharField(max_length=200)
    descrizione = models.TextField()
    problema_risolto = models.TextField()
    target = models.CharField(max_length=10, choices=TARGET_CHOICES)
    unique_value_proposition = models.TextField()
    settori = models.ManyToManyField(Settore, related_name='idee')
    tecnologie = models.ManyToManyField(TecnologiaAI, related_name='idee')
    modello_revenue = models.TextField()
    tempo_mvp = models.CharField(max_length=50)  # es. "3-4 mesi"
    
    # Valutazioni
    fattibilita_tecnica = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    potenziale_monetizzazione = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    competitivita_mercato = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    impatto_utente = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Relazioni
    quadrante = models.ForeignKey(Quadrante, on_delete=models.CASCADE, related_name='idee')
    creatore = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='idee_create')
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    # Flag per distinguere idee originali da quelle generate
    is_originale = models.BooleanField(default=True)
    
    def count_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.nome

class Like(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='likes')
    data_creazione = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('utente', 'idea')  # Un utente può mettere like a un'idea una sola volta
    
    def __str__(self):
        return f"{self.utente} likes {self.idea}"