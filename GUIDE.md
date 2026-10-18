# Guide de production — @reevesmotiv

Ce dépôt sert à produire et héberger les carrousels Instagram de @reevesmotiv.
Les images sont publiques ici, puis programmées dans Metricool via leurs liens
`https://raw.githubusercontent.com/reevesocaz-droid/reevesmotiv-carrousels/main/<dossier>/slide_XX.png`.

## Ligne éditoriale
Développement personnel en français, ton sobre et profond, tutoiement.
Les formats qui collent au compte (alterner dans la semaine) :
- **Vérités / leçons de vie** en liste : « 7 choses que tu comprendras trop tard », etc. Une idée par slide.
- **Paraboles et mini-histoires** avec une morale : bambou chinois, le jardin hérité, le renard et la foule, le vieux sage et le seau d'eau…
- **Symboles et animaux** : l'aigle, le lion, le loup, l'arbre, la montagne… et la leçon qu'on en tire.
- **Gratitude et valeurs** : les vrais luxes de la vie, ce que l'argent n'achète pas.
- **Entourage et choix** : loyauté, personnes à garder, bonnes décisions, discipline.

Règles :
- 6 à 8 slides. Slide 1 = accroche forte. Dernière slide = conclusion + appel à s'abonner.
- Phrases courtes (15 mots max par slide pour le texte principal), français impeccable (accents, apostrophes, ponctuation).
- Pas de citation attribuée à une personne réelle sans être certain qu'elle est authentique : préférer des formulations originales.
- Pas de contenu religieux, politique ou médical.
- Ne jamais réutiliser un sujet listé dans `SUJETS.md`.

## Légende (champ `text` Metricool)
Titre court + emoji, 3 à 5 phrases qui racontent l'idée, puis une question au lecteur
(« Et toi… ? 👇 »), puis 6 à 9 hashtags de niche en français. Jamais #fyp ni #pourtoi.
Réserve de hashtags : #developpementpersonnel #mindset #leconsdevie #sagesse #citationmotivation
#motivation #perseverance #discipline #confianceensoi #gratitude #reussite #inspiration #patience

## Fabrication des slides
1. Écrire `<dossier>/spec.json` (voir `2026-10-bambou/spec.json` comme modèle).
   Dossier : `AAAA-MM-JJ-matin` ou `AAAA-MM-JJ-soir` (date de publication).
   Chaque slide : `c1`/`c2` (dégradé haut→bas, couleurs sombres), `glow` [x, y, couleur], `kicker` (petit titre),
   `text` (texte principal), optionnel `sub` (sous-texte italique), `size` (76 par défaut, 88–92 pour les phrases courtes).
   Varier les palettes d'un carrousel à l'autre. `accent` : couleur dorée/ambre par défaut `#E8B04A`.
2. `python3 outils/make_carousel.py <dossier>/spec.json <dossier>`
3. Vérifier visuellement au moins la 1re et la dernière slide (texte qui ne déborde pas).

## Programmation Metricool
- blogId : `7501132`, réseau `instagram`, fuseau `Europe/Paris`.
- Créneaux : 2 par jour, **12:15** (carrousel) et **19:15** (reel, voir plus bas) (ajuster si Metricool `getBestTimeToPostByNetwork` donne des créneaux nettement meilleurs).
- Publication directe : `draft: false`, `autoPublish: true`, `instagramData: {"type": "POST"}`.
- Avant de programmer, lire `getScheduledPosts` sur la semaine et ne jamais occuper un créneau déjà pris (à moins de 2 h d'un post existant).
- Si Metricool renvoie une erreur de limite de l'offre gratuite : s'arrêter, ne pas réessayer, le signaler.

## Reels avec musique (1 par jour)
Chaque jour : **12:15 = carrousel**, **19:15 = reel**. Soit 7 carrousels + 7 reels par semaine.
Les carrousels ne peuvent pas avoir de musique via l'API ; les reels oui.

Fabrication d'un reel :
1. Même `spec.json` qu'un carrousel, avec `"reel": true` (masque le « Glisse → »). 6 à 7 slides, textes courts.
   Les formats les plus forts en reel : paraboles, « vérités qui font mal », listes percutantes.
2. `python3 outils/make_carousel.py <dossier>/spec.json <dossier>`
3. `python3 outils/make_reel.py <dossier>` → `<dossier>/reel.mp4` (9:16, ~3,2 s par slide, sans piste audio) et `<dossier>/cover.jpg`.
   Dossier : `AAAA-MM-JJ-reel`.
4. Programmation Metricool : `media` = [lien raw de `reel.mp4`], `videoThumbnailUrl` = lien raw de `cover.jpg`,
   `instagramData` = {"type": "REEL", "showReelOnFeed": true, "audioConfiguration": {"audioId": "<titre + artiste>", "audioVolume": 100}}.
   Musique : morceau instrumental, émotionnel ou inspirant (piano, cinématique, lo-fi calme), varier d'un reel à l'autre.
   Si Metricool renvoie une liste de candidats, reprendre avec l'identifiant numérique du plus pertinent.
   Si l'ajout de musique est refusé (compte non professionnel ou non relié à une page Facebook) : programmer le reel
   **sans** `audioConfiguration`, et le signaler dans le message final.

## Après chaque lot
Ajouter les sujets dans `SUJETS.md` (date, créneau, titre), commit et push.
