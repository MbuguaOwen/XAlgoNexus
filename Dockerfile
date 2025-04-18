# syntax=docker/dockerfile:1

# =============== Stage 1: Builder ===============
FROM ubuntu:22.04 AS builder

ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies & caching tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    pkg-config \
    libzmq3-dev \
    libssl-dev \
    libcpprest-dev \
    libwebsocketpp-dev \
    libquickfix-dev \
    python3-dev \
    python3-pip \
    ccache \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy entire project
COPY . .

# Configure ccache
RUN ccache --max-size=5G

# Configure, build & install
RUN mkdir build \
 && cd build \
 && cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/app/install \
 && cmake --build . --target install -j$(nproc)


# ============== Stage 2: Runtime ===============
FROM ubuntu:22.04 AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzmq3-4 \
    libssl3 \
    python3-minimal \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed artifacts
COPY --from=builder /app/install /app/install

# Ensure binaries are on PATH
ENV PATH="/app/install/bin:${PATH}"

# Default entrypoint
ENTRYPOINT ["tri_arbitrage_app"]
CMD ["--help"]
