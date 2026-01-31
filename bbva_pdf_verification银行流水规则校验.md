## ===================================bbva-pdf-verification===================================
D: 
cd D:\Mstar\bbva-pdf-verification_部署版本

python main.py "D:\Mstar\银行审核要点\BBVA流水测试-真实样例1022\BBVA JUN-JUL真实1-MSN20251016154.pdf" -o json excel csv
python main.py "D:\Mstar\银行审核要点\BBVA流水测试-真实样例1022\BBVA JUL-AGO真实2-MSN20251016154.pdf" -o json excel csv
python main.py "D:\Mstar\银行审核要点\BBVA流水测试-真实样例1022\BBVA AGO-SEP真实3-MSN20251016154.pdf" -o json excel csv



D:\App\Anaconda3\python.exe -m src.validator --input MSN20250630061.pdf --output-md reports\MSN20250630061.md

D:\App\Anaconda3\python.exe -m src.validator --input 真实1_MSN20251016154.pdf --output-md-es reports\真实1_MSN20251016154_es.md --output-md-zh reports\真实1_MSN20251016154_zh.md

D:\App\Anaconda3\python.exe -m src.validator --input 真实2-MSN20251016154.pdf --output-md-es reports\真实2-MSN20251016154_es.md --output-md-zh reports\真实2-MSN20251016154_zh.md

D:\App\Anaconda3\python.exe -m src.validator --input 真实3-MSN20251016154.pdf --output-md-es reports\真实3-MSN20251016154_es.md --output-md-zh reports\真实3-MSN20251016154_zh.md

## ===================================bbva-pdf-verification===================================