import csv


def load_csv(path):
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


customers = load_csv("data/customers.csv")
orders = load_csv("data/orders.csv")

print("müşteri sayısı:", len(customers))
print("sipariş sayısı:", len(orders))

print(customers[0])
print(orders[0])

# CSV'den okunan her şey metin (string) gelir
print(type(orders[0]["unit_price"]))

# Toplam geliri hesaplayalım
total_revenue = 0
for order in orders:
    total_revenue += int(order["quantity"]) * float(order["unit_price"])
print("Toplam gelir:", round(total_revenue, 2))

# Kaç farklı müşteri sipariş vermiş?
ordering_customers = set()
for order in orders:
    ordering_customers.add(order["customer_id"])
print("Sipariş veren müşteri sayısı:", len(ordering_customers))