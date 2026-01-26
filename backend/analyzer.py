import numpy as np
from sklearn.decomposition import PCA

def run_residue_pca(residue_data, feature_names=None):
    """
    Performs PCA on multi-featured residue data.
    residue_data: List of lists [residue_id, feature1, feature2, ..., featureN]
    """
    data = np.array(residue_data)
    if data.ndim != 2 or data.shape[1] < 2:
        return {"error": "Insufficient data for PCA. Need at least 2 columns (ID + Feature)"}

    residue_nos = data[:, 0]
    features = data[:, 1:].astype(float) # All but first column
    n_features = features.shape[1]
    
    # Defaults for header names if not provided
    if not feature_names or len(feature_names) != n_features:
        feature_names = [f"Col {i+1}" for i in range(n_features)]
    
    # Standardize features (Z-score normalization)
    # Manual standardization to avoid dependency if needed, but sklearn is in requirements
    mean = np.mean(features, axis=0)
    std = np.std(features, axis=0)
    # Avoid division by zero
    std[std == 0] = 1.0
    features_scaled = (features - mean) / std
    
    # PCA
    n_components = min(3, n_features, features.shape[0])
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(features_scaled)
    loadings = pca.components_ 
    variance_ratio = pca.explained_variance_ratio_.tolist()
    
    results = []
    for i in range(n_components):
        results.append({
            "pc_index": i + 1,
            "scores": scores[:, i].tolist(),
            "loadings": {name: float(val) for name, val in zip(feature_names, loadings[i])},
            "success": False # "success" triggers Titration fit in frontend; FALSE triggers Residue view
        })
        
    return {
        "results": results,
        "variance_ratio": variance_ratio,
        "residue_nos": residue_nos.tolist(),
        "feature_names": feature_names
    }
