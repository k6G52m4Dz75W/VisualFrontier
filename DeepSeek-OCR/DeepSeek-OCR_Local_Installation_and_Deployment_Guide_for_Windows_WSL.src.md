---
title: DeepSeek-OCR Windows WSL本地安装部署指南
source: "https://github.com/k6G52m4Dz75W/VisualFrontier/blob/main/DeepSeek-OCR/DeepSeek-OCR_Local_Installation_and_Deployment_Guide_for_Windows_WSL.md"
author: Visual Frontier (https://github.com/k6G52m4Dz75W/VisualFrontier), DeepSeek, Hy3@WorkBuddy
created: 2026-07-24
description: 本文提供了在Windows WSL中通过Miniconda、vLLM和国内镜像加速，完整安装部署DeepSeek-OCR模型并启动OpenAI兼容服务的实操指南。
tags:
  - DeepSeek-OCR
  - WSL
  - Windows Subsystem for Linux
  - vLLM
vars: _partials/vars/deepseek-ocr.yml
---

# 🛠️ DeepSeek-OCR Windows WSL本地安装部署指南

🕒 最后更新：`2026.7.25`

<!-- include: _partials/zh/nvidia-driver.md -->
<!-- include: _partials/zh/install-wsl.md -->
<!-- include: _partials/zh/start-ubuntu.md -->
<!-- include: _partials/zh/install-miniconda.md -->
<!-- include: _partials/zh/install-uv.md -->
<!-- include: _partials/zh/install-modelscope.md -->
<!-- include: _partials/zh/weights.md -->
<!-- include: _partials/zh/env.md -->
<!-- include: _partials/zh/install-cuda.md -->
<!-- include: _partials/zh/vllm.md -->
<!-- include: _partials/zh/start-vllm.md -->
<!-- include: _partials/zh/vibeocr.md -->
<!-- include: _partials/zh/clone.md -->
# ⚠️ 注意事项

本模型无论是按照官方安装指引还是按照以上vLLM智能安装得到的结果，抑或是硅基流动平台服务部署的结果都极大概率会随机性出现文本乱码或缺失、重复大段文本的问题，强烈建议使用升级后的[DeepSeek-OCR-2](https://github.com/deepseek-ai/DeepSeek-OCR-2)模型替代。
