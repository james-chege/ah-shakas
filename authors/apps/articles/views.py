from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsOwnerOrReadonly
from .models import ArticlesModel
from .serializers import ArticlesSerializers
from .renderers import ArticlesRenderer


class ArticlesList(ListCreateAPIView):
    queryset = ArticlesModel.objects.all()
    serializer_class = ArticlesSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticlesRenderer,)

    def post(self, request):
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
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
        serializer = self.serializer_class(article, data=data, partial=True)
        if serializer.is_valid():
            self.check_object_permissions(request, article)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        """This method overwrites the default django for an error message"""
        super().delete(self, request, slug)
        return Response({"message": "Article Deleted Successfully"})
