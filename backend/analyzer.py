import numpy as np
from sklearn.decomposition import PCA
def run_residue_pca(residue_data, feature_names=None):
    data = np.array(residue_data)
    if data.ndim != 2 or data.shape[1] < 2:
        return {"error": "Insufficient data for PCA. Need at least 2 columns (ID + Feature)"}
    residue_nos = data[:, 0]
    features = data[:, 1:].astype(float) # All but first column
    n_features = features.shape[1]
    if not feature_names or len(feature_names) != n_features:
        feature_names = [f"Col {i+1}" for i in range(n_features)]
    mean = np.mean(features, axis=0)
    std = np.std(features, axis=0)
    std[std == 0] = 1.0
    features_scaled = (features - mean) / std
    n_components = min(3, n_features, features.shape[0])
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(features_scaled)
    loadings = pca.components_ 
    variance_ratio = pca.explained_variance_ratio_.tolist()
    from scipy.stats import chi2
    eigenvalues = pca.explained_variance_
    mahalanobis_sq = np.sum((scores**2) / eigenvalues, axis=1)
    mahalanobis_dist = np.sqrt(mahalanobis_sq)
    p_values = chi2.sf(mahalanobis_sq, df=n_components)
    results = []
    for i in range(n_components):
        results.append({
            "pc_index": i + 1,
            "scores": scores[:, i].tolist(),
            "loadings": {name: float(val) for name, val in zip(feature_names, loadings[i])},
            "success": False 
        })
    return {
        "results": results,
        "variance_ratio": variance_ratio,
        "residue_nos": residue_nos.tolist(),
        "feature_names": feature_names,
        "mahalanobis_dist": mahalanobis_dist.tolist(),
        "p_values": p_values.tolist()
    }