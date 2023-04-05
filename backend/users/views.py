from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    CustomUserRegisterSerializer,
    CustomUserSerializer,
    SubscriptionSerializer,
    ChangePasswordSerializer
)
from api.pagination import CustomPagination
from .models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CustomUserSerializer
        return CustomUserRegisterSerializer

    def retrieve(self, request, id=None):
        author = get_object_or_404(User, id=id)
        context = {"request": request}
        serializer = CustomUserSerializer(
            author,
            context=context
        )
        return Response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
        pagination_class=None,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        context = {"request": request}
        serializer = ChangePasswordSerializer(
            data=request.data,
            context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        context = {"request": request}

        if request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                raise ValueError("Уже подписан")
            sub = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(sub, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        context = {"request": request}
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages, many=True, context=context)
        return self.get_paginated_response(serializer.data)
