# Inference Optimization: llama.cpp on Snapdragon 8 Elite

## Build Flags

```bash
cmake -B build \
  -DGGML_VULKON=1 \
  -DGGML_NATIVE=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DBUILD_SHARED_LIBS=OFF
cmake --build build -j6
```

Note: `-DGGML_NATIVE=OFF` prevents x86-specific optimizations from being silently used for ARM.

## Runtime Tuning

| Flag | Value | Rationale |
|------|-------|-----------|
| `--threads` | 6 | 8 cores total, leave 2 for OS |
| `--ctx` | 2048-4096 | 2048 for cron, 4096 for conversation |
| `--n-gpu-layers` | Max that fits in 2GB VRAM budget | Offload to Adreno 830 GPU |
| `--cache-type` | q8_0 | halves KV cache memory |
| `--temp` | 0.7 | default, increase for creative tasks |
| `--top-p` | 0.9 | standard sampling |

## RAM Budget (24GB shared)

- OS + Android: ~6-8GB
- Termux + llama.cpp: ~2GB
- Nemotron 4B Q4: ~2.5GB
- Qwen 9B Q5: ~5.5GB
- Headroom: ~4-6GB

Both models CAN fit simultaneously but we load/unload on demand to preserve headroom.

## Quantization Trade-offs

| Model | Precision | Size | Speed | Quality |
|-------|-----------|------|-------|---------|
| Nemotron 4B | Full | ~8GB | Slowest | Highest |
| Nemotron 4B | Q4 | ~2.5GB | Fast | 95%+ |
| Nemotron 4B | Q5 | ~3GB | Fast | 98%+ |
| Qwen 9B | Q5 | ~5.5GB | Medium | 95%+ |
| Qwen 9B | Q8 | ~8GB | Slower | 99%+ |

Recommendation: Use Q4 for Nemotron (speed-critical), Q5 for Qwen (quality balance).

## GPU Offloading

Test with increasing `--n-gpu-layers` until OOM or quality degrades:

```bash
# Layer-by-layer test
for layers in 10 20 30 40 50; do
  echo "Testing $layers layers..."
  ~/llama.cpp/build/bin/llama-cli \
    -m /sdcard/models/qwen-9b-q5.gguf \
    -p "Count to 5." \
    --n-gpu-layers $layers \
    --threads 6 \
    2>&1 | tail -3
done
```

Stop when:
- First layer fails to offload (VRAM full)
- Quality drops noticeably
- Speed plateaus or regresses

## Expected Performance

Based on Snapdragon 8 Elite specs and community benchmarks:

| Model | Quantization | CPU-only | Vulkan GPU | Context |
|-------|-------------|----------|------------|---------|
| Nemotron 4B | Q4 | 15-25 tok/s | 30-50 tok/s | 4096 |
| Qwen 9B | Q5 | 8-15 tok/s | 15-30 tok/s | 4096 |
| Nemotron 4B | Full | 10-18 tok/s | 20-35 tok/s | 2048 |

Test with your actual models — results vary by context length and prompt complexity.
