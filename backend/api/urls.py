from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = "api"

router = DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register(r"users", CustomUserViewSet, basename="users")
router.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
    path("", include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
