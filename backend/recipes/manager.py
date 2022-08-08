from django.db.models import  F, QuerySet,  Sum


class IngridientAmountQuerySet(QuerySet):
    def purchases(self, user):
        return self.filter(
            recipe__purchases__user=user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit'),
        ).annotate(
            total=Sum('amount'),
        )