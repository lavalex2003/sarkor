# sarkor.uz (Home Assistant Custom Integration)

English | Русский

## English

### Overview
`sarkor.uz` is a Home Assistant custom integration that connects to the Sarkor personal cabinet (JSON-RPC API) and exposes account data as sensors.

### Features
- UI configuration (Config Flow): login + password
- Polling via `DataUpdateCoordinator`
- Configurable update interval (hours), default: **12**
- Uses Home Assistant UI language automatically (e.g. `ru`, `uz`, `en`)
- Balance sensor includes extended attributes from the API (`accountBaseInfo`, `limits`, `speeds`)

### Installation

#### HACS (Custom repository)
1. HACS → Integrations → overflow menu → Custom repositories
2. Add repository `lavalex2003/sarkor` (category: Integration)
3. Install and restart Home Assistant

#### Manual
1. Copy `custom_components/sarkor` into your Home Assistant `config/custom_components/`
2. Restart Home Assistant

### Configuration
1. Settings → Devices & services → Add integration
2. Search for **sarkor.uz**
3. Enter your Sarkor cabinet login/password
4. (Optional) Set **Update interval (hours)** (default: 12)

### Options
After setup, you can change the update interval:
Settings → Devices & services → `sarkor.uz` → Configure.

### Entities
The integration creates sensors similar to your existing `BaseData` payload:

- **ASKUI Размер тарифа** (`tariff`) in `UZS`
- **Предоплата** (`saldo_out`) in `UZS`
  - Extra attributes:
    - `accountBaseInfo` fields flattened into attributes (e.g. `tariffTitle`, `contractID`, `ip`, `onlineStatus`, `startTime`, `lastActivity`, etc.)
    - `limits` (array)
    - `speeds` (array)
- **Следующее списание** (`next_debit_ts`) as timestamp (parsed from `nextAbonTime`)

### Troubleshooting
- If sensors show `unavailable`, check Home Assistant logs:
  Settings → System → Logs
- If credentials are correct but login fails, verify the Sarkor cabinet is reachable from your HA instance.

### Notes
- The integration talks to the Sarkor cabinet API endpoint:
  `https://cabinet.sarkor.uz/api/v1/jrpc/v1`

## Русский

### Описание
`sarkor.uz` это кастомная интеграция Home Assistant, которая подключается к личному кабинету Sarkor (JSON-RPC API) и выводит данные аккаунта в виде сенсоров.

### Возможности
- Настройка через UI (Config Flow): логин + пароль
- Опрос через `DataUpdateCoordinator`
- Настраиваемый интервал обновления (в часах), по умолчанию: **12**
- Язык для запросов берется автоматически из языка Home Assistant (например `ru`, `uz`, `en`)
- Сенсор баланса содержит расширенные атрибуты из API (`accountBaseInfo`, `limits`, `speeds`)

### Установка

#### HACS (Пользовательский репозиторий)
1. HACS → Integrations → меню → Custom repositories
2. Добавьте репозиторий `lavalex2003/sarkor` (категория: Integration)
3. Установите и перезапустите Home Assistant

#### Вручную
1. Скопируйте папку `custom_components/sarkor` в `config/custom_components/`
2. Перезапустите Home Assistant

### Настройка
1. Settings → Devices & services → Add integration
2. Найдите **sarkor.uz**
3. Введите логин/пароль от личного кабинета Sarkor
4. (Опционально) Укажите **Интервал обновления (часы)** (по умолчанию 12)

### Опции
Интервал обновления можно поменять после установки:
Settings → Devices & services → `sarkor.uz` → Configure.

### Сущности (сенсоры)
- **ASKUI Размер тарифа** (`tariff`) в `UZS`
- **Предоплата** (`saldo_out`) в `UZS`
  - Атрибуты:
    - поля из `accountBaseInfo` (например `tariffTitle`, `contractID`, `ip`, `onlineStatus`, `startTime`, `lastActivity` и т.д.)
    - `limits` (массив)
    - `speeds` (массив)
- **Следующее списание** (`next_debit_ts`) как timestamp (из `nextAbonTime`)

### Диагностика
- Если сенсоры `unavailable`, проверьте логи:
  Settings → System → Logs
- Если логин/пароль верные, но вход не проходит, проверьте доступность кабинета Sarkor с хоста Home Assistant.

### Примечание
- API endpoint:
  `https://cabinet.sarkor.uz/api/v1/jrpc/v1`

