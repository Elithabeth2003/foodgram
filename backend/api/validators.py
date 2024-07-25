from rest_framework import serializers


@staticmethod
def validate_items(items, model, field_name, min_amount=None):
    if field_name == 'ingredients':
        items_id_list = [int(item.get('id')) for item in items]
        amounts = [int(item.get('amount')) for item in items]
    else:
        items_id_list = [int(item) for item in items]
    if len(items_id_list) != len(set(items_id_list)):
        raise serializers.ValidationError(
            {field_name: 'Элементы должны быть уникальными!'}
        )
    existing_items = model.objects.filter(
        id__in=items_id_list
    ).values_list('id', flat=True)
    missing_items = set(items_id_list) - set(existing_items)
    if missing_items:
        raise serializers.ValidationError(
            {field_name: f'Элемент(ы) с id {missing_items} не существует!'}
        )
    if min_amount is not None and field_name == 'ingredients':
        if any(amount < min_amount for amount in amounts):
            raise serializers.ValidationError(
                {field_name: f'Количество элемента '
                 f'не может быть меньше {min_amount}'}
            )
    return items
