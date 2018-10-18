from django.db import models
from django.utils.text import slugify

from authors.apps.authentication.models import User


class ArticlesModel(models.Model):
    """ This class defines the model for creating articles"""
    slug = models.SlugField(db_index=True, max_length=128, unique=True, blank=True)
    title = models.CharField(max_length=128, blank=False)
    description = models.CharField(max_length=120, blank=False)
    body = models.TextField(blank=False)
    tags = models.ManyToManyField('articles.Tags', related_name='articles')
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    author = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def create_title_slug(self):
        """This method automatically slugs the title before saving"""
        slug = slugify(self.title)
        new_slug = slug
        n = 1
        while ArticlesModel.objects.filter(slug=new_slug).exists():
            new_slug = '{}-{}'.format(slug, n)
            n += 1

        return new_slug

    def save(self, *args, **kwargs):
        """This method ensures that the article is saved with a slug"""
        if not self.slug:
            self.slug = self.create_title_slug()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
   

class Comment(models.Model):
    """
    Model for comments
    """

    body = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    article = models.ForeignKey(ArticlesModel, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='threads',
        on_delete=models.CASCADE
    )

    def __str__(self):
       return self.body

    class Meta:
        ordering = ('-created_at',)


class Rating(models.Model):
    user = models.ForeignKey(User, related_name='rating', on_delete=models.CASCADE)
    article = models.ForeignKey(ArticlesModel, related_name='rating', on_delete=models.CASCADE)
    rating = models.FloatField(null=False)


class Favourite(models.Model):
    '''model for favourating articles'''
    article = models.ForeignKey(ArticlesModel, related_name="favourited", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="favourites", on_delete=models.CASCADE)


class Tags(models.Model):
    tag = models.CharField(max_length=120)

    def __str__(self):
        return self.tag
