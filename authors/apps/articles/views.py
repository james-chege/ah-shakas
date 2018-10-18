from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     GenericAPIView,
                                     ListAPIView)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError


from .models import ArticlesModel, Comment, Rating, Favourite, Tags, LikesDislikes
from .serializers import (ArticlesSerializers,
                          CommentsSerializers,
                          RatingSerializer,
                          FavouriteSerializer,
                          TagSerializers,
                          LikesDislikesSerializer)
from .renderers import ArticlesRenderer, RatingJSONRenderer, FavouriteJSONRenderer
from .permissions import IsOwnerOrReadonly



def get_article(slug):
    """
    This method returns article for further reference made to article slug
    """
    article = ArticlesModel.objects.filter(slug=slug).first()
    if not article:
        message = {'message': 'Article slug is not valid.'}
        return message
    # queryset always has 1 thing as long as it is unique
    return article

class ArticlesList(ListCreateAPIView):
    queryset = ArticlesModel.objects.all()
    serializer_class = ArticlesSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticlesRenderer,)

    def post(self, request):
        article = request.data.get('article', {})
        serializer = self.serializer_class(
            data=article, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class ArticlesDetails(RetrieveUpdateDestroyAPIView):
    queryset = ArticlesModel.objects.all()
    serializer_class = ArticlesSerializers
    renderer_classes = (ArticlesRenderer,)
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)
    lookup_field = 'slug'

    def put(self, request, slug):
        """This method overwrites the """
        article = ArticlesModel.objects.get(slug=slug)
        data = request.data.get('article', {})
        serializer = self.serializer_class(
            article, 
            data=data, 
            partial=True, 
            context={'request': request}
        )
        if serializer.is_valid():
            self.check_object_permissions(request, article)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        """This method overwrites the default django for an error message"""
        super().delete(self, request, slug)
        return Response({"message": "Article Deleted Successfully"})


class TagsView(ListAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)
        return Response({'tags': serializer.data}, status=status.HTTP_200_OK)


class RatingDetails(GenericAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)
    renderer_classes = (RatingJSONRenderer,)

    def get_rating(self, user, article):
        """
        Returns a rating given the user id and the article id
        """
        try:
            return Rating.objects.get(user=user, article=article)
        except Rating.DoesNotExist:
            raise NotFound(detail={'rating': 'Rating not found'})

    def get(self, request, slug):
        """
        Returns the authenticated user's rating on an article given
        its slug.
        """
        article = get_article(slug) 
        if isinstance(article, dict):
            raise ValidationError(detail={'artcle': 'No article found for the slug given'})

        # If the user is authenticated, return their rating as well, if not or
        # the user has not rated the article return the rating average...
        rating = None
        if request.user.is_authenticated:
            try:
                rating = Rating.objects.get(user=request.user, article=article)
            except Rating.DoesNotExist:
                pass
        if not rating:
            rating = Rating.objects.first()

        serializer = self.serializer_class(rating)
        return Response(serializer.data)

    def post(self, request, slug):
        """
        This will create a rating by user on an article. We also check 
        if the user has rated this article before and if that is the case,
        we just update the existing rating.
        """
        article = get_article(slug) 
        if isinstance(article, dict):
            raise ValidationError(detail={'artcle': 'No article found for the slug given'})
        rating = request.data.get('rating', {})
        rating.update({
            'user': request.user.pk,
            'article': article.pk
        })
        # ensure a user cannot rate their own articles
        if article.author == request.user:
            raise ValidationError(detail={'author': 'You cannot rate your own article'})
        # users current rating exists?
        try:
            # if the rating exists, we update it
            current_rating = Rating.objects.get(
                user=request.user.id, 
                article=article.id
            )
            serializer = self.serializer_class(current_rating, data=rating)
        except Rating.DoesNotExist:
            # if it doesn't, create a new one
            serializer = self.serializer_class(data=rating)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, article=article)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, slug):
        """
        Gets an existing rating and updates it
        """
        rating = request.data.get('rating', {})
        article = get_article(slug) 
        if isinstance(article, dict):
            raise ValidationError(detail={'artcle': 'No article found for the slug given'})
        current_rating = self.get_rating(user=request.user.id, article=article.id)
        serializer = self.serializer_class(current_rating, data=rating, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, article=article)

        return Response(serializer.data)
      
    def delete(self, request, slug):
        """
        Deletes a rating
        """
        article = get_article(slug) 
        if isinstance(article, dict):
            raise ValidationError(detail={'artcle': 'No article found for the slug given'})

        rating = self.get_rating(user=request.user, article=article)
        rating.delete()
        return Response(
            {'message': 'Successfully deleted rating'}, 
            status=status.HTTP_200_OK
        )


class CommentsListCreateView(ListCreateAPIView):
    """
    Class for creating and listing all comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentsSerializers
    permission_classes= (IsAuthenticatedOrReadOnly,)


    def post(self, request, slug):
        """
        Method for creating article
        """
        article = get_article(slug=slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)

        comment = request.data.get('comment',{})
        comment['author'] = request.user.id
        comment['article'] = article.pk
        serializer = self.serializer_class(data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        """
        Method for getting all comments
        """
        article = get_article(slug=slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)
        comments = article.comments.filter(parent=None)
        serializer = self.serializer_class(comments.all(), many=True)
        data = {
            'count': comments.count(),
            'comments': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class CommentsRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView, ListCreateAPIView):
    """
    Class for retrieving, updating and deleting a comment
    """
    queryset = Comment.objects.all()
    lookup_url_kwarg = 'id'
    serializer_class = CommentsSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)

    def create(self, request, slug, id):
        """Create a child comment on a parent comment."""
        context = super(CommentsRetrieveUpdateDestroy,
                        self).get_serializer_context()
        
        article = get_article(slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)
        parent = article.comments.filter(id=id).first().pk
        if not parent:
            message = {'detail': 'Comment not found.'}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        body = request.data.get('comment', {}).get('body', {})
        
        data = {
            'body': body,
            'parent': parent,
            'article': article.pk,
            'author': request.user.id
        }
        
        serializer = self.serializer_class(
            data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, slug, id):
        """
        Method for deleting a comment
        """
        article = get_article(slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)

        comment = article.comments.filter(id=id) 
        if not comment:
            message = {'detail': 'Comment not found.'}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        comment[0].delete()
        message = {'detail': 'You have deleted the comment'}
        return Response(message, status=status.HTTP_200_OK)

    def update(self, request, slug, id):
        """
        Method for editing a comment
        """
        article = get_article(slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)

        comment = article.comments.filter(id=id).first()
        if not comment:
            message = {'detail': 'Comment not found.'}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        
        new_comment = request.data.get('comment',{}).get('body', None)
        data = {
            'body': new_comment,
            'article': article.pk,
            'author': request.user.id
        }
        serializer = self.serializer_class(comment, data=data, partial=True)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class FavouriteGenericAPIView(APIView):
    serializer_class = FavouriteSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Favourite.objects.all()
    renderer_classes= (FavouriteJSONRenderer,)

    def post(self, request, slug):
        '''method to favourte by adding to db'''
        article = None
        try:
            article = ArticlesModel.objects.get(slug=slug)
        except ArticlesModel.DoesNotExist:
            raise NotFound(detail={"article": [
                        "does not exist"
                        ]})
        favourite = {}
        favourite["user"] = request.user.id
        favourite["article"] = article.pk
        serializer = self.serializer_class(data=favourite)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        article_serializer = ArticlesSerializers(instance=article, context={'request': request})
        data = {"article":article_serializer.data}
        data["article"]["favourited"]=True
        data["message"] = "favourited"
        return Response(data, status.HTTP_200_OK)

    def delete(self, request, slug):
        '''Method to unfavourite by deleting from the db '''
        article = None
        '''get article'''
        try:
            article = ArticlesModel.objects.get(slug=slug)
        except ArticlesModel.DoesNotExist:
            raise NotFound(detail={"article": [
                        "does not exist"
                        ]})
        "check if they have already unfavourited"
        try:
            favourite = Favourite.objects.get(user=request.user.id, article=article.pk)
        except Favourite.DoesNotExist:
            raise NotFound(detail={"message": [
                        "you had not favourited this article"
                        ]})
        favourite.delete()
        article_serializer = ArticlesSerializers(instance=article, context={'request': request})
        data = {"article":article_serializer.data}
        data["message"] = "unfavourited"
        return Response(data, status.HTTP_200_OK)


class ArticlesLikesDislikes(GenericAPIView):
    """
    Class for creating and deleting article likes/dislikes
    """
    
    queryset = LikesDislikes.objects.all()
    serializer_class = LikesDislikesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)


    def post(self, request, slug):
        #Check if the article exists in the database
        article = get_article(slug)
        
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)

        like = request.data.get('likes', None)

        #Check if the data in the request a valid boolean
        if type(like) == bool:

            #Check if the article belongs to the current user
            if article.author == request.user:
                message = {'detail': 'You cannot like/unlike your own article'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            like_data = {
                'reader': request.user.id,
                'article': article.id,
                'likes': like
            }

            try:
                #Verify if the instance of the article and the user
                #exist in the database and get the like
                user_likes = LikesDislikes.objects.get(article=article.id, reader=request.user.id)

                #if an instance of the user and article both exist in the database
                #we update the existing data instead of creating a new one
                if user_likes:
                    #check if the stored data and the request data are the same
                    #and both true
                    if user_likes.likes and like:
                        return Response(
                            {
                                'detail':'{}, you have already liked this article.'
                                .format(request.user.username)
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    #check if the stored data and the request data are the same
                    #and both false
                    elif not user_likes.likes and not like:
                        return Response(
                            {
                                'detail':'{}, you have already disliked this article.'
                                .format(request.user.username)
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    #check if the stored data and the request data are different
                    #one true and the other false
                    elif like and not user_likes.likes:
                        user_likes.likes = True
                        user_likes.save()
                        article.likes.add(request.user)
                        article.dislikes.remove(request.user)
                        article.save()
                        return Response(
                            {
                                'detail': '{}, you have liked this article.'
                                .format(request.user.username)
                            }, 
                            status=status.HTTP_200_OK
                        )

                    else:
                        user_likes.likes = False
                        user_likes.save()
                        article.likes.remove(request.user)
                        article.dislikes.add(request.user)
                        article.save()
                        return Response(
                            {
                                'detail': '{}, you have disliked this article.'
                                .format(request.user.username)
                            },
                            status=status.HTTP_200_OK
                        )

            except LikesDislikes.DoesNotExist:
                #Create and save a new like object since one does not exist
                serializer=self.serializer_class(data=like_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(article=article, reader=request.user)
                
                #if the request data is true, we update the article
                #with the new data
                if like:
                    article.likes.add(request.user)
                    article.save()
                    return Response(
                        {
                            'detail': '{}, you have liked this article.'
                            .format(request.user.username)
                        },
                        status=status.HTTP_201_CREATED
                    )

                #if the request data is false, we update the article
                #with the new data
                else:
                    article.dislikes.add(request.user)
                    article.save()
                    return Response(
                        {
                            'detail': '{}, you have disliked this article.'
                            .format(request.user.username)
                        }
                        , status=status.HTTP_201_CREATED
                    )
        else:

            return Response(
                {
                    'detail': 'Please indicate whether you like/dislike this article.'
                }
                , status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, slug):
        #Check if the article exists in the database
        article = get_article(slug)
        
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)

        try:
            #Verify if the instance of the article and the user
            #exist in the database and get the like
            user_like = LikesDislikes.objects.get(article=article.id, reader=request.user.id)
            if user_like:
                if user_like.likes:
                    #If like field in the database is true we remove the count
                    #from the likes field of the article and save the current state
                    article.likes.remove(request.user)
                    article.save()
                else:
                    #If like field in the database is false we remove the count
                    #from the dislikes field of the article and save the current state
                    article.dislikes.remove(request.user)
                    article.save()
        except LikesDislikes.DoesNotExist:
            return Response(
                {
                    'detail': 'Likes/dislikes not found.'
                }
                , status=status.HTTP_404_NOT_FOUND
            )
        user_like.delete()
        return Response(
                {
                    'detail': '{}, your reaction has been deleted successfully.'
                    .format(request.user.username)
                }
                , status=status.HTTP_200_OK
            )

