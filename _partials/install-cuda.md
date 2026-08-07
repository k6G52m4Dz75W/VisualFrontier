<!-- zh --> ## {{STEP}}. ⚙️ 安装cuda-toolkit并设置环境变量
<!-- en --> ## {{STEP}}. ⚙️ Install CUDA Toolkit and Set Environment Variables

```bash
<!-- zh --> # 安装最新版本的cuda-toolkit
<!-- en --> # Install the latest CUDA toolkit
conda install nvidia::cuda-toolkit -y
<!-- zh --> # 创建环境变量配置文件
<!-- en --> # Create environment variable config directory
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
<!-- zh --> # 写入设置命令（每次激活环境时自动执行）
<!-- en --> # Write setting commands (automatically executed when environment is activated)
echo 'export LIBRARY_PATH=/usr/lib/wsl/lib:$LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
<!-- zh --> #（可选）添加对应的卸载命令（退出环境时恢复）
<!-- en --> # (Optional) Add corresponding unset commands when deactivating
echo 'unset LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
<!-- zh --> # 设置完成后，重新激活环境即可生效
<!-- en --> # After setting, reactivate the environment for changes to take effect
conda deactivate
conda activate {{ENV_NAME}}
```
