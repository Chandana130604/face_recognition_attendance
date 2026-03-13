import numpy as np
import joblib
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_DIR = BASE_DIR / "data" / "embeddings"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Load embeddings and labels
embeddings = np.load(EMBEDDINGS_DIR / "embeddings.npy")
labels = np.load(EMBEDDINGS_DIR / "labels.npy")

# Split data
X_train, X_test, y_train, y_test = train_test_split(embeddings, labels, test_size=0.2, random_state=42, stratify=labels)

# Train SVM classifier
clf = SVC(kernel='linear', probability=True, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=np.unique(labels).astype(str)))

# Save model and label map
joblib.dump(clf, MODEL_DIR / "classifier.pkl")
# Also save label map (already done, but copy for consistency)
import shutil
shutil.copy(EMBEDDINGS_DIR / "label_map.txt", MODEL_DIR / "label_map.txt")
print("Classifier saved.")