## 8. ⚙️ 安装cuda-toolkit并设置环境变量

```bash
# 安装最新版本的cuda-toolkit
conda install nvidia::cuda-toolkit -y
# 创建环境变量配置文件
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
# 写入设置命令（每次激活环境时自动执行）
echo 'export LIBRARY_PATH=/usr/lib/wsl/lib:$LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
#（可选）添加对应的卸载命令（退出环境时恢复）
echo 'unset LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
# 设置完成后，重新激活环境即可生效
conda deactivate
conda activate {{ENV_NAME}}
```
