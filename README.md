# Klare Methode

Eine Django-basierte Coaching-Plattform zur Unterstützung von persönlicher Entwicklung und Zielsetzung. Das Projekt bietet Funktionen wie Vision Boards, Zielverfolgung und Lebensrad-Bewertungen.

## Funktionen

- **Vision Boards**: Erstellen und verwalten Sie Ihre Vision Boards mit Bildern und Elementen.
- **Zielverfolgung**: Setzen und überwachen Sie Ihre persönlichen Ziele.
- **Lebensrad-Bewertung**: Bewerten Sie verschiedene Lebensbereiche für eine ausgewogene Entwicklung.
- **Benutzerverwaltung**: Registrierung, Anmeldung und Dashboard für Benutzer.

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Django 4.x
- PostgreSQL oder SQLite (SQLite ist standardmäßig konfiguriert)

### Schritte

1. **Repository klonen**:
   ```bash
   git clone https://github.com/IhrBenutzername/klare-methode.git
   cd klare-methode
   ```

2. **Virtuelle Umgebung erstellen und aktivieren**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Auf Windows: venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Datenbank migrieren**:
   ```bash
   python manage.py migrate
   ```

5. **Entwicklungsserver starten**:
   ```bash
   python manage.py runserver
   ```

   Die Anwendung ist nun unter `http://127.0.0.1:8000/` verfügbar.

## Nutzung

- Registrieren Sie sich als neuer Benutzer oder melden Sie sich an.
- Erstellen Sie Ihr Vision Board und fügen Sie Elemente hinzu.
- Setzen Sie Ziele und verfolgen Sie Ihren Fortschritt.
- Nutzen Sie die Lebensrad-Bewertung für Selbstreflexion.

## Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Fork des Repositories und reichen Sie Pull Requests ein.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` für Details.

## Kontakt

Für Fragen oder Feedback: [Ihre E-Mail oder Kontaktinformationen]