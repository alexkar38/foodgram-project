from http import HTTPStatus

from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User
from users.serialaizers import FollowListSerializer, FollowSerializer


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {"author": id, "user": request.user.id}
        serializer = FollowSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = get_object_or_404(Follow, author=author, user=user)
        follow.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class FollowListView(ListAPIView):
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowListSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
