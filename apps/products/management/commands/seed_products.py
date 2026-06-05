from decimal import Decimal
from django.core.management.base import BaseCommand

from apps.products.models import Product


class Command(BaseCommand):
    help = 'Seed the database with 10 sample products for inventory'

    def handle(self, *args, **options):
        samples = [
            {'brand': 'Xiaomi', 'model': f'Redmi Note {i}', 'price': Decimal('149.99'), 'stock': 10 + i} for i in range(1, 6)
        ] + [
            {'brand': 'Samsung', 'model': f'Galaxy A{i}0', 'price': Decimal('199.99'), 'stock': 5 + i} for i in range(1, 6)
        ]

        created = 0
        skipped = 0
        base_imei = 990000000000000

        for idx, item in enumerate(samples, start=1):
            imei = str(base_imei + idx)
            # IMEI limited to 15 chars
            imei = imei[:15]

            obj, created_flag = Product.objects.get_or_create(
                imei=imei,
                defaults={
                    'brand': item['brand'],
                    'model': item['model'],
                    'price': item['price'],
                    'stock_quantity': item['stock'],
                    'warranty_months': 12,
                    'description': 'Sample seeded product',
                    'is_active': True,
                }
            )

            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.display_name} (IMEI: {obj.imei})"))
            else:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Skipped (exists): {obj.display_name} (IMEI: {obj.imei})"))

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created: {created}, Skipped: {skipped}"))
