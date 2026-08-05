from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum

from performance.models import KPIWeight
from performance.services import DEFAULT_KPI_WEIGHTS


class Command(BaseCommand):
    help = (
        'Seed default KPI weights (must total 100%). '
        'Safe to re-run; updates existing metric_key rows.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        for name, metric_key, weight in DEFAULT_KPI_WEIGHTS:
            existing = KPIWeight.objects.filter(metric_key=metric_key).first()
            if existing:
                existing.name = name
                existing.weight_percentage = weight
                existing.active = True
                existing.save(skip_weight_validation=True)
            else:
                obj = KPIWeight(
                    name=name,
                    metric_key=metric_key,
                    weight_percentage=weight,
                    active=True,
                )
                obj.save(skip_weight_validation=True)

        # Deactivate any unexpected extra active weights not in the default set.
        default_keys = [key for _n, key, _w in DEFAULT_KPI_WEIGHTS]
        KPIWeight.objects.exclude(metric_key__in=default_keys).filter(
            active=True
        ).update(active=False)

        total = (
            KPIWeight.objects.filter(active=True).aggregate(
                total=Sum('weight_percentage')
            )['total']
            or Decimal('0')
        )
        count = KPIWeight.objects.filter(active=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Default KPI weights seeded ({count} active). Total = {total}%'
            )
        )
