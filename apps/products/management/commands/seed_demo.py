"""
Demo ma'lumotlarni yuklash komandasi.
Bitta katta telefon do'konining bir oylik savdo tarixi.
"""
import random
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.models import CustomUser
from apps.products.models import Product
from apps.customers.models import Customer
from apps.sales.models import Sale, Payment


# ── Mahsulotlar ro'yxati ──────────────────────────────────────────────────────
PRODUCTS = [
    # (brand, model, price, stock, warranty)
    ("Apple",    "iPhone 15 Pro Max 256GB",   16_500_000, 8,  12),
    ("Apple",    "iPhone 15 Pro 128GB",        13_800_000, 10, 12),
    ("Apple",    "iPhone 15 128GB",            11_200_000, 15, 12),
    ("Apple",    "iPhone 14 128GB",             9_500_000, 12, 12),
    ("Apple",    "iPhone 13 128GB",             7_800_000, 18, 12),
    ("Samsung",  "Galaxy S24 Ultra 256GB",     15_900_000, 6,  12),
    ("Samsung",  "Galaxy S24+ 256GB",          12_400_000, 8,  12),
    ("Samsung",  "Galaxy S24 128GB",            9_800_000, 14, 12),
    ("Samsung",  "Galaxy A55 256GB",            5_200_000, 20, 12),
    ("Samsung",  "Galaxy A35 128GB",            3_900_000, 25, 12),
    ("Samsung",  "Galaxy A15 128GB",            2_500_000, 30, 12),
    ("Xiaomi",   "14 Ultra 512GB",             14_200_000, 5,  12),
    ("Xiaomi",   "13T Pro 256GB",               7_600_000, 10, 12),
    ("Xiaomi",   "Redmi Note 13 Pro 256GB",     4_100_000, 22, 12),
    ("Xiaomi",   "Redmi Note 13 128GB",         2_800_000, 35, 12),
    ("Xiaomi",   "Redmi 13C 128GB",             1_900_000, 40, 12),
    ("Realme",   "GT 5 Pro 256GB",              7_200_000, 8,  12),
    ("Realme",   "11 Pro+ 256GB",               4_300_000, 15, 12),
    ("Oppo",     "Find X7 Ultra 512GB",        15_500_000, 4,  12),
    ("Oppo",     "Reno 11 Pro 256GB",           6_800_000, 10, 12),
    ("Vivo",     "X100 Pro 256GB",             13_200_000, 5,  12),
    ("Vivo",     "V30 Pro 256GB",               5_900_000, 12, 12),
    ("OnePlus",  "12 256GB",                   11_800_000, 7,  12),
    ("OnePlus",  "Nord CE4 256GB",              4_600_000, 18, 12),
    ("Huawei",   "Pura 70 Pro 256GB",          14_800_000, 4,  12),
    ("Huawei",   "Nova 12 Pro 256GB",           6_200_000, 9,  12),
    ("Tecno",    "Phantom X2 Pro 256GB",        5_400_000, 12, 12),
    ("Tecno",    "Spark 20 Pro 128GB",          2_200_000, 30, 12),
    ("Infinix",  "Note 40 Pro 256GB",           3_600_000, 18, 12),
    ("Nokia",    "G42 5G 128GB",                2_100_000, 20, 24),
]

# ── Mijozlar ──────────────────────────────────────────────────────────────────
CUSTOMERS = [
    ("Jahongir",  "Toshmatov",   "Baxtiyorovich", "+998901234567", "Toshkent, Yunusobod t., 12-uy", "AB1234567", "Yunusobod IIB"),
    ("Dilnoza",   "Yusupova",    "Karimovna",      "+998901234568", "Toshkent, Chilonzor t., 5-uy",  "AB1234568", "Chilonzor IIB"),
    ("Bobur",     "Rahimov",     "Alievich",       "+998901234569", "Toshkent, Mirzo Ulugbek t.",    "AB1234569", "Mirzo Ulugbek IIB"),
    ("Muazzam",   "Hasanova",    "Saidovna",       "+998901234570", "Samarqand, Registon ko'ch.",    "AB1234570", "Samarqand IIB"),
    ("Sardor",    "Nazarov",     "Ulugbekovich",   "+998901234571", "Toshkent, Shayxontohur t.",     "AB1234571", "Shayxontohur IIB"),
    ("Feruza",    "Qodirov",     "Mansurovna",     "+998901234572", "Toshkent, Yakkasaroy t.",       "AB1234572", "Yakkasaroy IIB"),
    ("Otabek",    "Mirzayev",    "Hamidovich",     "+998901234573", "Toshkent, Olmazar t., 8-uy",   "AB1234573", "Olmazar IIB"),
    ("Hulkar",    "Sotvoldiyeva","Rajabovna",      "+998901234574", "Namangan, Uychi ko'ch.",        "AB1234574", "Namangan IIB"),
    ("Jasur",     "Ergashev",    "Norqulovich",    "+998901234575", "Farg'ona, Tinchlik ko'ch.",     "AB1234575", "Farg'ona IIB"),
    ("Malika",    "Abdullayeva", "Shavkatovna",    "+998901234576", "Toshkent, Uchtepa t., 3-uy",   "AB1234576", "Uchtepa IIB"),
    ("Nodir",     "Xolmatov",    "Baxtiyor ugli",  "+998901234577", "Toshkent, Bektemir t.",         "AB1234577", "Bektemir IIB"),
    ("Zulfiya",   "Tursunova",   "Davlatovna",     "+998901234578", "Toshkent, Sergeli t., 14-uy",  "AB1234578", "Sergeli IIB"),
    ("Ibrohim",   "Sultonov",    "Xurshidovich",   "+998901234579", "Andijon, Asaka ko'ch.",         "AB1234579", "Andijon IIB"),
    ("Nargiza",   "Qosimova",    "Vohidovna",      "+998901234580", "Toshkent, Yashnobod t.",        "AB1234580", "Yashnobod IIB"),
    ("Umid",      "Xasanov",     "Abrorovich",     "+998901234581", "Buxoro, Karvon ko'ch.",         "AB1234581", "Buxoro IIB"),
    ("Shahlo",    "Razzaqova",   "Ilhomovna",      "+998901234582", "Toshkent, Mirobod t., 7-uy",   "AB1234582", "Mirobod IIB"),
    ("Kamol",     "Normatov",    "Suxrobovich",    "+998901234583", "Toshkent, Yangihayot t.",       "AB1234583", "Yangihayot IIB"),
    ("Barno",     "Yo'ldosheva", "Zafar qizi",     "+998901234584", "Toshkent, Zangiota t.",         "AB1234584", "Zangiota IIB"),
    ("Sherzod",   "Botirov",     "Murodovich",     "+998901234585", "Qo'qon, Navoiy ko'ch.",         "AB1234585", "Qo'qon IIB"),
    ("Lobar",     "Umarova",     "Xurshida qizi",  "+998901234586", "Toshkent, Kibray t., 2-uy",    "AB1234586", "Kibray IIB"),
    ("Doniyor",   "Ismoilov",    "Lazizovich",     "+998901234587", "Toshkent, Yunusobod t., 21-uy","AB1234587", "Yunusobod IIB"),
    ("Gavhar",    "Pulatova",    "Muxammad qizi",  "+998901234588", "Toshkent, Hamza ko'ch.",        "AB1234588", "Hamza IIB"),
    ("Rustam",    "Jurayev",     "Sanjarovich",    "+998901234589", "Jizzax, Sharq ko'ch.",          "AB1234589", "Jizzax IIB"),
    ("Mohira",    "Sobirov",     "Alisher qizi",   "+998901234590", "Toshkent, To'xtaboeva ko'ch.", "AB1234590", "Shayxontohur IIB"),
    ("Akbar",     "Qurbonov",    "Dilshodovich",   "+998901234591", "Toshkent, Oqqo'rg'on t.",       "AB1234591", "Oqqo'rg'on IIB"),
    ("Nasiba",    "Hamidova",    "Bekzod qizi",    "+998901234592", "Qarshi, Nishon ko'ch.",         "AB1234592", "Qarshi IIB"),
    ("Eldor",     "Muxtorov",    "Farruxovich",    "+998901234593", "Toshkent, Qorasaroy ko'ch.",   "AB1234593", "Yakkasaroy IIB"),
    ("Sabohat",   "Tojiboyeva",  "Husan qizi",     "+998901234594", "Toshkent, Parkent t.",          "AB1234594", "Parkent IIB"),
    ("Muzaffar",  "Obloqulov",   "Olimovich",      "+998901234595", "Toshkent, Zangiota t., 9-uy",  "AB1234595", "Zangiota IIB"),
    ("Dilrabo",   "Asqarova",    "Jahongir qizi",  "+998901234596", "Toshkent, Uchtepa t., 18-uy",  "AB1234596", "Uchtepa IIB"),
]

# ── Sotuvchilar ───────────────────────────────────────────────────────────────
SELLERS = [
    ("seller1", "Alisher",  "Karimov",   "seller1@imobile.uz", "+998901111111"),
    ("seller2", "Ziyoda",   "Rahmonova", "seller2@imobile.uz", "+998901111112"),
    ("seller3", "Sanjar",   "Toshpulov", "seller3@imobile.uz", "+998901111113"),
]


def random_imei():
    """15 xonali tasodifiy IMEI raqami."""
    return ''.join([str(random.randint(0, 9)) for _ in range(15)])


class Command(BaseCommand):
    help = "Demo ma'lumotlarni bazaga yuklaydi (bir oylik savdo tarixi)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Demo ma'lumotlar yuklanmoqda..."))

        # 1. Sotuvchilar
        sellers = self._create_sellers()

        # 2. Mahsulotlar
        products = self._create_products()

        # 3. Mijozlar
        customers = self._create_customers()

        # 4. Savdolar (30 kun)
        self._create_sales(sellers, products, customers)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅  Demo ma'lumotlar muvaffaqiyatli yuklandi!\n"
            f"   Sotuvchilar : {len(sellers)}\n"
            f"   Mahsulotlar : {len(products)}\n"
            f"   Mijozlar    : {len(customers)}\n"
        ))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _create_sellers(self):
        sellers = []
        for username, first, last, email, phone in SELLERS:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults=dict(
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone_number=phone,
                    role='seller',
                    is_active=True,
                )
            )
            if created:
                user.set_password("seller123")
                user.save()
            sellers.append(user)
        self.stdout.write(f"  → {len(sellers)} ta sotuvchi")
        return sellers

    def _create_products(self):
        products = []
        for brand, model, price, stock, warranty in PRODUCTS:
            imei = random_imei()
            # Uniqligi uchun bir necha urinish
            for _ in range(10):
                try:
                    prod, created = Product.objects.get_or_create(
                        brand=brand,
                        model=model,
                        defaults=dict(
                            imei=imei,
                            price=Decimal(str(price)),
                            stock_quantity=stock,
                            warranty_months=warranty,
                            description=f"{brand} {model} — original, kafolat bilan",
                            is_active=True,
                        )
                    )
                    products.append(prod)
                    break
                except Exception:
                    imei = random_imei()
        self.stdout.write(f"  → {len(products)} ta mahsulot")
        return products

    def _create_customers(self):
        customers = []
        today = date.today()
        for i, (fn, ln, mn, phone, addr, passport, issued_by) in enumerate(CUSTOMERS):
            cust, _ = Customer.objects.get_or_create(
                phone_number=phone,
                defaults=dict(
                    first_name=fn,
                    last_name=ln,
                    middle_name=mn,
                    email=f"customer{i+1}@mail.com",
                    address=addr,
                    passport_number=passport,
                    passport_issued_date=today - timedelta(days=random.randint(365, 3650)),
                    passport_issued_by=issued_by,
                    is_active=True,
                )
            )
            customers.append(cust)
        self.stdout.write(f"  → {len(customers)} ta mijoz")
        return customers

    def _create_sales(self, sellers, products, customers):
        """Oxirgi 30 kun uchun kunlik 3–8 ta savdo yaratadi."""
        today = date.today()
        total_sales = 0

        # Savdolarni o'chirmaslik uchun mavjudlarni tekshiramiz
        if Sale.objects.exists():
            self.stdout.write(self.style.WARNING("  ⚠  Savdolar allaqachon mavjud, yangilari qo'shilmoqda..."))

        for day_offset in range(30, 0, -1):
            sale_date = today - timedelta(days=day_offset)
            # Dam olish kunlari kamroq savdo
            daily_count = random.randint(2, 5) if sale_date.weekday() >= 5 else random.randint(4, 9)

            for _ in range(daily_count):
                product = random.choice(products)

                # Omborga yetarli mahsulot bo'lsa sotamiz
                if product.stock_quantity < 1:
                    product.stock_quantity = random.randint(5, 15)
                    product.save()

                customer   = random.choice(customers)
                seller     = random.choice(sellers)
                payment_type = random.choices(
                    ['cash', 'card', 'credit'],
                    weights=[45, 35, 20]
                )[0]

                base_price = product.price
                # Katta xaridlarda chegirma
                discount = Decimal('0')
                if random.random() < 0.15:           # 15% ehtimollik
                    pct = random.choice([2, 3, 5])
                    discount = (base_price * pct / 100).quantize(Decimal('1'))

                total = base_price - discount

                if payment_type == 'cash':
                    paid = total
                elif payment_type == 'card':
                    paid = total
                else:  # credit
                    # Nasiyada 30–70% avans
                    pct_paid = random.randint(30, 70)
                    paid = (total * pct_paid / 100).quantize(Decimal('1'))

                # Stock ni qo'lda kamaytirmasdan Sale.save() qiladi,
                # lekin date auto_now_add — uni o'zgartirishimiz kerak
                product.stock_quantity += 1   # save() ichida kamaytiriladi
                product.save(update_fields=['stock_quantity'])

                sale = Sale(
                    customer=customer,
                    product=product,
                    seller=seller,
                    quantity=1,
                    price_per_unit=base_price,
                    discount_amount=discount,
                    total_price=total,
                    payment_type=payment_type,
                    paid_amount=paid,
                    is_completed=(payment_type != 'credit'),
                )
                sale.save()

                # Savdo sanasini to'g'rilaymiz (auto_now_add ni bypass)
                Sale.objects.filter(pk=sale.pk).update(date=sale_date)

                # Nasiya savdolarda qisman to'lovlar qo'shamiz
                if payment_type == 'credit' and paid < total:
                    remaining = total - paid
                    # 50% ehtimollik bilan qo'shimcha to'lov bo'lgan
                    if random.random() < 0.5:
                        extra_pay = (remaining * Decimal(str(random.randint(20, 60))) / 100).quantize(Decimal('1'))
                        payment = Payment(
                            sale=sale,
                            amount=extra_pay,
                            payment_method=random.choice(['cash', 'card', 'transfer']),
                            notes="Qisman to'lov",
                            created_by=seller,
                        )
                        payment.save()
                        pay_date = sale_date + timedelta(days=random.randint(1, day_offset - 1 or 1))
                        Payment.objects.filter(pk=payment.pk).update(payment_date=pay_date)

                total_sales += 1

        self.stdout.write(f"  → {total_sales} ta savdo (30 kunlik)")
