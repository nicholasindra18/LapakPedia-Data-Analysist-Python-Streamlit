import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_orders_df(df):
	monthly_orders_df = df.resample(rule= 'D', on='order_purchase_timestamp').agg({
    	"order_id": "nunique",
    	"price" : "sum"
	})

	monthly_orders_df = monthly_orders_df.reset_index()
	monthly_orders_df.rename(columns={
  	  "order_id": "order_count",
  	  "price": "revenue"
	}, inplace = True)

	return monthly_orders_df

def create_active_buyers_df(df):
	active_buyers_df = df.groupby(by="status").customer_id.nunique().reset_index()
	active_buyers_df.rename(columns={
		"customer_id" : "customer_count"
	})
	return active_buyers_df

def create_by_state_df(df):
	by_state_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
	by_state_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
	return by_state_df

def create_by_city_df(df):
	by_city_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
	by_city_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
	return by_city_df

def create_average_delivery_time_df(df):
	average_delivery_time_df = df.groupby('customer_city').delivery_time.mean().sort_values(ascending=False).reset_index()
	return average_delivery_time_df

def create_average_review_product_df(df):
	average_review_product_df = df.groupby('product_category_name').agg({
  		"product_id" : "nunique",
  		"review_score" : "mean"                                                                                                             
	})

	return average_review_product_df


def create_rfm_df(df):
	rfm_df = df.groupby('customer_id', as_index = False).agg({
	    "order_purchase_timestamp": "max",
	    "order_id": "nunique",
	    "price": "sum"
	})

	rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

	rfm_df.max_order_timestamp = rfm_df.max_order_timestamp.dt.date
	recent_date = df.order_purchase_timestamp.dt.date.max()
	rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
	rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

	return rfm_df
	

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_carrier_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1518281361980-b26bfd556770?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1005&q=80")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date, max_value=max_date,
        value=[min_date, max_date]
    )


main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]



monthly_orders_df = create_monthly_orders_df(main_df)
active_buyers_df = create_active_buyers_df(main_df)
by_state_df = create_by_state_df(main_df)
by_city_df = create_by_city_df(main_df)
average_delivery_time_df = create_average_delivery_time_df(main_df)
average_review_product_df = create_average_review_product_df(main_df)
rfm_df = create_rfm_df(main_df)


st.header('LapakPedia Collection Dashboard :star:')



#SECTION 1
st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)



#SECTION 2
st.subheader("Average Delivery Time")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x = "delivery_time", y = "customer_city" , data=average_delivery_time_df.sample(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Days", fontsize=30)
ax[0].set_title("Worst Delivery Time", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x = "delivery_time", y = "customer_city", data=average_delivery_time_df.sort_values(by="delivery_time", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Days", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Best Delivery Time", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)



#SECTION 3
st.subheader("Customer Demographics")
 
col1, col2 = st.columns(2)
 
with col1:
	fig, ax = plt.subplots(figsize=(20, 20))
	colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
	sns.barplot(
	    x="customer_count", 
	    y="customer_state",
	    data = by_state_df.sort_values(by="customer_count", ascending=False),
	    palette=colors,
	    ax=ax
	)
	ax.set_title("Number of Customer by States", loc="center", fontsize=30)
	ax.set_ylabel(None)
	ax.set_xlabel(None)
	ax.tick_params(axis='y', labelsize=20)
	ax.tick_params(axis='x', labelsize=15)
	st.pyplot(fig)
 
with col2:
	fig, ax = plt.subplots(figsize=(20, 23.45))
	colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
	sns.barplot(
	    x="customer_count", 
	    y="customer_city",
	    data = by_city_df.sample(20),
	    palette=colors,
	    ax=ax
	)
	ax.set_title("Number of Customer by City", loc="center", fontsize=30)
	ax.set_ylabel(None)
	ax.set_xlabel(None)
	ax.tick_params(axis='y', labelsize=20)
	ax.tick_params(axis='x', labelsize=15)
	st.pyplot(fig)



#SECTION 4
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=20)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=60)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=20)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].set_xticklabels(ax[0].get_xticklabels(), rotation=60)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=20)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
ax[2].set_xticklabels(ax[0].get_xticklabels(), rotation=60)
 
st.pyplot(fig)


st.caption('Copyright (c) Nicholas Indradjaja 2023')

 