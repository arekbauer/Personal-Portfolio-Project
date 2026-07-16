from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='portfolio/images/')
    url = models.URLField(blank=True)
    skill1 = models.CharField(max_length=16, null=True, blank=True)
    skill2 = models.CharField(max_length=16, null=True, blank=True)
    skill3 = models.CharField(max_length=16, null=True, blank=True)
    skill4 = models.CharField(max_length=16, null=True, blank=True)
    
class Intro(models.Model):
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/images/', null=True)
    image_small = models.ImageField(upload_to='portfolio/images/', null=True)


class SpotifyAlbumPick(models.Model):
    spotify_album_id = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=180, blank=True)
    artist = models.CharField(max_length=180, blank=True)
    cover_image_url = models.URLField(blank=True)
    spotify_url = models.URLField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)
    featured = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        if self.title and self.artist:
            return f"{self.title} - {self.artist}"
        return self.spotify_album_id
    
class Experience(models.Model):
    title = models.CharField(max_length=30)
    subtitle = models.CharField(max_length = 30, null=True)
    skills = models.CharField(max_length=200, blank=True, help_text="Separate skills with commas (e.g. Python, CSS, AWS)")
    start_date = models.PositiveSmallIntegerField()
    end_date = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField()
    
    @property
    def end_date_is_null(self):
        return self.end_date or "Present"
    
    def get_skills_list(self):
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',')]


class PokemonCardCache(models.Model):
    card_id = models.CharField(max_length=40, unique=True)
    data = models.JSONField(default=dict, blank=True)
    image_small = models.URLField(blank=True)
    image_large = models.URLField(blank=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["card_id"]
        verbose_name = "Pokemon card cache"
        verbose_name_plural = "Pokemon card cache"

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.data.get("name") or self.card_id

    @property
    def set_name(self):
        return self.data.get("set", {}).get("name", "")

    @property
    def card_number(self):
        return self.data.get("number", "")

    @property
    def rarity(self):
        return self.data.get("rarity", "")

    @property
    def pokedex_numbers(self):
        return self.data.get("nationalPokedexNumbers", [])


class Slab(models.Model):
    card_id = models.CharField(max_length=40)
    internal_name = models.CharField(max_length=80, blank=True)
    grader = models.CharField(max_length=20)
    grade = models.CharField(max_length=10)
    certification_number = models.CharField(max_length=60, blank=True)
    slab_photo = models.ImageField(upload_to="portfolio/slabs/", blank=True)
    featured = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        label = f"{self.internal_name} ({self.card_id})" if self.internal_name else self.card_id
        cert = f" #{self.certification_number}" if self.certification_number else ""
        return f"{label} - {self.grader} {self.grade}{cert}"
