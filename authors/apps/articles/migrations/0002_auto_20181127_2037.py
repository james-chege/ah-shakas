# Generated by Django 2.1.2 on 2018-11-27 17:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportarticles',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='email'),
        ),
        migrations.AddField(
            model_name='rating',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='articles.ArticlesModel'),
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='likesdislikes',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like', to='articles.ArticlesModel'),
        ),
        migrations.AddField(
            model_name='likesdislikes',
            name='reader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='highlighted',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to='articles.ArticlesModel'),
        ),
        migrations.AddField(
            model_name='highlighted',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favourite',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourited', to='articles.ArticlesModel'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='commentor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='specific_comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_like', to='articles.Comment'),
        ),
        migrations.AddField(
            model_name='commenthistory',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='articles.Comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='articles.ArticlesModel'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_likes',
            field=models.ManyToManyField(blank=True, related_name='LikeComment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='threads', to='articles.Comment'),
        ),
        migrations.AddField(
            model_name='articlestat',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_views', to='articles.ArticlesModel'),
        ),
        migrations.AddField(
            model_name='articlestat',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_views', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articlesmodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articlesmodel',
            name='dislikes',
            field=models.ManyToManyField(blank=True, related_name='_articlesmodel_dislikes_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articlesmodel',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='_articlesmodel_likes_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articlesmodel',
            name='tags',
            field=models.ManyToManyField(related_name='articles', to='articles.Tags'),
        ),
        migrations.AlterUniqueTogether(
            name='likesdislikes',
            unique_together={('article', 'reader')},
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together={('specific_comment', 'commentor')},
        ),
    ]
