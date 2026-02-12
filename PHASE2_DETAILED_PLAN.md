# План реализации Фазы 2: Структура документа

## Общая информация

**Цель:** Реализовать многоуровневую структуру документа согласно ГОСТ Р 1.5-2004  
**Целевое соответствие ГОСТ:** 50% → 77%  
**Дедлайн:** 2-3 недели  
**Приоритет:** ВЫСОКИЙ  
**Статус:** К началу реализации

---

## Обзор Фазы 2

### Что требуется реализовать

| Компонент | Описание | Приоритет | Сложность |
|-----------|---------|-----------|-----------|
| **SectionProcessor** | Многоуровневая нумерация разделов (1, 1.1, 1.1.1...) | 🔴 #1 | Высокая |
| **TOCProcessor** | Автоматическое оглавление (Table of Contents) | 🔴 #2 | Средняя |
| **PrefaceProcessor** | Предисловие/преамбула документа | 🟡 #3 | Низкая |
| **AppendixProcessor** | Приложения с буквенной нумерацией | 🟡 #4 | Средняя |

### Структура документа ГОСТ Р 1.5-2004

```
1. Заголовок раздела (Heading 1)
   1.1 Подзаголовок (Heading 2)
      1.1.1 Подпункт (Heading 3)
```

---

## Задача 1: SectionProcessor (НАЧАТЬ С ЭТОГО)

### Описание

**SectionProcessor** - компонент, отвечающий за многоуровневую нумерацию разделов документа.

**Текущая проблема:** Нумерация разделов ручная, нет поддержки автоматического форматирования иерархии.

**Требуемое решение:** 
- Автоматическая нумерация разделов (1, 1.1, 1.1.1...)
- Корректная иерархия по типам заголовков (Heading 1, Heading 2, Heading 3)
- Соответствие ГОСТ Р 1.5-2004

### Архитектура

#### Шаг 1: Расширить конфигурацию (models/config.py)

Добавить классы для конфигурации нумерации:

```python
@dataclass
class SectionConfig:
    """Конфигурация нумерации разделов."""
    enabled: bool = True
    start_number: int = 1
    numbering_format: str = "decimal"  # decimal, roman, arabic
    include_in_toc: bool = True
    auto_number_headings: bool = True
    numbering_levels: int = 3  # поддержка уровней нумерации

@dataclass
class DocumentStructureConfig:
    """Конфигурация структуры документа."""
    sections: SectionConfig = field(default_factory=SectionConfig)
    toc_enabled: bool = False
    preface_enabled: bool = False
    appendix_enabled: bool = False
```

#### Шаг 2: Создать SectionProcessor

**Файл:** `doc_editor/processors/section_processor.py`

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from typing import List, Dict, Tuple
import logging

class SectionProcessor:
    """Обработчик многоуровневой нумерации разделов."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.heading_levels = {
            'Heading 1': 0,
            'Heading 2': 1,
            'Heading 3': 2,
        }
        self.section_numbers = [0, 0, 0]  # Счетчики для каждого уровня
    
    def apply_section_numbering(self, document) -> None:
        """Применить нумерацию разделов к документу."""
        if not self.config.document_structure.sections.enabled:
            return
        
        self.logger.info("Применяю многоуровневую нумерацию разделов...")
        
        for paragraph in document.paragraphs:
            style = paragraph.style.name
            
            if style not in self.heading_levels:
                continue
            
            level = self.heading_levels[style]
            self._update_section_number(level)
            self._add_numbering_to_paragraph(paragraph, level)
    
    def _update_section_number(self, level: int) -> None:
        """Обновить счетчик для указанного уровня."""
        # Увеличиваем счетчик текущего уровня
        self.section_numbers[level] += 1
        
        # Обнуляем все подуровни
        for i in range(level + 1, len(self.section_numbers)):
            self.section_numbers[i] = 0
    
    def _add_numbering_to_paragraph(self, paragraph, level: int) -> None:
        """Добавить номер к абзацу (заголовку)."""
        # Получить текущий номер
        section_num = self._get_section_number(level)
        
        # Получить текущий текст заголовка
        current_text = paragraph.text
        
        # Проверить, не добавлен ли номер уже
        if current_text and current_text[0].isdigit():
            return
        
        # Очистить параграф
        paragraph.clear()
        
        # Добавить номер
        run = paragraph.add_run(section_num + " ")
        run.bold = True
        
        # Добавить остальной текст
        run = paragraph.add_run(current_text)
        run.bold = True
    
    def _get_section_number(self, level: int) -> str:
        """Получить отформатированный номер раздела."""
        numbers = self.section_numbers[:level + 1]
        return ".".join(str(n) for n in numbers)
    
    def reset_numbering(self) -> None:
        """Сбросить счетчики нумерации."""
        self.section_numbers = [0, 0, 0]
```

#### Шаг 3: Интегрировать в Pipeline

**Файл:** `doc_editor/pipeline.py` (строки ~40-50)

```python
from doc_editor.processors.section_processor import SectionProcessor

class DocumentEditorPipeline:
    def __init__(self, config: DocumentConfig):
        # ... существующий код ...
        self.section_processor = SectionProcessor(config)
    
    def execute(self, document: Document) -> Document:
        """Выполнить весь pipeline обработки."""
        # ... существующие шаги ...
        
        # Новый шаг для Фазы 2
        if config.document_structure.sections.enabled:
            self.section_processor.apply_section_numbering(document)
        
        # ... оставшиеся шаги ...
        return document
```

### Тестирование SectionProcessor

**Файл:** `doc_editor/tests/test_section_processor.py`

```python
import pytest
from docx import Document
from docx.enum.text import WD_STYLE_TYPE
from doc_editor.processors.section_processor import SectionProcessor
from doc_editor.models.config import DocumentConfig, SectionConfig, DocumentStructureConfig

class TestSectionProcessor:
    
    @pytest.fixture
    def config(self):
        config = DocumentConfig()
        config.document_structure = DocumentStructureConfig(
            sections=SectionConfig(enabled=True, start_number=1)
        )
        return config
    
    @pytest.fixture
    def processor(self, config):
        return SectionProcessor(config)
    
    @pytest.fixture
    def doc_with_headings(self):
        """Создать документ с заголовками."""
        doc = Document()
        
        # Heading 1
        p1 = doc.add_paragraph("Введение", style='Heading 1')
        # Heading 2
        p2 = doc.add_paragraph("Общие положения", style='Heading 2')
        p3 = doc.add_paragraph("Область применения", style='Heading 2')
        # Heading 3
        p4 = doc.add_paragraph("Нормативные ссылки", style='Heading 3')
        
        return doc
    
    def test_section_numbering_applied(self, processor, doc_with_headings):
        """Проверить, что нумерация применена."""
        processor.apply_section_numbering(doc_with_headings)
        
        # Первый Heading 1 должен быть "1 Введение"
        assert doc_with_headings.paragraphs[0].text.startswith("1 ")
    
    def test_section_hierarchy(self, processor, doc_with_headings):
        """Проверить иерархию нумерации."""
        processor.apply_section_numbering(doc_with_headings)
        
        # Получить текст каждого заголовка
        headings = [p.text for p in doc_with_headings.paragraphs if p.style.name.startswith('Heading')]
        
        # Проверить правильность нумерации
        assert headings[0].startswith("1 ")    # Heading 1
        assert headings[1].startswith("1.1 ")  # Heading 2
        assert headings[2].startswith("1.2 ")  # Heading 2
    
    def test_numbering_reset(self, processor):
        """Проверить сброс нумерации."""
        processor.apply_section_numbering(Document())
        processor.reset_numbering()
        
        assert processor.section_numbers == [0, 0, 0]
```

---

## Задача 2: TOCProcessor (оглавление)

### Описание

**TOCProcessor** - компонент для автоматического построения оглавления по заголовкам.

### Базовая реализация

```python
class TOCProcessor:
    """Обработчик оглавления (Table of Contents)."""
    
    def __init__(self, config):
        self.config = config
    
    def create_toc(self, document) -> None:
        """Создать оглавление в начале документа."""
        # Реализация будет на Этапе 2
        pass
```

---

## Задача 3: PrefaceProcessor (предисловие)

### Описание

**PrefaceProcessor** - компонент для добавления предисловия/преамбулы.

### Базовая реализация

```python
class PrefaceProcessor:
    """Обработчик предисловия документа."""
    
    def __init__(self, config):
        self.config = config
    
    def add_preface(self, document) -> None:
        """Добавить предисловие в начало документа."""
        # Реализация будет на Этапе 2
        pass
```

---

## Задача 4: AppendixProcessor (приложения)

### Описание

**AppendixProcessor** - компонент для управления приложениями с буквенной нумерацией.

### Базовая реализация

```python
class AppendixProcessor:
    """Обработчик приложений документа."""
    
    def __init__(self, config):
        self.config = config
    
    def process_appendices(self, document) -> None:
        """Обработать приложения (буквенная нумерация)."""
        # Реализация будет на Этапе 2
        pass
```

---

## План реализации (неделя за неделей)

### Неделя 1: SectionProcessor
- [ ] День 1-2: Расширить config.py, создать models
- [ ] День 3-4: Реализовать SectionProcessor
- [ ] День 5: Написать unit-тесты
- [ ] День 5+: Интегрировать в Pipeline

### Неделя 2: TOCProcessor
- [ ] День 1-2: Реализовать TOCProcessor
- [ ] День 3-4: Написать тесты
- [ ] День 5: Интегрировать в Pipeline

### Неделя 3: PrefaceProcessor + AppendixProcessor
- [ ] День 1-2: Реализовать PrefaceProcessor
- [ ] День 3-4: Реализовать AppendixProcessor
- [ ] День 5: Финальная интеграция и тестирование

---

## Файлы для создания/изменения

```
doc_editor/
├── models/
│   └── config.py              (ИЗМЕНИТЬ: добавить новые конфигурации)
├── processors/
│   ├── __init__.py            (ИЗМЕНИТЬ: импортировать новые процессоры)
│   ├── section_processor.py   (СОЗДАТЬ)
│   ├── toc_processor.py       (СОЗДАТЬ)
│   ├── preface_processor.py   (СОЗДАТЬ)
│   └── appendix_processor.py  (СОЗДАТЬ)
├── pipeline.py                (ИЗМЕНИТЬ: добавить новые шаги)
└── tests/
    ├── test_section_processor.py    (СОЗДАТЬ)
    ├── test_toc_processor.py        (СОЗДАТЬ)
    ├── test_preface_processor.py    (СОЗДАТЬ)
    └── test_appendix_processor.py   (СОЗДАТЬ)
```

---

## Критерии завершения

### Фаза 2 будет считаться завершенной, когда:

✅ SectionProcessor полностью реализован и протестирован  
✅ TOCProcessor полностью реализован и протестирован  
✅ PrefaceProcessor полностью реализован и протестирован  
✅ AppendixProcessor полностью реализован и протестирован  
✅ Все компоненты интегрированы в Pipeline  
✅ Все unit-тесты проходят (100% pass rate)  
✅ Общее соответствие ГОСТ Р достигло 77%  
✅ Документация обновлена  

---

## Чек-лист перед началом

- [ ] Прочитан PHASE2_DETAILED_PLAN.md
- [ ] Понимание архитектуры SectionProcessor
- [ ] Git ветка создана: `feature/phase2-structure`
- [ ] Окружение готово (.venv активирован)
- [ ] Готов писать код! 🚀

---

**Начинайте с SectionProcessor - это приоритет #1!**

Дата: 11 февраля 2026 г.  
Статус: К началу реализации ✅
