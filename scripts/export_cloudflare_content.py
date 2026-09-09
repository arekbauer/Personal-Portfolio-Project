"""Export the legacy Django SQLite content into Git-managed JSON files.

Run this against a fresh copy of the production db.sqlite3 before final cutover:
    python scripts/export_cloudflare_content.py /path/to/db.sqlite3
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "src" / "content"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def rows(db: sqlite3.Connection, query: str, parameters: tuple = ()) -> list[dict]:
    return [dict(row) for row in db.execute(query, parameters)]


def export(db_path: Path) -> None:
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    intro = rows(db, "SELECT description, image, image_small FROM portfolio_intro ORDER BY id")
    write_json(CONTENT / "site.json", {"intros": intro})

    project_dir = CONTENT / "projects"
    for project in rows(db, "SELECT * FROM portfolio_project ORDER BY id"):
        project["skills"] = [
            project.pop(key)
            for key in ("skill1", "skill2", "skill3", "skill4")
            if project.get(key)
        ]
        project["order"] = project.pop("id")
        write_json(project_dir / f"{project['order']:02d}.json", project)

    categories = {
        row["id"]: row["name"]
        for row in db.execute("SELECT id, name FROM recipes_category")
    }
    recipe_dir = CONTENT / "recipes"
    for recipe in rows(db, "SELECT * FROM recipes_recipe ORDER BY title"):
        recipe_id = recipe.pop("id")
        recipe["baseServings"] = recipe.pop("base_servings")
        recipe["imageCredit"] = recipe.pop("image_credit")
        recipe["imageCreditUrl"] = recipe.pop("image_credit_url")
        recipe["sourceName"] = recipe.pop("source_name")
        recipe["sourceUrl"] = recipe.pop("source_url")
        recipe["categories"] = [
            categories[row["category_id"]]
            for row in db.execute(
                "SELECT category_id FROM recipes_recipe_categories WHERE recipe_id = ? ORDER BY id",
                (recipe_id,),
            )
        ]
        recipe["ingredients"] = rows(
            db,
            """SELECT amount, unit, name, note, section
               FROM recipes_ingredient WHERE recipe_id = ? ORDER BY position, id""",
            (recipe_id,),
        )
        recipe["steps"] = [
            row["instruction"]
            for row in db.execute(
                "SELECT instruction FROM recipes_recipestep WHERE recipe_id = ? ORDER BY position, id",
                (recipe_id,),
            )
        ]
        write_json(recipe_dir / f"{recipe['slug']}.json", recipe)

    albums = rows(
        db,
        """SELECT spotify_album_id, title, artist, cover_image_url, spotify_url,
                  release_date, featured, display_order
           FROM portfolio_spotifyalbumpick ORDER BY display_order, id""",
    )
    for album in albums:
        album["spotifyAlbumId"] = album.pop("spotify_album_id").split("?", 1)[0]
        album["coverImageUrl"] = album.pop("cover_image_url")
        album["spotifyUrl"] = album.pop("spotify_url")
        album["releaseDate"] = album.pop("release_date")
        album["featured"] = bool(album["featured"])
        album["displayOrder"] = album.pop("display_order")
    write_json(CONTENT / "albums.json", albums)

    slab_rows = rows(
        db,
        """SELECT s.card_id, s.internal_name, s.grader, s.grade,
                  s.certification_number, s.slab_photo, s.featured,
                  s.display_order, c.image_large, c.data
           FROM portfolio_slab s
           LEFT JOIN portfolio_pokemoncardcache c ON c.card_id = s.card_id
           ORDER BY s.display_order, s.id""",
    )
    slabs = []
    for slab in slab_rows:
        card = json.loads(slab.pop("data") or "{}")
        slabs.append(
            {
                "cardId": slab["card_id"],
                "name": card.get("name") or slab["internal_name"] or slab["card_id"],
                "setName": card.get("set", {}).get("name", ""),
                "number": card.get("number", ""),
                "rarity": card.get("rarity", ""),
                "grader": slab["grader"],
                "grade": slab["grade"],
                "certificationNumber": slab["certification_number"],
                "image": slab["slab_photo"] or slab["image_large"],
                "featured": bool(slab["featured"]),
                "displayOrder": slab["display_order"],
            }
        )
    write_json(CONTENT / "slabs.json", slabs)

    print(f"Exported content from {db_path} to {CONTENT}")


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "db.sqlite3"
    export(source.resolve())
