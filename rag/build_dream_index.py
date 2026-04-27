from pathlib import Path
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


APP_DIR = Path(r"E:\Desktop\AIDM\project\tarot_dream_app")
DREAM_DIR = APP_DIR / "data" / "dream"

CHUNKS_PATH = DREAM_DIR / "dream_chunks.json"
INDEX_PATH = DREAM_DIR / "dream_index.faiss"
META_PATH = DREAM_DIR / "dream_index_meta.json"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main():
    print(f"[INFO] 读取 chunks: {CHUNKS_PATH}")

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"未找到 {CHUNKS_PATH}")

    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    texts = [item["text"] for item in chunks]

    print(f"[INFO] 共 {len(texts)} 条文本")
    print("[INFO] 开始加载 embedding 模型...")

    model = SentenceTransformer(MODEL_NAME)

    print("[INFO] 开始生成向量...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(embeddings, dtype="float32")
    dim = embeddings.shape[1]

    print(f"[INFO] 向量维度: {dim}")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] 已生成索引: {INDEX_PATH}")
    print(f"[OK] 已生成元数据: {META_PATH}")
    print(f"[OK] 共写入 {index.ntotal} 条向量")


if __name__ == "__main__":
    main()