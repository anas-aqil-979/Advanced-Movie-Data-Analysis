import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast

# --- PAGE CONFIG ---
st.set_page_config(page_title="🎬 Advanced Movie Data Analysis", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    url = "https://github.com/anas-aqil-979/Advanced-Movie-Data-Analysis/releases/download/csv/movies_metadata.csv"
    df = pd.read_csv(url, low_memory=False)

    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['year'] = df['release_date'].dt.year
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce')
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')

    def parse_genres(x):
        try:
            genres = ast.literal_eval(x)
            if isinstance(genres, list):
                return [d.get('name') for d in genres if 'name' in d]
        except:
            return []
        return []

    df['genres_list'] = df['genres'].apply(parse_genres)
    return df


df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎛️ Filter Options")
all_genres = sorted(set(g for sublist in df['genres_list'] for g in sublist if isinstance(sublist, list)))
genre_filter = st.sidebar.multiselect("Select Genre(s)", all_genres)
year_range = st.sidebar.slider("Select Year Range", int(df['year'].min()), int(df['year'].max()), (1990, 2020))
min_votes = st.sidebar.slider("Minimum Vote Count", 0, 5000, 100)

filtered_df = df[
    (df['year'].between(year_range[0], year_range[1])) &
    (df['vote_count'] >= min_votes)
]

if genre_filter:
    filtered_df = filtered_df[filtered_df['genres_list'].apply(lambda x: any(g in x for g in genre_filter))]

# --- TOP METRICS ---
st.title("🎬 Advanced Movie Data Analysis Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Movies Count", len(filtered_df))
col2.metric("Average Rating", round(filtered_df['vote_average'].mean(), 2))
col3.metric("Total Revenue ($)", f"{filtered_df['revenue'].sum():,.0f}")
col4.metric("Average Runtime (min)", round(filtered_df['runtime'].mean(), 1))

# --- SECTION 1: RATING ANALYSIS ---
st.header("⭐ Rating Analysis")
col1, col2 = st.columns(2)
fig1 = px.histogram(filtered_df, x="vote_average", nbins=20, title="Distribution of Movie Ratings", color_discrete_sequence=['#FF6347'])
fig2 = px.scatter(filtered_df, x="vote_count", y="vote_average", title="Vote Count vs Rating", color="vote_average", size="vote_count", hover_name="title", color_continuous_scale="viridis")
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

# --- SECTION 2: FINANCIAL ANALYSIS ---
st.header("💰 Financial Analysis")
fig3 = px.scatter(filtered_df, x="budget", y="revenue", size="vote_average", color="vote_average", title="Budget vs Revenue Scatter Plot", hover_name="title", log_x=True, log_y=True)
st.plotly_chart(fig3, use_container_width=True)

col1, col2 = st.columns(2)
top_revenue = filtered_df.nlargest(20, 'revenue')
fig4 = px.bar(top_revenue, x="revenue", y="title", orientation='h', title="Top 20 Movies by Revenue")
col1.plotly_chart(fig4, use_container_width=True)

revenue_by_genre = (
    filtered_df.explode('genres_list')
    .groupby('genres_list')['revenue']
    .mean()
    .reset_index()
    .sort_values('revenue', ascending=False)
)
fig5 = px.bar(revenue_by_genre, x="genres_list", y="revenue", title="Average Revenue by Genre")
col2.plotly_chart(fig5, use_container_width=True)

# --- SECTION 3: TEMPORAL ANALYSIS ---
st.header("📅 Temporal Analysis")
movies_per_year = filtered_df.groupby('year').size().reset_index(name='count')
fig6 = px.area(movies_per_year, x='year', y='count', title="Number of Movies Released per Year", color_discrete_sequence=['#6C63FF'])
st.plotly_chart(fig6, use_container_width=True)

avg_rating_per_year = filtered_df.groupby('year')['vote_average'].mean().reset_index()
fig7 = px.line(avg_rating_per_year, x='year', y='vote_average', title="Average Rating Over the Years", markers=True)
st.plotly_chart(fig7, use_container_width=True)

# --- SECTION 4: CORRELATION ---
st.header("📊 Correlation and Insights")
corr = filtered_df[['budget', 'revenue', 'vote_average', 'vote_count', 'runtime']].corr()
fig8 = px.imshow(corr, text_auto=True, title="Correlation Heatmap of Numeric Features")
st.plotly_chart(fig8, use_container_width=True)

# --- FINAL SECTION ---
st.subheader("🎞️ Top 10 Highest Rated Movies")
st.dataframe(filtered_df[['title', 'year', 'vote_average', 'revenue', 'genres_list']].nlargest(10, 'vote_average'))
