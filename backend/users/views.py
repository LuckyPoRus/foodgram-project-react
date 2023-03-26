from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers import (
    CustomUserRegisterSerializer,
    CustomUserSerializer,
    SubscriptionSerializer
)
from .models import Subscription

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CustomUserSerializer
        return CustomUserRegisterSerializer

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)

        if request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                raise ValueError("Уже подписан")
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author)
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
    def get_subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
