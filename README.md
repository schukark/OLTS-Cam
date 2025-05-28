# Object Location Tracking System

## Описание

Данный программный комплекс является self-host решением, позволяющим при установке и подключении камеры следить за мелкими вещами в помещении (например телефон/ноутбук/кошелек и прочее).

## Установка приложения

```bash
    git clone git@github.com:schukark/OLTS-Cam.git
    cd OLTS-Cam
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

Далее пути установки разнятся:

1. Если Вы обладатель видеокарты NVidia или AMD с поддержкой от PyTorch, то выполните `pip install -r requirements_torch.txt`
2. Если такой видеокарты у вас нет или Вы не знаете, то выполните `pip install -r requirements_torch_cpu.txt`

## Установка бота

1. Исполняемый файл бота поставляется в корне репозитория (файлы `bot` или `bot.exe` в зависимости от ОС)
2. Иначе, убедитесь, что на вашей системе установлен `rustup` и выбран `Rust 1.89.0-nightly`. Далее, находясь в корне проекта запустите `cargo build --release`. После выполнения команды, исполняемый файл бота будет лежать по пути `target/release/bot`.

Для проверки md5 получившегося исполняемого файла, прилагаются md5 под некоторые архитектуры:

|                   -march |                              md5 |
| ------------------------ | -------------------------------- |
| x86_64-unknown-linux-gnu | 45d5e9b4977174c19a39e4e431ef1d60 |
|    x86_64-pc-windows-gnu | e7185d58f7323d231b86b4439d448325 |

## Запуск

Приложение запускается с помощью файла `launch.sh` (*nix системы) /`launch.bat` (Windows)

Также, части проекта можно запустить отдельно, если такая потребность есть:

1. `python src/main.py` для десктопной части
2. `./bot`/`bot.exe` для бота (или `cargo run --release`, если установлен `rustup`)

## Использованные технологии

- Python
- OpenCV
- PyTorch
- FastAPI
- Rust
- Teloxide
- Telegram API

## Инструкция к репозиторию

Проект разделен на независимые и модульные части:

1. Python Desktop Application - приложение на ПК (написано на Python), содержащее все настройки и связь с камерой
2. Telegram Bot - код для телеграм-бота (написан на Rust)
3. Python API endpoint Server - сервер-приемник запросов от телеграм-бота (написан на Python)

Каждый модуль имеет очень ограчниенный набор публичных методов, чтобы жестко следовать API - это позволяет менять реализацию модулей.
Соответственно, чтобы не смешивать эти независимые модули между собой, код для каждой из них содержится в отдельной ветке репозитория:

1. telegram-bot - ветка телеграм-бота
2. desktop-application - ветка приложения на ПК
3. python-server - API server как часть десктоп приложения

## Значки (интерактивные)

[![Rust](https://github.com/schukark/OLTS-Cam/actions/workflows/rust.yml/badge.svg)](https://github.com/schukark/OLTS-Cam/actions/workflows/rust.yml)
[![doc coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fschukark%2F1b10014d0019c22cc1984bc8a7be7152%2Fraw%2F3de291300f3d36ee7956596666a10d667ab31971%2Fdoc-coverage.json)](https://github.com/schukark/OLTS-Cam/)
[![test coverage](https://coveralls.io/repos/github/schukark/OLTS-Cam/badge.svg?branch=telegram-bot)](https://coveralls.io/github/schukark/OLTS-Cam?branch=telegram-bot)
