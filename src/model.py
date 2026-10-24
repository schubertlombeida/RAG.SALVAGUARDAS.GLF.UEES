"""BM25 y E5 con corpus idéntico; puntuaciones no calibradas como probabilidad."""
import math
import re
import unicodedata
from collections import Counter
from urllib.parse import urlsplit
import numpy as np
import requests
from .data_processing import validate_records

def tokens(text):
    text = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))
    stop = set("a al de del el la las los un una unos unas y o en por para con que se es sobre como cuales".split())
    return [x for x in re.findall(r"[a-z0-9]+", text) if len(x) > 1 and x not in stop]

class BM25:
    name = "BM25"
    def __init__(self, records, k1=1.5, b=.75):
        if k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("Parámetros BM25 inválidos")
        self.records = validate_records(records)
        self.k1, self.b = k1, b
        self.counts = [Counter(tokens(row["text"])) for row in records]
        self.lengths = [sum(count.values()) for count in self.counts]
        self.average = sum(self.lengths) / len(records)
        if not self.average:
            raise ValueError("Corpus sin términos")
        df = Counter(term for count in self.counts for term in count)
        self.idf = {term: math.log(1 + (len(records) - n + .5) / (n + .5)) for term, n in df.items()}

    def search(self, query, limit=5):
        if limit < 1:
            raise ValueError("Top k debe ser positivo")
        scored = []
        for i, count in enumerate(self.counts):
            score = sum(self.idf.get(term, 0) * count.get(term, 0) * (self.k1 + 1) /
                        (count.get(term, 0) + self.k1 * (1-self.b+self.b*self.lengths[i]/self.average))
                        for term in set(tokens(query)))
            if score > 0:
                scored.append((score, i))
        return [dict(self.records[i], score=round(score, 6))
                for score, i in sorted(scored, key=lambda x: (-x[0], x[1]))[:limit]]

class E5Endpoint:
    name = "intfloat/multilingual-e5-small"
    batch_size = 8
    def __init__(self, records, endpoint, api_key="", transport=None):
        url = urlsplit(endpoint)
        if url.scheme != "https" or url.username or url.password or not url.hostname:
            raise ValueError("E5 requiere HTTPS")
        self.records = validate_records(records)
        self.endpoint, self.api_key = endpoint, api_key
        self.transport = transport or requests.post
        self.vectors = self.encode([row["text"] for row in records], "passage")

    def encode(self, texts, kind):
        rows = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start:start+self.batch_size]
            response = self.transport(self.endpoint, json={"inputs": batch, "kind": kind},
                                      headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                                      timeout=25, allow_redirects=False)
            response.raise_for_status()
            body = response.json()
            if body.get("model") != self.name:
                raise ValueError("Modelo E5 inesperado")
            values = np.asarray(body.get("embeddings"), dtype=float)
            if values.shape != (len(batch), 384) or not np.isfinite(values).all():
                raise ValueError("Embeddings E5 inválidos")
            norms = np.linalg.norm(values, axis=1, keepdims=True)
            if np.any(norms == 0):
                raise ValueError("Vector E5 nulo")
            rows.extend(values / norms)
        return np.asarray(rows)

    def search(self, query, limit=5):
        if not query.strip() or limit < 1:
            return []
        vector = self.encode([query], "query")[0]
        scores = self.vectors @ vector
        order = np.argsort(-scores, kind="stable")[:limit]
        return [dict(self.records[i], score=float(scores[i])) for i in order]
