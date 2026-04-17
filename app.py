import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

st.set_page_config(page_title="World Development Cluster Analysis", layout="wide")

st.title("🌍 Cluster Analysis – World Development Indicators")
st.markdown("An unsupervised machine learning project that groups countries by socio-economic development patterns using K-Means Clustering.")

# ---- Load dataset ----
@st.cache_data
def load_data():
    df = pd.read_excel("wdi_dataset.xlsx", engine='openpyxl')
    return df

try:
    df = load_data()
    st.success("✅ Dataset loaded successfully!")
except Exception as e:
    st.error(f"❌ Error loading file: {e}")
    st.stop()

# ---- Data Preview ----
st.subheader("📊 Data Preview")
st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")
st.dataframe(df.head())

# ---- Data Cleaning ----
st.subheader("🧹 Data Cleaning")

# Fix: clean string columns only, not the whole dataframe
for col in df.columns:
    if df[col].dtype == object and col != 'Country':
        df[col] = df[col].astype(str).str.replace('[$,%]', '', regex=True).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')

df.fillna(df.median(numeric_only=True), inplace=True)
st.success("✅ Missing values handled successfully.")

# ---- Feature Selection ----
st.subheader("🔧 Feature Selection")
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
selected_features = st.multiselect(
    "Select features for clustering:",
    options=numeric_cols,
    default=numeric_cols[:6]
)

if len(selected_features) < 2:
    st.warning("Please select at least 2 features.")
    st.stop()

# ---- Correlation Heatmap ----
st.subheader("🔥 Correlation Heatmap")
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(df[selected_features].corr(), annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# ---- Scaling ----
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df[selected_features])

# ---- Elbow Method ----
st.subheader("📈 Elbow Method – Optimal K")
inertia = []
k_range = range(2, 11)
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(scaled_data)
    inertia.append(km.inertia_)

fig2, ax2 = plt.subplots()
ax2.plot(k_range, inertia, marker='o')
ax2.set_xlabel("Number of Clusters (K)")
ax2.set_ylabel("Inertia")
ax2.set_title("Elbow Method")
st.pyplot(fig2)

# ---- K Selection ----
k = st.slider("Select number of clusters (K):", min_value=2, max_value=10, value=4)

# ---- KMeans Clustering ----
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(scaled_data)

# ---- PCA Visualization ----
st.subheader("🗺️ Cluster Visualization (PCA)")
pca = PCA(n_components=2)
pca_result = pca.fit_transform(scaled_data)
df['PCA1'] = pca_result[:, 0]
df['PCA2'] = pca_result[:, 1]

fig3, ax3 = plt.subplots(figsize=(10, 6))
scatter = ax3.scatter(df['PCA1'], df['PCA2'], c=df['Cluster'], cmap='tab10', alpha=0.7)
ax3.set_xlabel("PCA Component 1")
ax3.set_ylabel("PCA Component 2")
ax3.set_title(f"K-Means Clustering (K={k})")
plt.colorbar(scatter, ax=ax3, label='Cluster')
st.pyplot(fig3)

# ---- Cluster Summary ----
st.subheader("📋 Cluster Summary")
cluster_summary = df.groupby('Cluster')[selected_features].mean().round(2)
st.dataframe(cluster_summary)

# ---- Country-wise Cluster Table ----
st.subheader("🌐 Countries by Cluster")
if 'Country' in df.columns:
    for i in range(k):
        with st.expander(f"🔵 Cluster {i} Countries"):
            countries = df[df['Cluster'] == i]['Country'].values
            st.write(", ".join(map(str, countries)))

st.markdown("---")
st.markdown("👤 **Author:** Navaneethadheeravath | 📧 Navaneethadheeravath19@gmail.com")
