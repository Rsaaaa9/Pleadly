# Pleadly — Production Docker Image
# Multi-stage: build deps in stage 1, run slim in stage 2
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/build/deps -r requirements.txt

# ── Runtime stage ──
FROM python:3.11-slim

LABEL org.opencontainers.image.title="Pleadly"
LABEL org.opencontainers.image.description="AI-powered full-cycle career assistant"
LABEL org.opencontainers.image.url="https://github.com/Rsaaaa9/Pleadly"

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built deps
COPY --from=builder /build/deps /usr/local

# Copy app code
COPY app/ ./app/
COPY core/ ./core/
COPY rag/  ./rag/
COPY prompts/ ./prompts/
COPY templates/ ./templates/
COPY CLAUDE.md ./

# Create non-root user
RUN useradd -m -u 1000 pleadly && chown -R pleadly:pleadly /app
USER pleadly

# ChromaDB persist path (writable even in read-only containers)
ENV CHROMA_PERSIST_PATH=/tmp/chroma_data

EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -sf http://localhost:7860/ || exit 1

CMD ["python", "app/main.py"]
