# Phase 1: Termux Setup (Nubia Z70 Ultra)

Phone-side setup steps. Run in order.

## Prerequisites

- Nubia Z70 Ultra (Snapdragon 8 Elite, 24GB RAM, 1TB)
- AIOS (Android 15) stock ROM
- Stable WiFi connection

## Step-by-Step

### 1. Install Termux

Download from **F-Droid** (https://f-droid.org/en/packages/com.termux/), NOT the Play Store version (outdated, no longer maintained).

```bash
pkg update && pkg upgrade -y
```

### 2. Storage Access

```bash
termux-setup-storage
```

This grants access to `/sdcard/`. Confirm the permission dialog.

### 3. Install Build Tools

```bash
pkg install -y git cmake build-essential python openssh
```

### 4. Build llama.cpp (Vulkan)

```bash
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_VULKAN=1 -DCMAKE_BUILD_TYPE=Release
cmake --build build -j6 --config Release
```

Vulkan support requires the Vulkan SDK. On Android, the GPU drivers should expose Vulkan natively.

### 5. Set Up SSH Key for VPS

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

Add the public key to VPS `~/.ssh/authorized_keys` for secure model file transfer.

### 6. Tailscale

Install the Tailscale Android app from Play Store or F-Droid. Log in to Russell's tailnet.

Verify from VPS: `tailscale status --json` should show the phone by hostname.

### 7. Model Storage

```bash
mkdir -p /sdcard/models
```

Download GGUF models from HuggingFace via WiFi:

```bash
# Nemotron 3 4B Q4
wget -O /sdcard/models/nemotron-3-4b-q4.gguf "<huggingface_url>"

# Qwen 3.5 9B Q5
wget -O /sdcard/models/qwen-9b-q5.gguf "<huggingface_url>"
```

### 8. Verify

```bash
# Test llama.cpp loads a model
~/llama.cpp/build/bin/llama-cli \
  -m /sdcard/models/nemotron-3-4b-q4.gguf \
  -p "Hello, world." \
  -n 20 \
  --threads 6 \
  --ctx 2048
```

Expected: coherent response in 10-30 seconds on first run.

## Post-Setup (After Basic Verification)

1. Battery optimization whitelist for Termux (Settings → Apps → Termux → Battery → Unrestricted)
2. Disable battery saver for AIOS AI features that might conflict
3. Test process persistence: leave Termux running overnight, verify no OOM kills
