# 7. cluster_analysis.py
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

def run_kmeans(df, n_clusters=3):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df.dropna())
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df_clustered = df.copy()
    df_clustered['cluster'] = labels
    return df_clustered
