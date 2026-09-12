@echo off
chcp 65001 >nul
echo 测试网络连接...
python -c "import requests; r=requests.get('https://api.siliconflow.cn/v1/models', headers={'Authorization':'Bearer sk-gzyeogocatitgfyocczpevbzkecktirtesatpsbzhwhbrobc'}, timeout=10); print('连接成功:', r.status_code); print(r.text[:200])"
if %ERRORLEVEL% NEQ 0 (
    echo 网络连接失败，请检查网络或代理设置
)
pause