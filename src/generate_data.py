import random
import csv
from datetime import date, timedelta

random.seed(33) # Set the seed for reproducibility

END_DATE = date(2026,9,30)  #"Bugün" yerine sabit bir bitiş tarihi. date.today() kullansaydık her gün farklı tarih çıkardı ve seed'in anlamı kalmazdı.

START_DATE = END_DATE - timedelta(days=730)   # siparişler son 2 yılı kapsıyor

CATEGORIES = {
    'Gıda': (50, 400),
    'Giyim': (250, 1500),
    'Kozmetik': (100, 900),
    'Ev & Yaşam': (150, 3000),
    'Kitap & Kırtasiye': (40, 400),
    'Elektronik': (1500, 25000),
}
# Yukarıdaki kategorilerle aynı sırada: Gıda en sık, Elektronik en nadir satılır
CATEGORY_WEIGHTS = [35, 22, 14, 13, 9, 7]

def generate_customers():
    customers = []
    cities = ['İstanbul', 'Ankara', 'Mersin', 'Tekirdağ']

    for i in range(500):
         
        age = int(random.gauss(30, 8))

        if age < 18:
            age = 18

        if age > 65:
            age = 65

        days_ago = random.randint(0, 365 * 3)  # Random number of days ago (up to 3 years)
        signup_date = END_DATE - timedelta(days=days_ago)

        customer = {
            'customer_id': i+1,
            'age': age,
            'city': random.choices(
                cities, 
                weights=[50, 30, 15, 5], 
                k=1)
                [0],
            'signup_date': signup_date

        }
        customers.append(customer)
    return customers

def generate_orders(customers, n_orders=3000):
    category_names = list(CATEGORIES.keys())

    # random.expovariate(1): Çoğu sayının küçük, birkaçının büyük olduğu rastgele sayılar üretir
    activity = [random.expovariate(1) for _ in customers]

    orders = []
    for _ in range(n_orders):
        customer = random.choices(
            customers, 
            weights=activity, 
            k=1)[0]

        # Sipariş, kayıt tarihinden önce olamaz
        first_day = max(customer['signup_date'], START_DATE)
        days_range = (END_DATE - first_day).days
        order_date = first_day + timedelta(days=random.randint(0, days_range))

        category = random.choices(category_names, weights=CATEGORY_WEIGHTS, k=1)[0]
        min_price, max_price = CATEGORIES[category]
        unit_price = round(random.uniform(min_price, max_price), 2)

        # Elektronikten genelde tek adet alınır
        if category == 'Elektronik':
            quantity = 1
        else:
            quantity = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5], k=1)[0]

        orders.append({
            'customer_id': customer['customer_id'],
            'order_date': order_date,
            'category': category,
            'quantity': quantity,
            'unit_price': unit_price
        })

    # Tarihe göre sırala, sonra sıraya göre order_id ver
    orders.sort(key=lambda order: order['order_date'])
    for i, order in enumerate(orders):
        order['order_id'] = i + 1

    return orders

customers = generate_customers()

with open("data/customers.csv", "w", newline="", encoding="utf-8") as file:
#with bloktan çıkınca dosyayı otomatik kapatır, hata çıksa bile. with olmasaydı sonuna file.close() yazman gerekirdi.
#encoding="utf-8": İ, ğ, ş gibi Türkçe karakterlerin bozulmaması için
    
    fieldnames = ["customer_id", "age", "city", "signup_date"]
    #fieldnames hem sütunların sırasını hem de hangi anahtarların yazılacağını belirler. Sözlükte fieldnames'te olmayan bir anahtar varsa hata verir.
    writer = csv.DictWriter(file, fieldnames=fieldnames)#DictWriter, sözlükleri CSV satırlarına çevirir

    writer.writeheader()#writeheader() ilk satıra sütun adlarını yazar (customer_id,age,city).
    writer.writerows(customers)#writerows(liste) listedeki her sözlüğü bir satır olarak yazar. writerow() ise tek bir satır yazar.

orders = generate_orders(customers)

with open("data/orders.csv", "w", newline="", encoding="utf-8") as file:
    fieldnames = ["order_id", "customer_id", "order_date", "category", "quantity", "unit_price"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(orders)    