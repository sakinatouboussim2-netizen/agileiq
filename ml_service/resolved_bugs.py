RESOLVED_BUGS = [
    {
        "id": "BUG-001",
        "title": "Crash login avec mot de passe special Firefox",
        "description": "Erreur 500 sur saisie de caracteres Unicode",
        "resolution": "Encoder explicitement le mot de passe en UTF-8 avant le hashage bcrypt.",
        "resolved_at": "2026-03-12",
        "severity_resolved": "major",
    },
    {
        "id": "BUG-002",
        "title": "Login impossible apres mise a jour navigateur",
        "description": "Tokens JWT non reconnus apres changement de version Chrome",
        "resolution": "Desactiver la verification stricte de l iss claim. Regenerer les tokens expires.",
        "resolved_at": "2026-04-05",
        "severity_resolved": "major",
    },
    {
        "id": "BUG-003",
        "title": "Bug authentification email avec accents",
        "description": "Emails contenant des caracteres accentues refuses",
        "resolution": "Normaliser l email en NFC Unicode avant le stockage.",
        "resolved_at": "2026-02-18",
        "severity_resolved": "minor",
    },
    {
        "id": "BUG-004",
        "title": "Export CSV produit fichier vide",
        "description": "Telechargement de CSV ne contient que les en-tetes",
        "resolution": "Corriger le filtre SQL qui excluait tous les tickets.",
        "resolved_at": "2026-04-22",
        "severity_resolved": "major",
    },
    {
        "id": "BUG-005",
        "title": "Notification email non envoyee aux assignes",
        "description": "Les notifications de creation de ticket ne partent pas",
        "resolution": "Augmenter le timeout SMTP de 5s a 30s. Ajouter retry avec backoff.",
        "resolved_at": "2026-03-30",
        "severity_resolved": "major",
    },
    {
        "id": "BUG-006",
        "title": "Lenteur generale sur les requetes complexes",
        "description": "Listes de tickets superieur a 1000 mettent plusieurs secondes",
        "resolution": "Ajouter index PostgreSQL sur project_id et status. Cache Redis TTL 60s.",
        "resolved_at": "2026-05-10",
        "severity_resolved": "minor",
    },
    {
        "id": "BUG-007",
        "title": "Pagination cassee sur la vue calendrier",
        "description": "Le bouton page suivante ne fonctionne pas en mode mois",
        "resolution": "Corriger le calcul d offset qui ignorait le filtre de date.",
        "resolved_at": "2026-04-15",
        "severity_resolved": "minor",
    },
]


def get_all_resolved():
    return RESOLVED_BUGS
