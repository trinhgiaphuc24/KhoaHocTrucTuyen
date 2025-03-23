
# from threading import activeCount
#
# from cloudinary.provisioning import users
# from django.contrib.gis.gdal.prototypes.raster import create_ds
from rest_framework import viewsets, generics, permissions, parsers, status
from courses.models import Course, Category, Lesson, User, Comment, Like
from courses import serializers, paginators, perms
from rest_framework.response import Response
from rest_framework.decorators import action

class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer

class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = paginators.CoursePagination

    def get_queryset(self):
        query = self.queryset

        q = self.request.query_params.get('q')
        if q:
            query = query.filter(subject__icontains=q)

        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            query = query.filter(category_id=cate_id)

        return query

    @action(methods=['get'], url_path='lessons', detail=True)
    def get_lessons(self, request, pk):
        lessons = self.get_object().lesson_set.filter(active=True)
        return Response(serializers.LessonSerializer(lessons, many=True).data)


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.prefetch_related('tags').filter(active=True)
    serializer_class = serializers.LessonDetailsSerializer

    def get_permissions(self):
        if self.action in ['get_comments','like'] and self.request.method.__eq__('POST'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'post'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        if request.method.__eq__('POST'):
            u = serializers.CommentSerializer(data={
                'content' : request.data.get('content'),
                'user' : request.user.pk,
                'lesson' : pk
            })
            u.is_valid()
            c = u.save()
            return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)
        else:
            comments = self.get_object().comment_set.select_related('user').filter(active=True)
            return Response(serializers.CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='like')
    def like(self, request, pk):
        li, created = Like.objects.get_or_create(user=request.user, lesson_id=pk)
        if not created:
            li.active = not li.active
        li.save()

        return Response(serializers.LessonDetailsSerializer(self.get_object(), context={'request':request}).data)

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(methods=['get'], url_path='current-user', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data)

class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.IsCommentOwner]