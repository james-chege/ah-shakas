from django.urls import path

from . import views

app_name = "articles"

urlpatterns = [
    path('articles/', views.ArticlesList.as_view(), name='articles'),
    path('articles/<slug>', views.ArticlesDetails.as_view(),  name='article-details'),
    path('articles/<slug>/comments/', views.CommentsListCreateView.as_view(), name='comments'),
    path('articles/<slug>/comments/<int:id>/', views.CommentsRetrieveUpdateDestroy.as_view(), name='comment-details'),
    path('articles/<slug>/rate/', views.RatingDetails.as_view(), name='ratings')
]
