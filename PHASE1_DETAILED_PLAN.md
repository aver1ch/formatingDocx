# План реализации Фазы 1: Исправление текущих проблем

## Общая информация

**Дедлайн:** 1-2 недели  
**Приоритет:** КРИТИЧЕСКИЙ  
**Статус:** К началу реализации

---

## Задача 1: Форматирование колонтитула (жирный ГОСТ Р)

### Описание проблемы
Текущая реализация `HeaderFooterProcessor.py` добавляет весь текст колонтитула одинаковым форматом. Согласно требованиям:
- "ГОСТ Р" должен быть **жирным**
- "(проект, первая редакция)" должен быть **обычным**

**Пример желаемого результата:**
```
ГОСТ Р (проект, первая редакция)
```
Где `ГОСТ Р` - жирный, остальное - нет.

### Текущий код (проблемный)
```python
# header_footer_processor.py, строки ~90-95
run = paragraph.add_run(text)  # Весь текст одинаково
main_family = self.config.general.fonts['main'].get('family', None)
```

### Решение

#### Шаг 1: Расширить HeadersConfig (models/config.py)

Добавить поддержку форматирования:

```python
@dataclass
class HeaderTextPart:
    """Часть текста колонтитула с форматированием."""
    text: str
    bold: bool = False
    italic: bool = False
    font_family: Optional[str] = None

@dataclass
class HeadersConfig:
    """Конфигурация колонтитулов."""
    enabled: bool = False
    left: str = ""  # Остается для обратной совместимости
    right: str = ""
    left_parts: List[HeaderTextPart] = field(default_factory=list)  # Новое
    right_parts: List[HeaderTextPart] = field(default_factory=list)  # Новое
    page_numbers: bool = False
```

#### Шаг 2: Обновить HeaderFooterProcessor

```python
def _add_text_to_element_with_formatting(self, element, text_parts: List[Dict], align: str) -> None:
    """Добавляет текст с поддержкой форматирования."""
    if element.paragraphs:
        paragraph = element.paragraphs[0]
        paragraph.clear()
    else:
        paragraph = element.add_paragraph()
    
    if align == 'left':
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    elif align == 'right':
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    
    # Добавляем каждую часть с её форматированием
    for part in text_parts:
        run = paragraph.add_run(part['text'])
        run.bold = part.get('bold', False)
        run.italic = part.get('italic', False)
        
        font_family = part.get('font_family') or \
                      self.config.general.fonts['main'].get('family', 'Arial')
        run.font.name = font_family
```

#### Шаг 3: Обновить YAML конфигурацию

```yaml
numbering:
  headers:
    enabled: true
    right_parts:
      - text: "ГОСТ Р"
        bold: true
      - text: "\n(проект, первая редакция)"
        bold: false
    left: "Обозначение стандарта"
    page_numbers: true
```

### Тестирование
- [ ] Проверить, что ГОСТ Р отображается жирным
- [ ] Проверить, что подпись не жирная
- [ ] Проверить совместимость со старой конфигурацией (поле `left`/`right`)

---

## Задача 2: Межстрочный интервал на титульнике

### Описание проблемы
Межстрочный интервал, установленный в конфигурации (1.5), может не применяться к титульному листу после его рендера через `docxtpl`.

### Анализ текущего кода

**TitleProcessor** (`title_processor.py`, строка ~62-75):
```python
def _apply_font_to_doc(title_doc, main_family):
    # Применяет шрифт, но не интервалы
```

**StyleProcessor** не обрабатывает титульный лист, т.к. он добавляется позже.

### Решение

#### Шаг 1: Расширить TitlePageConfig (models/config.py)

```python
@dataclass
class TitlePageConfig:
    """Конфигурация титульного листа."""
    # ... существующие поля ...
    line_spacing: float = 1.5  # Новое
    spacing_before: float = 0.0
    spacing_after: float = 0.0
```

#### Шаг 2: Создать метод в TitleProcessor

```python
def _apply_formatting_to_doc(self, doc: Document, title_config: TitlePageConfig) -> None:
    """Применяет форматирование (интервалы, шрифты) к всему документу."""
    main_family = self.config.general.fonts['main'].get('family', 'Arial')
    
    # Применяем интервалы ко всем параграфам
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing = title_config.line_spacing
        paragraph.paragraph_format.space_before = Pt(title_config.spacing_before)
        paragraph.paragraph_format.space_after = Pt(title_config.spacing_after)
        
        # Применяем шрифт
        for run in paragraph.runs:
            if not run.font.name:
                run.font.name = main_family
    
    # Применяем интервалы к таблицам
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing = title_config.line_spacing
```

#### Шаг 3: Вызвать в pipeline после добавления титула

В `title_processor.py`, метод `_add_title_page`:

```python
# После рендера
title_doc.render(context)

# Применяем форматирование
self._apply_formatting_to_doc(title_doc, title_config)
```

### Конфигурация YAML

```yaml
structure:
  title_page:
    template_path: "doc_editor/templates/title_page_template.docx"
    enabled: true
    line_spacing: 1.5  # Явно указываем интервал
    elements:
      - agency_name: "..."
```

### Тестирование
- [ ] Проверить интервал в рендеренном титуле
- [ ] Убедиться, что он не перекрывает другие параметры
- [ ] Проверить таблицы на титульнике

---

## Задача 3: Форматирование таблицы на титульнике

### Описание проблемы
Таблица в шаблоне `title_page_template.docx` может терять форматирование:
- Неправильная ширина столбцов
- Неправильное выравнивание текста
- Неправильные отступы в ячейках

### Анализ

Проблема в методе `TitleProcessor._apply_font_to_doc()` - он применяет шрифт, но не проверяет таблицы.

### Решение

#### Шаг 1: Улучшить обработку таблиц в TitleProcessor

```python
def _apply_formatting_to_doc(self, doc: Document, title_config: TitlePageConfig) -> None:
    """Применяет форматирование ко всему документу, включая таблицы."""
    main_family = self.config.general.fonts['main'].get('family', 'Arial')
    
    # ... код для параграфов ...
    
    # Применяем форматирование к таблицам
    for table in doc.tables:
        self._format_table(table, main_family, title_config)

def _format_table(self, table, font_family: str, config: TitlePageConfig) -> None:
    """Форматирует таблицу согласно конфигурации."""
    for row in table.rows:
        for cell in row.cells:
            # Применяем шрифт ко всем параграфам в ячейке
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.line_spacing = config.line_spacing
                
                for run in paragraph.runs:
                    if not run.font.name:
                        run.font.name = font_family
                
                # Убеждаемся, что выравнивание корректное
                # (если оно было установлено в шаблоне, сохраняем)
```

#### Шаг 2: Добавить конфигурацию для таблиц титула

Расширить `TitlePageConfig`:

```python
@dataclass
class TableFormatConfig:
    """Конфигурация форматирования таблиц в титуле."""
    preserve_existing: bool = True  # Сохранять существующее форматирование
    apply_font: bool = True  # Применять основной шрифт
    apply_spacing: bool = True  # Применять интервалы

@dataclass
class TitlePageConfig:
    # ... существующие поля ...
    table_format: TableFormatConfig = field(default_factory=TableFormatConfig)
```

#### Шаг 3: Конфигурация YAML

```yaml
structure:
  title_page:
    template_path: "doc_editor/templates/title_page_template.docx"
    enabled: true
    line_spacing: 1.5
    table_format:
      preserve_existing: true
      apply_font: true
      apply_spacing: true
    elements:
      - agency_name: "..."
```

### Тестирование
- [ ] Запустить локальный тест с текущим шаблоном
- [ ] Проверить ширину столбцов таблицы
- [ ] Проверить выравнивание текста в ячейках
- [ ] Проверить отступы (padding) в ячейках
- [ ] Сравнить с оригинальным шаблоном

---

## Порядок реализации

### Week 1

**День 1-2:** Задача 1 (Форматирование колонтитула)
- Обновить `models/config.py`
- Обновить `processors/header_footer_processor.py`
- Обновить конфиг YAML в `tests/test_data/formatConfig.yaml`
- Тестирование

**День 3-4:** Задача 2 (Межстрочный интервал)
- Обновить `models/config.py`
- Обновить `processors/title_processor.py`
- Тестирование

**День 5:** Задача 3 (Таблица на титульнике)
- Обновить `processors/title_processor.py`
- Обновить `models/config.py`
- Тестирование интеграции

### Week 2

**День 1-2:** Integration Testing
- Комплексное тестирование всех трех фич
- Проверка обратной совместимости

**День 3:** Documentation
- Обновить `README.md`
- Обновить примеры конфигурации

---

## Критерии готовности

### Задача 1 ✅ Готово, когда:
- [ ] ГОСТ Р отображается жирным в колонтитуле
- [ ] Остальной текст обычным
- [ ] Старая конфигурация все еще работает
- [ ] Тесты проходят

### Задача 2 ✅ Готово, когда:
- [ ] Межстрочный интервал 1.5 применяется ко всем элементам титула
- [ ] Интервал не переопределяется другими процессорами
- [ ] Таблицы имеют правильный интервал
- [ ] Тесты проходят

### Задача 3 ✅ Готово, когда:
- [ ] Таблица на титуле имеет правильное форматирование
- [ ] Ширина столбцов не сбивается
- [ ] Выравнивание текста верное
- [ ] Визуально соответствует шаблону
- [ ] Тесты проходят

---

## Тестовые сценарии

### Тест 1.1: Жирный ГОСТ Р
```python
# tests/test_phase1_task1.py
def test_header_bold_formatting():
    editor = DocumentEditor('test_docs/input.docx')
    editor.load_config('test_configs/bold_header.yaml')
    editor.apply_config()
    
    doc = Document(editor.doc)
    header = doc.sections[0].header
    
    # Проверяем, что "ГОСТ Р" жирный
    assert any(run.bold for run in header.paragraphs[0].runs)
```

### Тест 2.1: Межстрочный интервал
```python
def test_title_line_spacing():
    editor = DocumentEditor('test_docs/input.docx')
    editor.load_config('test_configs/spacing.yaml')
    editor.apply_config()
    
    doc = Document(editor.doc)
    # Проверяем интервал на титульнике
    for para in doc.paragraphs[:10]:  # Первые 10 параграфов - титул
        assert para.paragraph_format.line_spacing == 1.5
```

### Тест 3.1: Таблица на титульнике
```python
def test_title_table_formatting():
    editor = DocumentEditor('test_docs/input.docx')
    editor.load_config('test_configs/title_with_table.yaml')
    editor.apply_config()
    
    doc = Document(editor.doc)
    # Проверяем таблицу
    table = doc.tables[0]
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                assert para.paragraph_format.line_spacing == 1.5
```

---

## Зависимости и потенциальные конфликты

| Компонент | Зависит от | Потенциальный конфликт |
|-----------|-----------|----------------------|
| HeaderFooterProcessor | StyleProcessor | ❌ Нет |
| TitleProcessor | StyleProcessor | ⚠️ Возможен конфликт интервалов |
| Pipeline | Все процессоры | ✅ Нужен порядок выполнения |

**Рекомендуемый порядок в Pipeline:**
```
1. StyleProcessor (базовые стили и интервалы)
2. MarginsProcessor (поля)
3. TitleProcessor (титул с его интервалами)
4. HeaderFooterProcessor (колонтитулы)
```

---

## Документация для обновления

- [ ] [README.md](README.md) - примеры использования новых параметров
- [ ] [ARCHITECTURE.md](ARCHITECTURE.md) - обновить описание HeaderFooterProcessor
- [ ] Inline documentation в код (docstrings)
- [ ] Примеры конфигурации в `doc_editor/tests/test_data/`

---

## Чек-лист для PR

- [ ] Все тесты проходят
- [ ] Код следует PEP8
- [ ] Документация обновлена
- [ ] Обратная совместимость проверена
- [ ] Нет временных файлов или отладочного кода
- [ ] Type hints добавлены для новых методов
