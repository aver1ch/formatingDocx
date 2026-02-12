# Рекомендации по использованию и расширению модуля doc_editor

## Содержание

1. [Использование модуля doc_editor](#использование-модуля-doc_editor)
2. [Как расширять функционал](#как-расширять-функционал)
3. [Интеграция с микросервисом](#интеграция-с-микросервисом)
4. [Лучшие практики](#лучшие-практики)
5. [Troubleshooting](#troubleshooting)

---

## Использование модуля doc_editor

### Локальное использование (Python)

```python
from doc_editor.editor import DocumentEditor

# 1. Инициализация
editor = DocumentEditor('input.docx')

# 2. Загрузить конфигурацию
editor.load_config('config.yaml')

# 3. Применить форматирование
editor.apply_config()

# 4. Сохранить результат
editor.save('output.docx')
```

### Использование через REST API

```bash
# Запустить микросервис
python main.py

# Обработать документ
curl -X POST http://localhost:5000/api/process_document \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://example.com/input.docx",
    "config": {
      "document": {
        "general": {
          "margins": {"left": "20mm", "right": "10mm", ...},
          "fonts": {...},
          "spacing": {"line": 1.5}
        },
        "structure": {...}
      }
    }
  }'
```

### Использование через Docker

```bash
# Собрать образ
docker build -t doc-editor .

# Запустить контейнер
docker run -p 5000:5000 doc-editor

# Обработать документ
curl -X POST http://localhost:5000/api/process_document \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Как расширять функционал

### Добавление нового процессора

#### Шаг 1: Создать новый процессор

```python
# doc_editor/processors/custom_processor.py

import logging
from docx import Document
from ..models import DocumentConfig, ProcessorError

logger = logging.getLogger(__name__)

class CustomProcessor:
    """Описание вашего процессора."""
    
    def __init__(self, doc: Document, config: DocumentConfig):
        """
        Инициализация.
        
        Args:
            doc: Документ
            config: Конфигурация
        """
        self.doc = doc
        self.config = config
        self.logger = logger
    
    def apply(self) -> None:
        """Применить обработку."""
        try:
            self.logger.info("Начало обработки")
            # Ваша логика здесь
            self._do_something()
            self.logger.info("Обработка завершена")
        except Exception as e:
            self.logger.error(f"Ошибка: {e}")
            raise ProcessorError(f"Ошибка: {e}")
    
    def _do_something(self) -> None:
        """Вспомогательный метод."""
        # Ваша реализация
        pass
```

#### Шаг 2: Расширить конфигурацию

```python
# doc_editor/models/config.py

from dataclasses import dataclass, field

@dataclass
class CustomConfig:
    """Конфигурация для кастомного процессора."""
    enabled: bool = True
    param1: str = "default"
    param2: int = 0

@dataclass
class StructureConfig:
    # ... существующие поля ...
    custom: CustomConfig = field(default_factory=CustomConfig)
```

#### Шаг 3: Добавить в Pipeline

```python
# doc_editor/pipeline.py

from .processors import (
    # ... существующие ...
    CustomProcessor  # Добавить импорт
)

class DocumentProcessingPipeline:
    def execute(self, add_title_page: bool = True) -> None:
        # ... существующие этапы ...
        
        # Добавить новый этап
        self._apply_custom()
        
        # ... остальные этапы ...
    
    def _apply_custom(self) -> None:
        """Применить кастомную обработку."""
        self.logger.info("Этап X: Кастомная обработка")
        custom_processor = CustomProcessor(self.doc, self.config)
        custom_processor.apply()
```

#### Шаг 4: Добавить в инициализацию конфига YAML

```yaml
document:
  structure:
    custom:
      enabled: true
      param1: "значение"
      param2: 42
```

#### Шаг 5: Написать тесты

```python
# tests/test_processors/test_custom_processor.py

import pytest
from docx import Document
from doc_editor.processors import CustomProcessor
from doc_editor.models import DocumentConfig

def test_custom_processor():
    doc = Document()
    config = DocumentConfig.from_dict({...})
    
    processor = CustomProcessor(doc, config)
    processor.apply()
    
    # Ваши проверки
    assert doc is not None
```

---

## Интеграция с микросервисом

### Нужно ли расширять REST API?

**Короткий ответ:** ❌ **НЕ требуется** для основной функциональности

**Длинный ответ:** Текущий endpoint `/api/process_document` достаточен, но можно добавить:

### Опциональные новые endpoints

#### 1. Валидация конфигурации

```python
# main.py - добавить новый endpoint

@app.route('/api/validate_config', methods=['POST'])
def validate_config():
    """Валидирует конфигурацию без обработки документа."""
    try:
        config_data = request.json.get('config')
        config = ConfigParser.from_dict(config_data)
        return jsonify({'status': 'valid', 'config': config})
    except Exception as e:
        return jsonify({'status': 'invalid', 'error': str(e)}), 400
```

**Использование:**
```bash
curl -X POST http://localhost:5000/api/validate_config \
  -H "Content-Type: application/json" \
  -d '{"config": {...}}'
```

#### 2. Получить список доступных профилей

```python
@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Возвращает список доступных профилей конфигурации."""
    profiles = ['minimal', 'standard', 'full', 'gost', 'sto']
    return jsonify({'profiles': profiles})
```

#### 3. Асинхронная обработка (Celery)

```python
# tasks.py - добавить Celery задачу

from celery import Celery

app = Celery('doc_editor')

@app.task
def process_document_async(document_url, config):
    """Асинхронная обработка документа."""
    editor = DocumentEditor(download_file(document_url))
    editor.load_config_from_dict(config)
    editor.apply_config()
    return save_and_return_url(editor.doc)

# main.py
@app.route('/api/process_document_async', methods=['POST'])
def process_document_async():
    data = request.json
    task = process_document_async.delay(
        data['document_url'],
        data['config']
    )
    return jsonify({'task_id': task.id, 'status_url': f'/api/task/{task.id}'})
```

### Когда расширять микросервис?

✅ **Расширяйте, если:**
- Нужна асинхронная обработка больших документов
- Нужны дополнительные endpoints для валидации
- Нужна кэширование результатов
- Нужна фоновая очередь обработки (Celery)

❌ **НЕ расширяйте, если:**
- Нужно просто развить модуль `doc_editor`
- Все требования решаются изменениями в модуле

---

## Лучшие практики

### 1. Код

#### Типизация
```python
# ✅ Правильно
def apply(self, doc: Document) -> Document:
    """Применить обработку."""
    return doc

# ❌ Неправильно
def apply(self, doc):
    return doc
```

#### Логирование
```python
# ✅ Правильно
self.logger.info("Начало применения стилей")
try:
    self._apply_styles()
    self.logger.info("Стили успешно применены")
except Exception as e:
    self.logger.error(f"Ошибка применения стилей: {e}")
    raise

# ❌ Неправильно
print("Applying styles...")
self._apply_styles()
print("Done")
```

#### Обработка ошибок
```python
# ✅ Правильно
try:
    self.doc = Document(doc_path)
except FileNotFoundError:
    raise DocumentFormattingError(f"Файл не найден: {doc_path}")
except Exception as e:
    raise DocumentFormattingError(f"Ошибка загрузки: {e}")

# ❌ Неправильно
self.doc = Document(doc_path)  # Может упасть без обработки
```

### 2. Конфигурация

#### Структурирование
```yaml
# ✅ Правильно - логичная иерархия
document:
  general:
    margins: {...}
    fonts: {...}
  structure:
    title_page: {...}
    sections: {...}

# ❌ Неправильно - плоская структура
document:
  left_margin: 20mm
  right_margin: 10mm
  title_page_enabled: true
```

#### Значения по умолчанию
```python
# ✅ Правильно
@dataclass
class Config:
    enabled: bool = True
    margin: str = "20mm"
    font_size: str = "12pt"

# ❌ Неправильно - обязательные поля
@dataclass
class Config:
    enabled: bool
    margin: str
    font_size: str
```

### 3. Тестирование

#### Структура тестов
```
tests/
  test_processors/
    test_style_processor.py
    test_margins_processor.py
    test_title_processor.py
  test_integration/
    test_full_document.py
  test_data/
    sample_input.docx
    sample_config.yaml
```

#### Пример теста
```python
import pytest
from docx import Document
from doc_editor.editor import DocumentEditor

@pytest.fixture
def editor():
    return DocumentEditor('tests/test_data/sample_input.docx')

def test_load_config(editor):
    editor.load_config('tests/test_data/sample_config.yaml')
    assert editor.config is not None
    assert editor.config.general.margins.left == '20mm'

def test_apply_config_saves_document(editor, tmp_path):
    editor.load_config('tests/test_data/sample_config.yaml')
    editor.apply_config()
    
    output_path = tmp_path / "output.docx"
    editor.save(str(output_path))
    
    assert output_path.exists()
    result_doc = Document(str(output_path))
    assert len(result_doc.sections) > 0
```

### 4. Документирование

```python
# ✅ Правильно
def apply_styles(self) -> None:
    """
    Применяет стили из конфигурации к документу.
    
    Стили применяются в следующем порядке:
    1. Основные стили (main)
    2. Стили заголовков (header1, header2, ...)
    3. Специальные стили (appendices, notes)
    
    Raises:
        ProcessorError: Если применение стилей не удалось.
    
    Example:
        >>> processor = StyleProcessor(doc, config)
        >>> processor.apply()
    """
    pass

# ❌ Неправильно
def apply_styles(self):
    # Применить стили
    pass
```

---

## Troubleshooting

### Проблема: Конфигурация не загружается

```python
# Отладка
from doc_editor.parsers import ConfigParser

try:
    config = ConfigParser.from_file('config.yaml')
except Exception as e:
    print(f"Ошибка: {e}")
    # Проверьте:
    # 1. Файл существует?
    # 2. YAML синтаксис корректен?
    # 3. Обязательные поля присутствуют?
```

### Проблема: Документ не обрабатывается

```python
# Проверить логи
import logging
logging.basicConfig(level=logging.DEBUG)

editor = DocumentEditor('input.docx')
editor.load_config('config.yaml')
editor.apply_config()  # Теперь виднее логи
```

### Проблема: Форматирование не применяется

```python
# Проверить, что конфиг содержит нужные параметры
from doc_editor.models import DocumentConfig

config = DocumentConfig.from_dict(yaml_data)
print(config.general.margins)
print(config.general.fonts)
print(config.general.spacing)

# Убедиться, что это передается в процессоры
```

### Проблема: Производительность медленная

```python
# Профилирование
import cProfile
import pstats
from io import StringIO

pr = cProfile.Profile()
pr.enable()

editor = DocumentEditor('input.docx')
editor.load_config('config.yaml')
editor.apply_config()

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(10)
print(s.getvalue())
```

---

## Контрольный список для расширения модуля

- [ ] Прочитали документацию текущего кода
- [ ] Создали новый файл процессора
- [ ] Добавили конфигурационные классы
- [ ] Интегрировали в Pipeline
- [ ] Написали unit-тесты (80%+ покрытие)
- [ ] Добавили docstrings
- [ ] Проверили backward compatibility
- [ ] Обновили README.md
- [ ] Создали PR с описанием

---

## Ссылки на документацию

- [python-docx API](https://python-docx.readthedocs.io/)
- [ГОСТ Р 1.5-2004](https://docs.cntd.ru/document/gost-r-1-5-2004)
- [PyYAML документация](https://pyyaml.org/)
- [pytest документация](https://docs.pytest.org/)

---

## Контакты и поддержка

**Вопросы?** Смотрите:
1. [GOST_COMPLIANCE_ANALYSIS.md](GOST_COMPLIANCE_ANALYSIS.md) - Анализ требований
2. [PHASE1_DETAILED_PLAN.md](PHASE1_DETAILED_PLAN.md) - План Фазы 1
3. [ROADMAP.md](ROADMAP.md) - Дорожная карта проекта

---

**Последнее обновление:** 10 февраля 2026 г.
