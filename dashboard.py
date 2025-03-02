import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import folium
sns.set(style='dark')


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_count_product_category_df(df):
    count_product_category_df = df.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=False).reset_index()
    return count_product_category_df

all_df = pd.read_csv("./data/clean_data.csv")

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
count_product_category_df = create_count_product_category_df(main_df)

st.header('E-commerce Dashboard')

st.subheader('Pernjualan Harian')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Penjualan", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "R$", locale='es_CO')
    st.metric("Total Pendapatan", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Produk yang paling banyak dan paling sedikit terjual")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="product_category_name_english",
            data=count_product_category_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk yang paling banyak terjual", loc="center", fontsize=15)
ax[0].tick_params(axis='y', labelsize=12)

sns.barplot(x="order_id", y="product_category_name_english", data=count_product_category_df.sort_values(
    by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk yang paling sedikit terjual", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle(
    "Produk yang paling banyak dan paling sedikit terjual", fontsize=20)

st.pyplot(fig)

st.subheader("Tingkat kepuasan pelanggan")

order_counts = main_df.groupby(by="satisfaction_status").order_id.nunique().sort_values(ascending=False)
explode = [0.1 if i == order_counts.idxmax() else 0 for i in order_counts.index]

fig = plt.figure(figsize=(6, 6))
plt.pie(order_counts, labels=order_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"), explode=explode)
plt.title('Tingkat kepuasan pelanggan')

st.pyplot(fig)

plt.suptitle(
    "Lokasi geografis pelanggan", fontsize=20)

customer_order_location = main_df.groupby(by="customer_state").order_id.nunique().sort_values(ascending=False).reset_index()

geojson_url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'

m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

folium.Choropleth(
    geo_data=geojson_url,
    name='choropleth',
    data=customer_order_location,
    columns=['customer_state', 'order_id'],
    key_on='feature.properties.sigla',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Value'
).add_to(m)

folium.LayerControl().add_to(m)

st.subheader("Lokasi geografis pelanggan")
st_folium = st.components.v1.html(m._repr_html_(), height=600)


st.caption('Copyright (c) Oka Widhyartha 2025')
