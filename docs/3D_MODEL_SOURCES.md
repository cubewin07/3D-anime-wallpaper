# 3D Anime Character Sourcing Guide

A curated, verified catalog of sources for finding high-quality 3D anime characters legally and for free (non-commercial fan art).

---

## Tier 1: Official Studio Fan-Distribution Hubs

### 1. Aplaybox (模之屋 - [aplaybox.com](https://www.aplaybox.com/))
* **Best for**: *Genshin Impact*, *Honkai: Star Rail*, *Zenless Zone Zero*, *Honkai Impact 3rd*, *Arknights*, *Naraka: Bladepoint*.
* **Quality**: **S-Tier** (Original studio assets released officially by miHoYo/HoYoverse and NetEase).
* **Format**: MMD (`.pmx`) with textures, armatures, physics, and facial blendshapes.
* **License**: Free for non-commercial fan creation.
* **How to search**:
  * Type character name in English or Chinese (e.g., "Raiden Shogun" / "雷电将军", "Kafka" / "卡芙卡", "Ellen Joe" / "艾莲").
  * Filter by **Models (模型)**.

---

## Tier 2: Japanese Community Model Archives

### 2. BowlRoll ([bowlroll.net](https://bowlroll.net/)) & NicoNico Douga ([3d.nicovideo.jp](https://3d.nicovideo.jp/))
* **Best for**: Classic anime series (*Attack on Titan*, *Fate/stay night*, *Jujutsu Kaisen*, *Demon Slayer*, *Chainsaw Man*, *Evangelion*, *Vocaloid/Miku*, *Hololive*).
* **Quality**: **S/A-Tier** (High-effort community sculpts created by Japanese 3D modelers).
* **Format**: MMD (`.pmx` / `.pmd`).
* **Search Tip**:
  * Japanese modelers tag with Japanese Kanji/Katakana.
  * Search using the character's Japanese name (e.g., `五条悟` for Gojo Satoru, `初音ミク` for Hatsune Miku, `セイバー` for Saber).
  * Some BowlRoll files require a "pass" (hint usually found in the linked NicoNico/Twitter post, often character birthdate or catchphrase).

---

## Tier 3: VRM & VRChat Avatar Platforms

### 3. VRoid Hub ([hub.vroid.com](https://hub.vroid.com/))
* **Best for**: Modern VTubers, slice-of-life anime aesthetics, custom anime characters.
* **Quality**: **A-Tier** (Fully rigged with spring-bone hair physics and MToon shaders).
* **Format**: `.vrm` (Importable directly using our `VRM_Addon_for_Blender`).
* **License Filter**:
  * Click the filter button and check **"Free to download"** and **"CC-BY"** (Attribution permitted).

### 4. Booth.pm ([booth.pm](https://booth.pm/))
* **Best for**: High-fashion anime clothing, accessories, hairstyles, and full avatars.
* **Format**: `.vrm`, `.fbx`, `.unitypackage`.
* **Search Tip**:
  * Search keywords like `VRM free`, `MMD free`, or character names, then set price filter to `¥0`.

---

## Tier 4: Video Game Asset Archives

### 5. The Models Resource ([models-resource.com](https://www.models-resource.com/))
* **Best for**: Characters from anime fighting and action games (*Naruto Ultimate Ninja Storm*, *Dragon Ball FighterZ*, *One Piece: Pirate Warriors*, *Persona 5*, *Bleach*).
* **Quality**: **A-Tier** (Authentic game topology and UVs).
* **Format**: `.obj`, `.fbx`, `.dae`.
* **Notes**: Game models often require our custom cel-shading setup since game shaders are proprietary engine shaders.

---

## Sourcing Checklist Before Bringing into Blender
1. Check the file format (`.pmx`, `.vrm`, or `.fbx`).
2. Extract all textures into a dedicated `textures/` subfolder next to the model.
3. Review the creator's README for non-commercial fan-use credits.
4. Place the raw files in `characters/<character_name>/raw/`.
