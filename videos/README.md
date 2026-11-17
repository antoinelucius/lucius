# Vidéos de gameplay — Mythic Worlds Simulator

Ce dossier contient tout pour produire le **trailer de la page Roblox** et des **vidéos courtes verticales** (TikTok, YouTube Shorts, Reels) à partir de **vrai gameplay**.

**Le principe :**
1. Vous enregistrez les séquences (« rushes ») dans le jeu en suivant la liste ci-dessous.
2. Vous les déposez dans `videos/rushes/` avec les noms indiqués.
3. Le script `montage.py` monte automatiquement les vidéos : découpe, recadrage vertical, textes en anglais, flashs, ralentis, musique et carte de fin.

> Les textes à l'écran sont en anglais pour toucher le public Roblox international. Ils se modifient dans les fichiers `configs/*.json`.

---

## 1. Les séquences à enregistrer

Chaque fichier doit durer **au moins 14 secondes**. Démarrez l'enregistrement 2 à 3 s **avant** l'action et arrêtez-le 2 à 3 s **après**.

| Fichier | Quoi filmer | Point fort à capter |
|---|---|---|
| `01_divine_hatch.mp4` | Éclosion d'un pet **Divin** | Colonnes de lumière, auréole arc-en-ciel, son de récompense |
| `02_world1_pets.mp4` | Le joueur court dans le monde 1 avec plusieurs pets qui le suivent | Plan large, beaucoup de pets à l'écran |
| `03_egg_meadow.mp4` | Ouverture de l'œuf **Prairie** | L'animation complète de l'œuf |
| `04_egg_treasure.mp4` | Ouverture de l'œuf **Trésor** | Idem |
| `05_egg_volcanic_storm.mp4` | Ouverture de l'œuf **Orage volcanique** | Idem |
| `06_egg_eruption.mp4` | Ouverture de l'œuf **Éruption** | Idem |
| `07_egg_constellation.mp4` | Ouverture de l'œuf **Constellation** | Idem |
| `08_egg_black_hole.mp4` | Ouverture de l'œuf **Trou noir** | Idem, c'est le plus spectaculaire |
| `09_boss_golem.mp4` | Combat contre le **Golem** | Son attaque spéciale « éruption » |
| `10_boss_knight.mp4` | Combat contre le **Chevalier** | Sa bulle, et le joueur qui esquive |
| `11_fusion.mp4` | Une **fusion** de pets | Le moment où le nouveau pet apparaît |
| `12_new_world.mp4` | Passage dans un **nouveau monde** | Le portail ou la transition, puis la découverte |
| `13_secret_hatch.mp4` | Éclosion d'un pet **Secret** | Toute l'animation (elle sera ralentie) |
| `s1_hatch_spam.mp4` | 15 s d'éclosions à la chaîne (pets communs) | Le rythme, le compteur de pets |
| `s3_boss_full.mp4` | Un combat de boss en entier, jusqu'aux récompenses | Attaque spéciale vers 5 s, victoire et récompenses vers 7 à 12 s |
| `s4_fusion_full.mp4` | Une fusion complète : choix des pets, attente, résultat | Le résultat apparaît vers 6 s |
| `s5_last_world.mp4` | Le dernier monde (ou le plus beau) | Plan large du décor |

**Astuce pour les éclosions rares :** pour filmer un Divin ou un Secret sans attendre des heures, utilisez une commande de test réservée aux admins dans Roblox Studio pour forcer la rareté. Retirez-la avant la publication du jeu. Ce que vous filmez reste la vraie animation du jeu.

### Réglages d'enregistrement
- **Outil :** OBS Studio (gratuit), ou l'enregistreur intégré de Roblox.
- **Format :** 1920×1080, 30 ou 60 images/s, en MP4.
- **Cadrage :** gardez l'action **au centre de l'écran**. Les versions verticales recadrent le centre de l'image.
- **Son :** laissez le son du jeu activé. Les « retours » sonores (récompense, coup, éclosion) sont ce qui rend une vidéo accrocheuse.
- **Interface :** masquez les menus qui ne servent pas à la scène. Gardez ceux qui montrent la récompense (pet obtenu, rareté).
- Faites **2 ou 3 prises** de chaque scène et gardez la meilleure.
- Un fichier fait plus de 100 Mo (limite de GitHub) ? Raccourcissez-le, ou envoyez-le autrement (Google Drive par exemple).

---

## 2. Les vidéos prévues

### Trailer de la page Roblox — `configs/trailer.json` (29 s, 16:9)

| Temps | Séquence | Texte à l'écran |
|---|---|---|
| 0–2,5 s | Éclosion Divine (flash blanc) | CAN YOU HATCH A DIVINE? |
| 2,5–5 s | Le joueur et ses pets dans le monde 1 | COLLECT MYTHIC PETS |
| 5–10,5 s | Les 6 œufs en coupes rapides (environ 0,9 s chacun) | 6 LEGENDARY EGGS |
| 10,5–14 s | Boss Golem, attaque éruption (léger zoom) | DEFEAT EPIC BOSSES |
| 14–16,5 s | Boss Chevalier, bulle | DODGE THEIR SPECIAL ATTACKS |
| 16,5–20 s | Fusion (flash) | FUSE PETS / MAKE THEM STRONGER |
| 20–23 s | Nouveau monde (zoom) | UNLOCK NEW WORLDS |
| 23–26 s | Éclosion Secrète, ralentie | SECRET PETS EXIST... |
| 26–29 s | Carte de fin | MYTHIC WORLDS SIMULATOR / PLAY NOW ON ROBLOX |

Dès la première seconde, on voit l'action et l'univers. Tout est du vrai gameplay.

### Vidéos courtes verticales (9:16)

| Config | Idée | Durée | Accroche (première seconde) |
|---|---|---|---|
| `short_divine_hatch.json` | « Hatching until I get a DIVINE » | ~18 s | La fin (le Divin) montrée en premier : « 1 IN 1,000,000 PET? » |
| `short_egg_rating.json` | « Rating every egg animation » | ~20 s | Le trou noir : « RATING EVERY EGG » |
| `short_boss.json` | L'attaque spéciale du boss | ~17 s | « THIS BOSS IS NOT FAIR » |
| `short_fusion.json` | Le pari de la fusion | ~15 s | « I FUSED MY BEST PETS... » |
| `short_worlds.json` | Monde 1 contre dernier monde | ~13 s | « WORLD 1 » |

**Avant de publier :** remplacez « 1 IN 1,000,000 » par la vraie probabilité du jeu, et ajustez les notes de `short_egg_rating.json` (4/10… 11/10) selon vos goûts. Il ne faut rien annoncer que le jeu ne fait pas.

**Légende et hashtags (exemple) :** `Would you risk your best pets? 😱 #roblox #robloxsimulator #petsimulator #robloxgame #fyp`. Terminez par une question : elle pousse aux commentaires, et c'est ce qui crée la communauté.

---

## 3. Faire le montage

### Option simple
Déposez les rushes dans `videos/rushes/` (et une musique libre de droits dans `videos/music/`), poussez-les, puis demandez à Claude : « fais le montage ». Les vidéos finies arrivent dans `videos/out/`.

### Sur votre ordinateur
Il faut [Python 3](https://www.python.org/downloads/) et [ffmpeg](https://ffmpeg.org/download.html) version 6.1 ou plus récente.

```bash
# Vérifier que tous les rushes sont présents et assez longs
python3 videos/montage.py videos/configs/trailer.json --check

# Monter le trailer, puis les vidéos courtes
python3 videos/montage.py videos/configs/trailer.json
python3 videos/montage.py videos/configs/short_boss.json
```

### Musique
Mettez `trailer.mp3` et `short.mp3` dans `videos/music/`. Utilisez **uniquement** de la musique libre de droits (bibliothèque audio de YouTube, Pixabay Music…), sinon TikTok ou YouTube couperont le son. Sans musique, supprimez la ligne `"music"` de la config. Sur TikTok, vous pouvez aussi ajouter un son tendance directement dans l'application.

### Modifier une vidéo (format des configs)

```jsonc
{
  "format": "9:16",              // "16:9", "9:16" ou "1:1"
  "output": "../out/ma_video.mp4",
  "music": "../music/short.mp3", // optionnel
  "music_volume": 0.45,          // volume de la musique (0 à 1)
  "game_volume": 1.0,            // volume du son du jeu
  "fit": "crop",                 // "crop" = plein écran recadré, "blur" = image entière sur fond flou
  "segments": [
    {
      "file": "../rushes/09_boss_golem.mp4",
      "start": 3.2,              // où commencer dans le rush (en secondes)
      "duration": 2.5,           // durée dans la vidéo finale
      "text": "DEFEAT EPIC BOSSES",
      "subtext": "OPTIONAL SECOND LINE",
      "speed": 0.5,              // 0.5 = ralenti x2
      "zoom": 1.1,               // zoom progressif
      "flash": true,             // flash blanc au début
      "crop_x": 0.5,             // vertical : 0 = garder la gauche, 1 = la droite
      "audio": true              // false = couper le son du jeu sur ce plan
    },
    { "type": "card", "duration": 2, "text": "PLAY NOW ON ROBLOX", "subtext": "...", "color": "#120A2E" }
  ]
}
```

En général, il suffit d'ajuster le `start` de chaque plan pour tomber pile sur le moment fort.
