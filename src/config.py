# Paths
DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"
EMBEDDINGS_PATH = "data/embeddings/embeddings.npy"
LABELS_PATH = "data/embeddings/labels.npy"

# Face detection settings
DETECTOR_BACKEND = "mtcnn"  # or "dlib", "opencv"
FACE_ALIGNMENT = True
TARGET_SIZE = (160, 160)    # Input size for FaceNet

# Recognition settings
SIMILARITY_THRESHOLD = 0.5   # Cosine distance threshold
USE_GPU = True

# Camera settings
CAMERA_ID = 0
FRAME_SKIP = 2               # Process every nth frame