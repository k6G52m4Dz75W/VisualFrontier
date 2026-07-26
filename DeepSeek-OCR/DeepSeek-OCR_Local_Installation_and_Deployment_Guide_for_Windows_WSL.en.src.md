---
title: DeepSeek-OCR Local Installation and Deployment Guide for Windows WSL
source: "https://github.com/k6G52m4Dz75W/VisualFrontier/blob/main/DeepSeek-OCR/DeepSeek-OCR_Local_Installation_and_Deployment_Guide_for_Windows_WSL.en.md"
author: Visual Frontier (https://github.com/k6G52m4Dz75W/VisualFrontier), DeepSeek, Hy3@WorkBuddy
created: 2026-07-24
description: This article provides a practical guide for fully installing and deploying the DeepSeek-OCR model on Windows WSL using Miniconda, vLLM, and domestic mirror acceleration, and starting the OpenAI-compatible service.
tags:
  - DeepSeek-OCR
  - WSL
  - Windows Subsystem for Linux
  - vLLM
---

# 🛠️ DeepSeek-OCR Local Installation and Deployment Guide for Windows WSL

🕒 Last updated: `2026-07-25`

<!-- include: _partials/en/common/nvidia-driver.md -->
<!-- include: _partials/en/common/install-wsl.md -->
<!-- include: _partials/en/common/start-ubuntu.md -->
<!-- include: _partials/en/common/install-miniconda.md -->
<!-- include: _partials/en/common/install-uv.md -->
<!-- include: _partials/en/common/install-modelscope.md -->
<!-- include: _partials/en/deepseek-ocr/weights.md -->
<!-- include: _partials/en/deepseek-ocr/env.md -->
<!-- include: _partials/en/deepseek-ocr/install-cuda.md -->
<!-- include: _partials/en/deepseek-ocr/vllm.md -->
<!-- include: _partials/en/deepseek-ocr/start-vllm.md -->
<!-- include: _partials/en/common/vibeocr.md -->
<!-- include: _partials/en/deepseek-ocr/clone.md -->
# ⚠️ Notes

Whether you follow the official installation guide, use the intelligent vLLM installation described above, or use the model deployed via the SiliconFlow platform service, this model is highly likely to randomly produce garbled text, omit content, or repeat large passages. It is strongly recommended to use the upgraded [DeepSeek-OCR-2](https://github.com/deepseek-ai/DeepSeek-OCR-2) model as a replacement.
