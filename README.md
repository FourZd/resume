
## Предварительные требования

Прежде чем начать, убедитесь, что на вашем компьютере установлен Docker. Если Docker не установлен, следуйте инструкциям ниже для его установки с помощью скрипта.

### Установка Docker

Для установки Docker на Linux можно использовать специальный скрипт, который автоматизирует процесс установки. Выполните следующие шаги:

  1. Откройте терминал.
  2. Выполните следующую команду для загрузки и запуска скрипта установки Docker:
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  3. После завершения скрипта, проверьте установку, выполнив команду `docker --version`, которая должна показать установленную версию Docker.

Для установки Docker на Windows просто установите Docker Desktop с официального сайта.

## Запуск проекта
Для запуска проекта выполните следующие шаги:

1. Перейдите в директорию `dev_tools` проекта:
cd dev_tools
2. Запустите Docker Compose:
docker-compose up --build

После выполнения данных команд ваш проект будет запущен и доступен для использования через localhost:8000.
Доступен Swagger по эндпоинту localhost:8000/docs/
