# Архитектура системы редактирования документов формата DOCX

## Обзор проекта

Проект представляет собой микросервис на базе Flask для автоматизированной обработки и форматирования документов в формате DOCX (Microsoft Word). Система применяет конфигурируемые стили, добавляет титульные листы, управляет колонтитулами, устанавливает поля и межстрочные интервалы на основе описания в YAML-файле конфигурации.

**Основной стек технологий:**
- Python 3.11+
- Flask (REST API)
- python-docx (манипуляция DOCX)
- docxtpl (шаблонизация документов)
- docxcompose (объединение документов)
- PyYAML (парсинг конфигурации)

---

## Архитектурная иерархия

```
app.py (REST endpoint)
  └─> DocumentEditor (главный интерфейс)
       └─> ConfigParser (парсинг YAML)
       │    └─> models/config.py (типизированные dataclasses)
       │
       └─> DocumentProcessingPipeline (оркестратор)
            ├─> StyleProcessor (применение стилей и шрифтов)
            ├─> HeaderFooterProcessor (добавление колонтитулов)
            ├─> TitleProcessor (добавление титульного листа)
            └─> MarginsProcessor (установка полей страницы)
```

---

## Компоненты системы

### 1. **Уровень REST API (`main.py`)**

**Отвественность:**
- Прием HTTP-запросов с документом и конфигурацией
- Загрузка документа по URL или из локального хранилища
- Обработка ошибок и возврат результата

**Основной endpoint:**
- `POST /api/process_document`
  - Input: JSON с `document_url` и `config` (YAML конфигурация)
  - Output: обработанный DOCX файл

**Особенности:**
- Валидация URL документов
- Загрузка файлов через HTTP
- Обработка временных файлов
- Логирование всех операций

---

### 2. **Главный интерфейс (`doc_editor/editor.py`)**

**Класс: `DocumentEditor`**

**Отвественность:**
- Координация загрузки документа и конфигурации
- Управление жизненным циклом обработки
- Сохранение результата

**Основные методы:**
- `__init__(doc_path: str)` — загрузка DOCX файла
- `load_config(config_path: str)` — загрузка конфигурации из YAML
- `apply_config()` — применение конфигурации (запуск pipeline)
- `save(output_path: str)` — сохранение обработанного документа

**Пример использования:**
```python
editor = DocumentEditor('input.docx')
editor.load_config('config.yaml')
editor.apply_config()
editor.save('output.docx')
```

---

### 3. **Парсинг конфигурации**

#### 3.1 **`ConfigParser` (`doc_editor/parsers/config_parser.py`)**

**Отвественность:**
- Загрузка YAML файла
- Преобразование словаря в типизированный объект `DocumentConfig`
- Валидация конфигурации

**Основные методы:**
- `from_file(config_path: str) -> DocumentConfig` — загрузка и парсинг YAML
- `from_dict(data: Dict[str, Any]) -> DocumentConfig` — преобразование словаря

**Особенности:**
- Обработка ошибок YAML
- Логирование процесса парсинга
- Автоматическая валидация на уровне dataclass

#### 3.2 **Модели конфигурации (`doc_editor/models/config.py`)**

**Dataclasses для типизации конфигурации:**

```
DocumentConfig (корневая)
├── GeneralConfig (общие настройки)
│   ├── margins: MarginsConfig
│   ├── fonts: Dict[str, FontConfig]
│   └── spacing: SpacingConfig
│
└── StructureConfig (структура документа)
    ├── title_page: TitlePageConfig
    ├── sections: Optional[Dict]
    └── numbering: NumberingConfig
        └── headers: HeadersConfig
```

**Назначение каждого:**

| Класс | Назначение |
|-------|-----------|
| `FontConfig` | Параметры шрифта (семейство, размер, жирность, курсив) |
| `MarginsConfig` | Поля страницы (левое, правое, верхнее, нижнее) |
| `SpacingConfig` | Межстрочные интервалы и исключения |
| `TitlePageConfig` | Параметры титульного листа (шаблон, логотип, элементы) |
| `HeadersConfig` | Параметры колонтитулов (левый, правый, номера страниц) |
| `NumberingConfig` | Конфигурация нумерации и заголовков |
| `DocumentConfig` | Полная конфигурация документа |

**Пример YAML конфигурации:**
```yaml
document:
  general:
    margins:
      left: "20mm"
      right: "10mm"
      top: "20mm"
      bottom: "20mm"
    fonts:
      main:
        family: Arial
        size: 12pt
      header1:
        family: Arial
        size: 14pt
        bold: true
    spacing:
      line: 1.5
  
  structure:
    title_page:
      enabled: true
      template_path: "doc_editor/templates/title_page_template.docx"
      image_path: "doc_editor/templates/logo.png"
      elements:
        - agency_name: "Государственная организация"
        - title: "Название стандарта"
  
  numbering:
    headers:
      enabled: true
      left: "Обозначение стандарта"
      right: "ГОСТ Р"
      page_numbers: true
```

---

### 4. **Pipeline обработки (`doc_editor/pipeline.py`)**

**Класс: `DocumentProcessingPipeline`**

**Отвественность:**
- Оркестрация последовательности процессоров
- Управление жизненным циклом обработки
- Координация фаз обработки

**Основные методы:**
- `execute(add_title_page: bool = True)` — запуск полного pipeline
- `get_document() -> Document` — получение обработанного документа

**Фазы выполнения:**

```
Фаза 1: Применение стилей и полей
  └─> StyleProcessor.apply() — установка шрифтов, размеров, стилей
  └─> MarginsProcessor.apply() — установка полей страницы

Фаза 2: Добавление титульного листа
  └─> TitleProcessor.apply() — если enabled в конфигурации

Фаза 3: Переприменение настроек и колонтитулы
  └─> StyleProcessor._apply_to_existing_document() — повторное применение к body
  └─> HeaderFooterProcessor.apply() — добавление колонтитулов
```

**Особенности:**
- Обработка ошибок на каждом этапе
- Логирование начала и завершения каждой фазы
- Откат на ошибку

---

### 5. **Процессоры документа**

#### 5.1 **`StyleProcessor` (`doc_editor/processors/style_processor.py`)**

**Отвественность:**
- Применение шрифтов к документу (семейство, размер, жирность, курсив)
- Настройка стилей заголовков
- Установка межстрочных интервалов

**Основные методы:**
- `apply()` — главный метод, запускает все стадии применения стилей
- `_setup_base_styles()` — настройка основных стилей (Normal, Custom_Main, etc.)
- `_setup_heading_styles()` — настройка стилей заголовков (Heading 1-3)
- `_setup_special_styles()` — настройка специальных стилей (титул, колонтитулы)
- `_apply_line_spacing()` — установка межстрочных интервалов
- `_apply_to_existing_document()` — принудительное применение шрифта ко всем существующим параграфам
- `_apply_font_settings(style, font_cfg)` — применение настроек шрифта к стилю
- `_set_font_family(style, family)` — установка семейства шрифта на уровне XML (w:rFonts)

**Ключевые особенности:**
- Использование XML-манипуляций для установки `w:rFonts` (перебивает тему документа)
- Установка шрифтов как на уровне стилей, так и на уровне отдельных run'ов (runs)
- Поддержка сложных скриптов (szCs, bCs, iCs)

**Пример:**
```python
processor = StyleProcessor(doc, config)
processor.apply()  # применяет все стили из конфигурации
```

#### 5.2 **`HeaderFooterProcessor` (`doc_editor/processors/header_footer_processor.py`)**

**Отвественность:**
- Добавление колонтитулов (заголовки и подвалы) на все страницы
- Установка номеров страниц
- Применение конфигурируемого шрифта к содержимому колонтитулов

**Основные методы:**
- `apply()` — главный метод, применяет конфигурацию колонтитулов
- `_apply_headers_footers()` — добавление текста в колонтитулы
- `_add_text_to_element(element, text, align)` — добавление текста с шрифтом
- `_add_page_number(footer, align)` — добавление поля PAGE в подвал
- `_clear_element(element)` — очистка элемента

**Ключевые особенности:**
- Установка разных колонтитулов для нечетных и четных страниц
- Очистка титульной страницы от колонтитулов
- Run-level шрифты (w:rFonts) для перебивания темы
- Поддержка выравнивания (left, center, right)

**Пример:**
```python
config.structure.numbering.headers = HeadersConfig(
    enabled=True,
    left="Левый колонтитул",
    right="Правый колонтитул",
    page_numbers=True
)
processor = HeaderFooterProcessor(doc, config)
processor.apply()
```

#### 5.3 **`TitleProcessor` (`doc_editor/processors/title_processor.py`)**

**Отвественность:**
- Загрузка шаблона титульного листа (DOCX файл)
- Подстановка данных через шаблонизатор (docxtpl)
- Объединение титульного листа с основным документом
- Применение конфигурируемого шрифта к шаблонизированному содержимому

**Основные методы:**
- `apply(source_doc_path, output_path)` — добавление титульного листа
- `_add_title_page(source_doc_path, output_path, title_config)` — логика добавления
- `_parse_elements(elements_list)` — преобразование элементов конфигурации в словарь
- `_apply_font_to_doc(doc, family)` — установка шрифта ко всем параграфам и таблицам

**Ключевые особенности:**
- Использование `DocxTemplate` для подстановки данных
- Поддержка вставки изображений (логотипы)
- Применение конфигурируемого шрифта ко всему шаблонизированному контенту (параграфы, таблицы, runs)
- Run-level w:rFonts для перебивания темы шаблона
- Использование `Composer` для объединения документов
- Очистка временных файлов

**Пример:**
```python
config.structure.title_page = TitlePageConfig(
    enabled=True,
    template_path="template.docx",
    image_path="logo.png",
    elements=[
        {"agency_name": "МОО"},
        {"title": "ГОСТ Р 1.5—2004"}
    ]
)
processor = TitleProcessor(config)
processor.apply("main.docx", "output.docx")
```

#### 5.4 **`MarginsProcessor` (`doc_editor/processors/margins_processor.py`)**

**Отвественность:**
- Установка полей страницы (левое, правое, верхнее, нижнее)
- Применение параметров из конфигурации к документу

**Основные методы:**
- `apply()` — применение полей ко всем секциям

**Ключевые особенности:**
- Парсинг размеров из различных форматов (mm, pt, in, cm)
- Применение к каждой секции документа

---

### 6. **Утилиты (`doc_editor/utils.py`)**

**Функции для парсинга и преобразования:**
- `parse_measurement(value: str) -> float` — преобразование строк типа "20mm", "1in" в пункты
- `parse_size(size_str: str) -> float` — преобразование размеров шрифта

**Пример:**
```python
parse_measurement("20mm")  # => 566.92
parse_size("12pt")  # => 12.0
```

---

### 7. **Исключения (`doc_editor/models/exceptions.py`)**

**Иерархия исключений:**
```
ProcessorError (базовое)
├── ConfigValidationError (ошибка валидации конфигурации)
├── ConfigParsingError (ошибка парсинга конфигурации)
└── DocumentFormattingError (ошибка форматирования документа)
```

---

## Поток данных

### Сценарий: Обработка документа через API

```
1. HTTP POST /api/process_document
   ├─> Получить document_url и config (YAML)
   ├─> Скачать документ
   │
   2─> DocumentEditor.load_config()
   ├─> ConfigParser.from_file() / from_dict()
   ├─> Создать DocumentConfig (типизированные dataclasses)
   │
   3─> DocumentEditor.apply_config()
   ├─> DocumentProcessingPipeline.execute()
   │
   ├─── ФАЗА 1: Стили и поля
   │   ├─> StyleProcessor.apply()
   │   │   ├─> _setup_base_styles() — основные стили
   │   │   ├─> _setup_heading_styles() — стили заголовков
   │   │   ├─> _setup_special_styles() — специальные стили
   │   │   ├─> _apply_line_spacing() — интервалы
   │   │   └─> _apply_to_existing_document() — к body
   │   │
   │   └─> MarginsProcessor.apply()
   │       └─> Установить поля для всех секций
   │
   ├─── ФАЗА 2: Титульный лист (если enabled)
   │   └─> TitleProcessor.apply()
   │       ├─> Загрузить шаблон
   │       ├─> Подставить данные (docxtpl)
   │       ├─> Применить шрифты ко всему контенту
   │       └─> Объединить с основным документом
   │
   └─── ФАЗА 3: Колонтитулы и повторное применение
       ├─> StyleProcessor._apply_to_existing_document()
       └─> HeaderFooterProcessor.apply()
           ├─> Установить разные колонтитулы для четных/нечетных
           └─> Добавить номера страниц
│
4─> DocumentEditor.save(output_path)
│
5─> HTTP 200 + файл

Обработка ошибок на каждом этапе:
- Логирование в stderr/stdout
- Исключение с понятным сообщением
- HTTP 400/500 ответ
```

---

## Ключевые механизмы

### 1. **Применение шрифтов**

**Проблема:** Theme в DOCX шаблонах может переопределять явно установленные шрифты.

**Решение:** Установка шрифтов на трех уровнях:
1. На уровне **style** (стиль абзаца)
2. На уровне **run** (`run.font.name`)
3. На уровне **XML** (`w:rFonts` с атрибутами ascii, hAnsi, cs)

```python
# Уровень 3: XML (перебивает тему)
rFonts = rPr.find(qn('w:rFonts'))
rFonts.set(qn('w:ascii'), 'Arial')
rFonts.set(qn('w:hAnsi'), 'Arial')
rFonts.set(qn('w:cs'), 'Arial')  # Complex script
```

### 2. **Управление секциями**

**Задача:** Разные колонтитулы для первой страницы (титул) и остальных.

**Решение:**
```python
section.different_first_page_header_footer = True
# => first_page_header, header (для нечетных), even_page_header (для четных)
```

### 3. **Объединение документов**

**Задача:** Добавить титульный лист к основному документу.

**Решение:**
```python
title_doc = DocxTemplate(template_path)
title_doc.render(context)  # подставка данных
composer = Composer(Document())
composer.append(Document("title.docx"))
composer.append(Document("main.docx"))
composer.save("output.docx")
```

---

## Расширяемость

### Добавление нового процессора

1. Создать класс наследующий интерфейс:
```python
class NewProcessor:
    def __init__(self, doc: Document, config: DocumentConfig):
        self.doc = doc
        self.config = config
    
    def apply(self) -> None:
        """Основной метод обработки."""
        pass
```

2. Добавить в `pipeline.py`:
```python
from .processors import NewProcessor

def execute(self):
    new_proc = NewProcessor(self.doc, self.config)
    new_proc.apply()
```

3. Добавить конфигурационный класс в `models/config.py`:
```python
@dataclass
class NewProcConfig:
    enabled: bool = True
    # ... другие параметры
```

---

## Тестирование

**Локальный тест:** `local.py`
```python
editor = DocumentEditor('doc_editor/tests/test_data/test.docx')
editor.load_config('doc_editor/tests/test_data/formatConfig.yaml')
editor.apply_config()
editor.save('output.docx')
```

**Проверка результата:**
```python
from docx import Document
doc = Document('output.docx')
# Инспектировать font.name, margins, headers, etc.
```

---

## Рекомендации по развитию

1. **Unit тесты** для каждого процессора
2. **Интеграционные тесты** для полного pipeline
3. **Validation schema** для YAML конфигурации (JSONSchema)
4. **Асинхронная обработка** для больших документов (Celery)
5. **Кэширование** типизированных конфигов
6. **Метрики и мониторинг** обработки документов

---

## Заключение

Архитектура базируется на **separation of concerns**:
- **ConfigParser** отвечает только за парсинг
- Каждый **Processor** отвечает за одну операцию
- **Pipeline** координирует последовательность
- **DocumentEditor** предоставляет простой API

Это позволяет легко тестировать, расширять и поддерживать код.
