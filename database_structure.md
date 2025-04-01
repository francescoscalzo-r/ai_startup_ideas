# Struttura del Database per la Web App di Idee Startup AI

## Panoramica

La struttura del database è progettata per supportare tutte le funzionalità richieste per la web app di esplorazione e valutazione delle idee di startup basate su AI. Il database dovrà gestire:

- Archiviazione delle idee con tutti i loro attributi
- Sistema di autenticazione per gli utenti
- Sistema di votazione (massimo 5 like per utente)
- Visualizzazione a cluster per quadranti
- Filtri dinamici per vari attributi
- Possibilità di aggiungere nuove idee

## Modelli di Dati (Django Models)

### User (Utente)
Estenderemo il modello User di Django per aggiungere campi personalizzati:

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_registrazione = models.DateTimeField(auto_now_add=True)
    likes_disponibili = models.IntegerField(default=5)  # Ogni utente ha 5 like disponibili
    
    def __str__(self):
        return f"{self.nome} {self.cognome}"
```

### Quadrante
```python
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
```

### Settore
```python
class Settore(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descrizione = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome
```

### TecnologiaAI
```python
class TecnologiaAI(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descrizione = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome
```

### Idea
```python
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
```

### Like
```python
class Like(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='likes')
    data_creazione = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('utente', 'idea')  # Un utente può mettere like a un'idea una sola volta
    
    def __str__(self):
        return f"{self.utente} likes {self.idea}"
```

## Relazioni tra i Modelli

1. **User - Idea**: Un utente può creare molte idee (relazione one-to-many)
2. **User - Like**: Un utente può mettere like a molte idee, ma massimo 5 in totale (relazione one-to-many con vincolo)
3. **Idea - Like**: Un'idea può ricevere molti like da utenti diversi (relazione one-to-many)
4. **Quadrante - Idea**: Un quadrante può contenere molte idee (relazione one-to-many)
5. **Settore - Idea**: Un'idea può appartenere a più settori e un settore può essere associato a più idee (relazione many-to-many)
6. **TecnologiaAI - Idea**: Un'idea può utilizzare più tecnologie AI e una tecnologia può essere utilizzata in più idee (relazione many-to-many)

## Vincoli e Logica di Business

1. **Limite di Like**: Ogni utente ha un massimo di 5 like disponibili da assegnare
2. **Unicità dei Like**: Un utente può mettere like a un'idea una sola volta
3. **Validazione Valutazioni**: Tutte le valutazioni (fattibilità, monetizzazione, ecc.) devono essere comprese tra 1 e 5
4. **Quadranti**: Le idee devono essere classificate in uno dei quattro quadranti definiti

## Indici per Ottimizzazione delle Query

Per migliorare le prestazioni delle query più frequenti, verranno creati i seguenti indici:

1. Indice su `Idea.quadrante` per la visualizzazione a cluster
2. Indice su `Like.utente` e `Like.idea` per il conteggio rapido dei like
3. Indice su `Idea.target` per il filtraggio per target
4. Indice su `Idea.fattibilita_tecnica`, `Idea.potenziale_monetizzazione`, ecc. per il filtraggio e l'ordinamento basato su valutazioni

## Considerazioni sulla Migrazione dei Dati

Per popolare inizialmente il database con le idee esistenti e quelle nuove generate:

1. Creare fixture per i quadranti
2. Creare fixture per i settori e le tecnologie AI
3. Importare le idee esistenti e quelle nuove generate
4. Assegnare correttamente le relazioni tra idee, quadranti, settori e tecnologie

Questa struttura del database supporterà tutte le funzionalità richieste per la web app, inclusa la navigazione a cluster, la visualizzazione in elenco con ordinamento, il filtraggio dinamico, l'aggiunta di nuove idee e il sistema di votazione.
