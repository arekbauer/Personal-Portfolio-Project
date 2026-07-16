from django.contrib import admin
from .models import Experience, Intro, PokemonCardCache, Project, Slab, SpotifyAlbumPick

admin.site.register(Project)
admin.site.register(Intro)
admin.site.register(Experience)


@admin.register(PokemonCardCache)
class PokemonCardCacheAdmin(admin.ModelAdmin):
    list_display = ("card_id", "display_name", "set_name", "card_number", "rarity", "fetched_at")
    search_fields = ("card_id", "data")
    readonly_fields = ("fetched_at", "image_small", "image_large")


@admin.register(Slab)
class SlabAdmin(admin.ModelAdmin):
    list_display = ("internal_name", "card_id", "grader", "grade", "certification_number", "featured", "display_order")
    list_display_links = ("card_id",)
    list_filter = ("grader", "grade", "featured")
    search_fields = ("internal_name", "card_id", "certification_number")
    ordering = ("display_order", "id")


@admin.register(SpotifyAlbumPick)
class SpotifyAlbumPickAdmin(admin.ModelAdmin):
    list_display = ("spotify_album_id", "title", "artist", "release_date", "featured", "display_order", "fetched_at")
    list_filter = ("featured",)
    search_fields = ("spotify_album_id", "title", "artist")
    readonly_fields = ("title", "artist", "cover_image_url", "spotify_url", "release_date", "data", "fetched_at")
    ordering = ("-release_date", "display_order", "id")
