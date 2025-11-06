# --- EXERCICE 2 : NETTOYAGE DU BRUIT ET IMPACT VISUEL ---

# --- CONTEXTE ---
# Objectif : Apprendre à nettoyer un texte en éliminant les "stopwords" (mots courants sans signification sémantique)
# et visualiser de manière frappante comment ce nettoyage change l'analyse de fréquence, permettant
# aux mots véritablement importants d'émerger.
#
# Que sont les Stopwords ? Ce sont des mots comme 'le', 'et', 'ou', 'de', qui sont extrêmement fréquents
# mais ne nous disent rien sur le thème ou le sentiment d'un texte. Ce sont les "bruits" du langage.

# --- IMPORTATIONS ---
import re
from collections import Counter
import matplotlib.pyplot as plt

# --- CORPUS ET STOPWORDS ---
corpus = [
    "Le premier lundi du mois d'avril 1625, le bourg de Meung,",
    "où naquit l'auteur du Roman de la Rose, semblait être dans",
    "une révolution aussi complète que si les Huguenots étaient venus",
    "faire une seconde Rochelle.",
    "Beaucoup de bourgeois, voyant les femmes fuir par la Grand-Rue,",
    "entendant les enfants crier sur le seuil des portes,",
    "se hâtaient de revêtir leur cuirasse et, armés d'un mousquet",
    "ou d'une hallebarde, se dirigeaient vers l'auberge du Franc-Meurier,",
    "devant laquelle s'amassait une foule compacte,",
    "chaque fois plus nombreuse et bruyante.",
    "En ces temps les émeutes étaient fréquentes,",
    "et peu de jours s'écoulaient sans qu'une ville",
    "n'enregistrât dans ses annales un de ces événements.",
    "Les seigneurs se faisaient la guerre entre eux ; le roi faisait la guerre au cardinal ;",
    "les Espagnols faisaient la guerre au roi.",
    "Puis, outre ces guerres sourdes ou publiques, secrètes ou patentes,",
    "il y avait les voleurs, les mendiants, les Huguenots, les loups",
    "et les laquais, qui faisaient la guerre à tout le monde.",
    "Les bourgeois s'armaient toujours contre les voleurs,",
    "contre les loups, contre les laquais, souvent contre les seigneurs"
]

# Liste de stopwords courants en français.
stopwords_fr = set([
    'de', 'la', 'le', 'et', 'à', 'les', 'des', 'l', 's', 'd', 'en', 'un', 'du', 'une', 'que', 'dans', 'pour', 'qui', 'au', 'par', 'avec', 'sur', 'est', 'il', 'elle', 'ont', 'ces', 'dans', 'son', 'sa', 'se', 'ses', 'ce', 'cette', 'pas', 'plus', 'tout', 'comme', 'mais', 'ou', 'où', 'y', 'sont', 'aussi', 'bien', 'fait', 'faire', 'avait', 'étaient', 'être', 'avoir', 'peu', 'sans', 'si', 'tous', 'tout', 'toute', 'trop', 'très', 'vers', 'voient'
])

# --- TRAITEMENT ---

# Fonction pour traiter et nettoyer le texte
def traiter_et_compter(texte, stopwords=None):
    """Prend un bloc de texte, le normalise, le tokenise et optionnellement supprime les stopwords."""
    texte_minuscule = texte.lower()
    mots = re.findall(r'\b\w+\b', texte_minuscule)
    if stopwords:
        mots = [mot for mot in mots if mot not in stopwords]
    return Counter(mots)

# 1. Analyse SANS nettoyage (Nous répétons l'étape de l'exercice 1 pour comparer)
print("Étape 1 : Analyse des fréquences SANS nettoyer le texte...")
tout_texte = ' '.join(corpus)
comptes_mots_sans_nettoyage = traiter_et_compter(tout_texte)
top_12_sans_nettoyage = comptes_mots_sans_nettoyage.most_common(12)
print("Top 12 mots (sans nettoyage):", top_12_sans_nettoyage)

# 2. Analyse AVEC nettoyage
print("\nÉtape 2 : Analyse des fréquences AVEC nettoyage des stopwords...")
comptes_mots_avec_nettoyage = traiter_et_compter(tout_texte, stopwords=stopwords_fr)
top_12_avec_nettoyage = comptes_mots_avec_nettoyage.most_common(12)
print("Top 12 mots (avec nettoyage):", top_12_avec_nettoyage)


# --- VISUALISATION COMPARATIVE ---

print("\nGénération des graphiques comparatifs...")

# Déballons les résultats pour les deux graphiques
mots_sans, comptes_sans = zip(*top_12_sans_nettoyage)
mots_avec, comptes_avec = zip(*top_12_avec_nettoyage)

# Créons une figure avec deux sous-graphiques (l'un à côté de l'autre)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Graphique 1 : Sans Nettoyage
ax1.bar(mots_sans, comptes_sans, color='#ff9999')
ax1.set_title('Fréquences AVANT le Nettoyage', fontsize=16)
ax1.set_xlabel('Mots')
ax1.set_ylabel('Fréquence')
ax1.tick_params(axis='x', rotation=45)

# Graphique 2 : Avec Nettoyage
ax2.bar(mots_avec, comptes_avec, color='#99ff99')
ax2.set_title('Fréquences APRÈS le Nettoyage', fontsize=16)
ax2.set_xlabel('Mots')
ax2.set_ylabel('Fréquence')
ax2.tick_params(axis='x', rotation=45)

# Titre général pour toute la figure
fig.suptitle("Impact de l'Élimination des Stopwords", fontsize=20)

# Ajustons la mise en page et affichons
plt.tight_layout(rect=[0, 0, 1, 0.96]) # Ajustement pour le super-titre
plt.show()

print("\n--- FIN DE L'EXERCICE 2 ---")
print("Observation : Le changement est radical ! Le graphique de droite révèle les mots qui apportent véritablement du sens :")
print("Maintenant nous pouvons voir les termes clés de la narration historique des Trois Mousquetaires.")