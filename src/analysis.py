import pandas as pd
import os
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)

customers = pd.read_csv("data/customers.csv", parse_dates=["signup_date"])
orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])

orders["total_amount"] = orders["quantity"] * orders["unit_price"]

#print(customers.head())
#print(orders.head()) #-->head() tablonun ilk 5 satırını gösterir.

#orders.info()#-->Veri seti hakkında bilgi verir:Kaç satır var?Kaç sütun var?Sütunların veri tipleri ne?Eksik değerler var mı?
#print(orders.describe()) #-->Sayısal sütunlar için istatistiksel özet verir:Ortalama (mean)-Standart sapma (std)-Minimum ve maksimum

#print("Toplam gelir:", round(orders["total_amount"].sum(), 2))
#print(orders.isna().sum())

# 1. Kategori bazında gelir
category_revenue = (
    orders.groupby("category")["total_amount"]
    .sum()
    .sort_values(ascending=False)
)
print("Kategori bazında gelir:")
print(category_revenue.round(2))

# 2. En çok harcayan 10 müşteri
top_spenders = (
    orders.groupby("customer_id")["total_amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
print("\nEn çok harcayan 10 müşteri:")
print(top_spenders.round(2))

# 3. En çok sipariş veren 10 müşteri
top_buyers = (
    orders.groupby("customer_id")["order_id"]
    .count()
    .sort_values(ascending=False)
    .head(10)
)
print("\nEn çok sipariş veren 10 müşteri:")
print(top_buyers)

# 4. Ortalama sipariş tutarı ve sipariş başına ürün sayısı
avg_order_value = orders["total_amount"].mean()
avg_items_per_order = orders["quantity"].mean()
print("\nOrtalama sipariş tutarı:", round(avg_order_value, 2))
print("Sipariş başına ortalama ürün sayısı:", round(avg_items_per_order, 2))

# 5. Aylık satış trendi
monthly_revenue = (
    orders.groupby(orders["order_date"].dt.to_period("M"))["total_amount"]
    .sum()
)
print("\nAylık gelir:")
print(monthly_revenue.round(2))

# 6. Şehir bazında gelir
orders_with_city = orders.merge(customers[["customer_id", "city"]], on="customer_id") #merge: SQL'deki JOIN'in Pandas karşılığı.
city_revenue = (
    orders_with_city.groupby("city")["total_amount"]
    .sum()
    .sort_values(ascending=False)
)
print("\nŞehir bazında gelir:")
print(city_revenue.round(2))

# 7. Şehir bazında müşteri sayısı ve müşteri başına gelir
customers_per_city = customers.groupby("city")["customer_id"].count()
revenue_per_customer = (city_revenue / customers_per_city).sort_values(ascending=False)
print("\nŞehir başına müşteri sayısı:")
print(customers_per_city)
print("\nŞehir bazında müşteri başına gelir:")
print(revenue_per_customer.round(2))

# 8. Tekrar alışveriş yapan müşteriler
orders_per_customer = orders.groupby("customer_id")["order_id"].count()
total_customers = len(customers)
ordering_customers = len(orders_per_customer)
repeat_customers = (orders_per_customer >= 2).sum()

print("\nHiç sipariş vermeyen müşteri sayısı:", total_customers - ordering_customers)
print("Tekrar alışveriş yapan müşteri oranı:",
      round(repeat_customers / ordering_customers * 100, 1), "%")
print(orders_per_customer.describe())

# 9. Müşteri segmentasyonu
customer_stats = (
    orders.groupby("customer_id")
    .agg(
        total_spent=("total_amount", "sum"),
        order_count=("order_id", "count"),
        last_order_date=("order_date", "max"),
    )
    .reset_index()
)

segments = customers.merge(customer_stats, on="customer_id", how="left")

reference_date = pd.Timestamp("2026-09-30")  # generate_data.py'deki END_DATE ile aynı
segments["days_since_signup"] = (reference_date - segments["signup_date"]).dt.days
segments["days_since_last_order"] = (reference_date - segments["last_order_date"]).dt.days

high_value_threshold = segments["total_spent"].quantile(0.90)
frequent_threshold = segments["order_count"].quantile(0.75)


def assign_segment(row):
    if row["days_since_signup"] <= 90:
        return "New"
    if pd.isna(row["order_count"]):
        return "No Purchase"
    if row["days_since_last_order"] > 180:
        return "Inactive"
    if row["total_spent"] >= high_value_threshold:
        return "High-value"
    if row["order_count"] >= frequent_threshold:
        return "Frequent"
    return "Regular"


segments["segment"] = segments.apply(assign_segment, axis=1)

print("\nHigh-value eşiği (90. yüzdelik):", round(high_value_threshold, 2), "TL")
print("Frequent eşiği (75. yüzdelik):", frequent_threshold, "sipariş")

segment_summary = segments.groupby("segment").agg(
    customer_count=("customer_id", "count"),
    revenue=("total_spent", "sum"),
)
segment_summary["revenue_share_%"] = (
    segment_summary["revenue"] / segment_summary["revenue"].sum() * 100
).round(1)
print(segment_summary.sort_values("revenue", ascending=False))

# 10. Grafikler
os.makedirs("images", exist_ok=True)

# Grafik 1: Kategori bazında gelir
fig, ax = plt.subplots(figsize=(8, 5))
(category_revenue.sort_values() / 1_000_000).plot(kind="barh", ax=ax)
ax.set_title("Kategori Bazında Gelir")
ax.set_xlabel("Gelir (milyon TL)")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig("images/category_revenue.png", dpi=150)
plt.close(fig)

# Grafik 2: Aylık gelir (ilk ay sadece 1 günlük olduğu için çıkarıldı)
monthly = monthly_revenue.iloc[1:]
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly.index.astype(str), monthly.values / 1000, marker="o")
ax.set_title("Aylık Gelir")
ax.set_ylabel("Gelir (bin TL)")
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
fig.savefig("images/monthly_revenue.png", dpi=150)
plt.close(fig)

# Grafik 3: Segmentlere göre müşteri sayısı
fig, ax = plt.subplots(figsize=(8, 5))
segment_summary["customer_count"].sort_values(ascending=False).plot(kind="bar", ax=ax)
ax.set_title("Segmentlere Göre Müşteri Sayısı")
ax.set_xlabel("")
ax.set_ylabel("Müşteri sayısı")
plt.xticks(rotation=0)
fig.tight_layout()
fig.savefig("images/segments.png", dpi=150)
plt.close(fig)

print("\nGrafikler images/ klasörüne kaydedildi.")