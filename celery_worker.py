from celery import Celery

# Configuração do Celery
# Substitua 'redis://localhost:6379/0' pelo URL do seu broker Redis, se diferente.
import os

celery_app = Celery(__name__,
                 broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
                 backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

# Configurações adicionais (opcional)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Permitir apenas conteúdo JSON
    result_serializer='json',
    timezone='America/Sao_Paulo', # Ajuste para o seu fuso horário
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()