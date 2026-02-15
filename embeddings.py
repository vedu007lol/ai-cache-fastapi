import hashlib
import math

# Simple deterministic embedding using hash
def embed(text: str):
    h = hashlib.md5(text.encode()).hexdigest()
    return [int(h[i:i+2], 16)/255 for i in range(0, 32, 2)]

def similarity(vec1, vec2):
    dot = sum(a*b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a*a for a in vec1))
    norm2 = math.sqrt(sum(b*b for b in vec2))
    return dot / (norm1 * norm2)
