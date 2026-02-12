# NEXT STEPS - Фаза 2 Этап 2: TOCProcessor

## 📋 Инструкции для следующего разработчика

**Прочитайте ЭТО перед началом работы!**

---

## 🎯 Ваша задача: Реализовать TOCProcessor

### Что это такое?

**TOCProcessor** - компонент для автоматического построения оглавления (Table of Contents) документа.

**Задача:** Извлечь все заголовки (Heading 1, 2, 3) из документа и создать оглавление с номерами страниц.

### Входные данные

- Документ с нумерованными заголовками (благодаря SectionProcessor)
- Конфигурация в `DocumentStructureConfig.toc`

### Выходные данные

- Оглавление, вставленное в начало документа (после титула, перед основным текстом)
- Форматирование: обычный текст, inden на каждом уровне, номера страниц

---

## 📚 Ресурсы

### Файлы для изучения

1. **PHASE2_DETAILED_PLAN.md** - Полный план Фазы 2
   - Раздел "Задача 2: TOCProcessor"

2. **doc_editor/processors/section_processor.py** - Пример реализации
   - Как организовать код
   - Как работать с документом python-docx
   - Как писать логирование

3. **doc_editor/tests/test_section_processor.py** - Пример тестов
   - Как писать fixtures
   - Как писать параметризованные тесты
   - Как проверять граничные случаи

4. **doc_editor/processors/toc_processor.py** - Скелет для TOCProcessor
   - Уже есть класс, нужно добавить реализацию

### Документация python-docx

```python
# Получить все параграфы с определённым стилем
headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]

# Получить номер страницы параграфа
page_num = doc.paragraphs.index(paragraph) // 55  # ПРИМЕРНО, нужно уточнить

# Добавить параграф в начало
new_para = doc.paragraphs[0].insert_paragraph_before("Новый текст")
```

---

## 🔧 Архитектура TOCProcessor

### Предлагаемая реализация

```python
class TOCProcessor:
    def __init__(self, config):
        self.config = config
    
    def create_toc(self, document) -> None:
        """Создать оглавление и вставить в начало документа."""
        if not self.config.structure.document_structure.toc.enabled:
            return
        
        # Шаг 1: Извлечь все заголовки
        headings = self._extract_headings(document)
        
        # Шаг 2: Получить номера страниц для каждого заголовка
        toc_entries = self._get_toc_entries(document, headings)
        
        # Шаг 3: Построить оглавление (список строк)
        toc_lines = self._build_toc_lines(toc_entries)
        
        # Шаг 4: Вставить оглавление в начало документа
        self._insert_toc_to_document(document, toc_lines)
    
    def _extract_headings(self, document) -> List[Paragraph]:
        """Извлечь все заголовки из документа."""
        headings = []
        for paragraph in document.paragraphs:
            if paragraph.style.name in ['Heading 1', 'Heading 2', 'Heading 3']:
                headings.append(paragraph)
        return headings
    
    def _get_toc_entries(self, document, headings) -> List[Dict]:
        """Получить инфу о каждом заголовке (уровень, текст, номер страницы)."""
        entries = []
        for heading in headings:
            level = self._get_heading_level(heading.style.name)
            page_num = self._get_paragraph_page_number(document, heading)
            entries.append({
                'level': level,
                'text': heading.text,
                'page': page_num
            })
        return entries
    
    def _build_toc_lines(self, entries) -> List[str]:
        """Построить строки оглавления с отступами."""
        lines = []
        for entry in entries:
            indent = "  " * entry['level']  # Отступ 2 символа на уровень
            line = f"{indent}{entry['text']}...{entry['page']}"
            lines.append(line)
        return lines
    
    def _insert_toc_to_document(self, document, toc_lines) -> None:
        """Вставить оглавление в начало документа."""
        # Вставить заголовок "ОГЛАВЛЕНИЕ"
        title_para = document.paragraphs[0].insert_paragraph_before(
            self.config.structure.document_structure.toc.title
        )
        title_para.style = 'Heading 1'
        
        # Вставить строки оглавления
        for line in toc_lines:
            document.paragraphs[0].insert_paragraph_before(line)
```

---

## ✅ Чек-лист для TOCProcessor

### Функциональность

- [ ] Извлечение всех заголовков (Heading 1, 2, 3)
- [ ] Определение уровня заголовка
- [ ] Получение номера страницы для каждого заголовка
- [ ] Форматирование оглавления с отступами
- [ ] Вставка оглавления в начало документа
- [ ] Поддержка конфигурации (enabled, title, page_numbers, levels)
- [ ] Обработка пустого документа
- [ ] Обработка документа без заголовков
- [ ] Сохранение форматирования

### Тестирование

- [ ] test_toc_processor_initialization
- [ ] test_toc_disabled
- [ ] test_simple_toc_creation
- [ ] test_hierarchical_toc
- [ ] test_toc_with_page_numbers
- [ ] test_empty_document_toc
- [ ] test_document_without_headings
- [ ] test_toc_title_customization
- [ ] test_toc_levels_filter (if levels < 3)
- [ ] test_toc_insertion_position
- [ ] test_multiple_toc_creation_in_sequence
- [ ] test_toc_formatting_styles

### Интеграция

- [ ] Добавлено в Pipeline (после SectionProcessor)
- [ ] Экспортировано в processors/__init__.py
- [ ] Работает с остальными компонентами
- [ ] Не ломает Фазу 1 тесты

### Документация

- [ ] Docstrings для всех методов
- [ ] Примеры использования
- [ ] Комментарии для сложной логики

---

## 🧪 Написание тестов

### Пример структуры тестов

```python
class TestTOCProcessor:
    @pytest.fixture
    def toc_config(self):
        return TOCConfig(
            enabled=True,
            title="ОГЛАВЛЕНИЕ",
            page_numbers=True,
            levels=3
        )
    
    @pytest.fixture
    def document_config(self, toc_config):
        doc_structure = DocumentStructureConfig(toc=toc_config)
        # ... полная конфигурация
        return config
    
    @pytest.fixture
    def processor(self, document_config):
        return TOCProcessor(document_config)
    
    def test_simple_toc_creation(self, processor):
        doc = Document()
        doc.add_paragraph("Раздел 1", style='Heading 1')
        doc.add_paragraph("Подраздел 1.1", style='Heading 2')
        
        processor.create_toc(doc)
        
        # Проверить, что оглавление добавлено
        assert "ОГЛАВЛЕНИЕ" in [p.text for p in doc.paragraphs]
```

---

## 💡 Советы и подсказки

### Работа с номерами страниц

**Проблема:** python-docx не предоставляет прямой доступ к номерам страниц.

**Решение:** 
```python
# Вариант 1: Использовать Field codes (более сложно)
# Вариант 2: Приблизительно рассчитать (55 строк на страницу)
# Вариант 3: Использовать python-docx-oxml для доступа к полям

# Рекомендуется: Вариант 3 (самый надежный)
```

### Форматирование оглавления

- Используйте style 'Normal' или 'TOC' (если есть)
- Отступы можно делать через пробелы или через `paragraph.paragraph_format.left_indent`
- Форматирование обычного текста (не жирный, не курсив)

### Обработка граничных случаев

- Пустой документ → вывести предупреждение, не падать
- Документ без заголовков → создать пустое оглавление
- Оглавление уже существует → перестроить (или пропустить)

---

## 📊 Метрики успеха

Когда TOCProcessor будет готов:

- ✅ 12+ unit-тестов (все пройдены)
- ✅ 100% pass rate для всех 41+ тестов (Фаза 1 + этап 1 Фазы 2 + новые)
- ✅ GOST соответствие 50% → ~58% (увеличение на ~8%)
- ✅ Полная интеграция в Pipeline
- ✅ Код готов к code review
- ✅ Документация завершена

---

## 🔗 Полезные ссылки

- [python-docx documentation](https://python-docx.readthedocs.io/)
- [PHASE2_DETAILED_PLAN.md](PHASE2_DETAILED_PLAN.md)
- [SectionProcessor implementation](doc_editor/processors/section_processor.py)
- [Existing tests](doc_editor/tests/test_section_processor.py)

---

## ❓ Вопросы?

**Перед началом убедитесь, что:**

- [ ] Понимаете архитектуру SectionProcessor
- [ ] Прочитали PHASE2_DETAILED_PLAN.md раздел "Задача 2"
- [ ] Изучили примеры в test_section_processor.py
- [ ] Готовы писать тесты ДО реализации (TDD)
- [ ] Git ветка создана: `feature/phase2-toc`

---

## 🚀 Начните с этого

1. Создайте ветку: `git checkout -b feature/phase2-toc`
2. Прочитайте: [PHASE2_DETAILED_PLAN.md](PHASE2_DETAILED_PLAN.md)
3. Напишите тесты: `doc_editor/tests/test_toc_processor.py`
4. Реализуйте: `doc_editor/processors/toc_processor.py`
5. Запустите: `pytest doc_editor/tests/`
6. Создайте PR!

---

**Удачи! Вы справитесь! 💪**

*Дата создания: 11 февраля 2026 г.*
