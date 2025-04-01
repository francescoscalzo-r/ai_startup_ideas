import unittest
from django.test import TestCase, Client
from django.urls import reverse
from ideas.models import User, Idea, Quadrante, Settore, TecnologiaAI, Like

class TestAuthentication(TestCase):
    def setUp(self):
        # Crea un utente di test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            nome='Test',
            cognome='User'
        )
        
    def test_login(self):
        # Test del login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect dopo login
        
    def test_register(self):
        # Test della registrazione
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'nome': 'New',
            'cognome': 'User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect dopo registrazione
        self.assertTrue(User.objects.filter(username='newuser').exists())

class TestLikeSystem(TestCase):
    def setUp(self):
        # Crea un utente di test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            nome='Test',
            cognome='User'
        )
        
        # Crea un quadrante
        self.quadrante = Quadrante.objects.create(
            nome='Test Quadrante',
            asse_x='automazione',
            asse_y='pratico',
            descrizione='Quadrante di test'
        )
        
        # Crea un'idea
        self.idea = Idea.objects.create(
            nome='Test Idea',
            descrizione='Descrizione di test',
            problema_risolto='Problema di test',
            target='B2B',
            unique_value_proposition='UVP di test',
            modello_revenue='Modello di test',
            tempo_mvp='1 mese',
            fattibilita_tecnica=4,
            potenziale_monetizzazione=4,
            competitivita_mercato=3,
            impatto_utente=5,
            quadrante=self.quadrante,
            creatore=self.user
        )
        
    def test_like_idea(self):
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Metti like all'idea
        response = self.client.post(reverse('ideas:idea_like', args=[self.idea.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect dopo like
        
        # Verifica che il like sia stato aggiunto
        self.assertTrue(Like.objects.filter(utente=self.user, idea=self.idea).exists())
        
        # Verifica che i like disponibili siano diminuiti
        self.user.refresh_from_db()
        self.assertEqual(self.user.likes_disponibili, 4)
        
        # Rimuovi il like
        response = self.client.post(reverse('ideas:idea_like', args=[self.idea.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect dopo rimozione like
        
        # Verifica che il like sia stato rimosso
        self.assertFalse(Like.objects.filter(utente=self.user, idea=self.idea).exists())
        
        # Verifica che i like disponibili siano aumentati
        self.user.refresh_from_db()
        self.assertEqual(self.user.likes_disponibili, 5)

class TestExploration(TestCase):
    def setUp(self):
        # Crea un utente di test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            nome='Test',
            cognome='User'
        )
        
        # Crea un quadrante
        self.quadrante = Quadrante.objects.create(
            nome='Test Quadrante',
            asse_x='automazione',
            asse_y='pratico',
            descrizione='Quadrante di test'
        )
        
        # Crea un'idea
        self.idea = Idea.objects.create(
            nome='Test Idea',
            descrizione='Descrizione di test',
            problema_risolto='Problema di test',
            target='B2B',
            unique_value_proposition='UVP di test',
            modello_revenue='Modello di test',
            tempo_mvp='1 mese',
            fattibilita_tecnica=4,
            potenziale_monetizzazione=4,
            competitivita_mercato=3,
            impatto_utente=5,
            quadrante=self.quadrante,
            creatore=self.user
        )
        
    def test_idea_list(self):
        # Test della lista delle idee
        response = self.client.get(reverse('ideas:idea_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_idea_detail(self):
        # Test del dettaglio dell'idea
        response = self.client.get(reverse('ideas:idea_detail', args=[self.idea.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Idea')
        self.assertContains(response, 'Descrizione di test')
        
    def test_quadrante_list(self):
        # Test della lista dei quadranti
        response = self.client.get(reverse('ideas:quadrante_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Quadrante')
        
    def test_quadrante_detail(self):
        # Test del dettaglio del quadrante
        response = self.client.get(reverse('ideas:quadrante_detail', args=[self.quadrante.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Quadrante')
        self.assertContains(response, 'Test Idea')

if __name__ == '__main__':
    unittest.main()
