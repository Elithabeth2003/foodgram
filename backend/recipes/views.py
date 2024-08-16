from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from .models import Recipe


def redirect_to_recipe_detail(request, pk):
    """Перенаправляет на детальную страницу рецепта, если он существует."""
    if Recipe.objects.filter(pk=pk).exists():
        return redirect(f'/recipes/{pk}/')
    else:
        raise ValidationError(f'Рецепт с id {pk} отсутствует.')
