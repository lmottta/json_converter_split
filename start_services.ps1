# Script para iniciar os serviços da aplicação JSON Converter

# IMPORTANTE: Certifique-se de que o servidor Redis esteja em execução antes de rodar este script.
# Você pode baixá-lo e iniciá-lo a partir de: https://redis.io/docs/getting-started/installation/

Write-Host "Iniciando o Worker Celery..."
# Inicia o Celery worker em uma nova janela do PowerShell para que não bloqueie este script
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Iniciando Celery Worker...'; cd c:\Users\Mota\json_converter; celery -A celery_worker.celery_app worker -l info"

Write-Host "Aguardando alguns segundos para o Celery Worker iniciar..."
Start-Sleep -Seconds 10

Write-Host "Iniciando o Servidor Flask..."
# Inicia o Flask em uma nova janela do PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Iniciando Flask App...'; cd c:\Users\Mota\json_converter; flask run"

Write-Host "Serviços iniciados!"
Write-Host "- O Worker Celery está rodando em uma janela separada."
Write-Host "- O Servidor Flask está rodando em outra janela separada (geralmente em http://127.0.0.1:5000)."
Write-Host "Lembre-se de que o Redis DEVE estar em execução para que o Celery funcione corretamente."