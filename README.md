# Гайд к репозиторию

Проект разделен на независимые и модульные части:

1. Python Desktop Application - приложение на ПК (написано на Python), содержащее все настройки и связь с камерой
2. Telegram Bot - код для телеграм-бота (написан на Rust)
3. Machine Learning Model - модель машинного или глубокого обучения для распознавания мелких объектов на изображении

Соответственно, чтобы не смешивать эти независимые модули между собой, код для каждой из них содержится в отдельной ветке репозитория:

1. telegram-bot - ветка телеграм-бота
2. desktop-application - ветка приложения на ПК
3. model - ветка модели распознавания объектов (пока отсутствует, так как находится в разработке)
4. infra - ветка с информацией об архитектуре системы как в целом, так и на отдельных уровнях
5. python-server - API server как часть десктоп приложения


[![Rust](https://github.com/schukark/OLTS-Cam/actions/workflows/rust.yml/badge.svg)](https://github.com/schukark/OLTS-Cam/actions/workflows/rust.yml)
[![doc coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fschukark%2F1b10014d0019c22cc1984bc8a7be7152%2Fraw%2F3de291300f3d36ee7956596666a10d667ab31971%2Fdoc-coverage.json)](https://github.com/schukark/OLTS-Cam/)
[![test coverage](https://coveralls.io/repos/github/schukark/OLTS-Cam/badge.svg?branch=telegram-bot)](https://coveralls.io/github/schukark/OLTS-Cam?branch=telegram-bot)
