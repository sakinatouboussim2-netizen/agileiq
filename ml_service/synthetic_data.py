"""Génère un corpus synthétique de tickets pour entraîner le classifieur."""

EPIC_EXAMPLES = [
    "Refonte complete du module de paiement",
    "Migration de l'architecture vers microservices",
    "Strategie de transformation numerique 2026",
    "Nouvelle plateforme d'integration partenaires",
    "Refonte de l'experience utilisateur",
    "Modernisation du systeme de notifications",
    "Programme de mise en conformite RGPD",
    "Restructuration de la base de donnees clients",
    "Plan de scalabilite pour 100k utilisateurs",
    "Initiative globale de securisation des API",
    "Vision strategique pour le module de reporting",
    "Programme d'amelioration de la performance globale",
    "Refonte architecturale du backoffice",
    "Strategie d'internationalisation multi-pays",
    "Roadmap de migration cloud sur 12 mois",
]

FEATURE_EXAMPLES = [
    "Ajouter un filtre par date sur la liste des projets",
    "Permettre l'export des tickets en CSV",
    "Implementer la connexion via Google OAuth",
    "Afficher un graphique de velocite par sprint",
    "Ajouter un mode sombre a l'interface",
    "Creer une page de profil utilisateur editable",
    "Implementer la pagination sur la liste des bugs",
    "Ajouter des tags personnalises aux tickets",
    "Permettre la duplication d'un ticket en un clic",
    "Creer un raccourci clavier pour creer un ticket",
    "Ajouter une vue Kanban pour les tickets",
    "Implementer la recherche full-text dans les commentaires",
    "Permettre la mention d'utilisateurs dans les commentaires",
    "Ajouter un selecteur de langue dans le menu",
    "Creer un widget de statistiques sur le dashboard",
]

BUG_EXAMPLES = [
    "Crash au login quand le mot de passe contient un emoji",
    "Le bouton supprimer ne fonctionne pas sur Firefox",
    "Erreur 500 lors de l'upload d'un avatar",
    "Les notifications email ne sont pas envoyees",
    "Le filtre par statut ne renvoie aucun resultat",
    "Page blanche apres la creation d'un projet",
    "Le compteur de tickets affiche un mauvais total",
    "L'API retourne 422 sur une requete valide",
    "La barre de progression reste bloquee a 50 pourcent",
    "Probleme d'encodage UTF-8 dans les exports",
    "Le lien de reinitialisation de mot de passe est casse",
    "Erreur de timeout sur les longues requetes",
    "Les images uploadees apparaissent rotation incorrecte",
    "Le tri par date est inverse sur la vue liste",
    "Crash de l'application au scroll rapide",
]


def get_training_data():
    """Retourne (textes, etiquettes) pour entrainer le classifieur."""
    texts = EPIC_EXAMPLES + FEATURE_EXAMPLES + BUG_EXAMPLES
    labels = (
        ["epic"] * len(EPIC_EXAMPLES)
        + ["feature"] * len(FEATURE_EXAMPLES)
        + ["bug"] * len(BUG_EXAMPLES)
    )
    return texts, labels
