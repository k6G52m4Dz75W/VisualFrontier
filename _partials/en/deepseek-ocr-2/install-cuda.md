## 8. ⚙️ Install CUDA Toolkit and Set Environment Variables

```bash
# Install the latest CUDA toolkit
conda install nvidia::cuda-toolkit -y
# Create environment variable config directory
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
# Write setting commands (automatically executed when environment is activated)
echo 'export LIBRARY_PATH=/usr/lib/wsl/lib:$LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
# (Optional) Add corresponding unset commands when deactivating
echo 'unset LD_LIBRARY_PATH' > $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
# After setting, reactivate the environment for changes to take effect
conda deactivate
conda activate deepseek-ocr
```
