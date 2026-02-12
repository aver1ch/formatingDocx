# Примеры конфигураций для разных типов документов (ГОСТ Р 1.5-2004)

## Обзор

Этот файл содержит примеры YAML конфигураций для различных документов согласно ГОСТ Р 1.5-2004:
- Государственный стандарт (полный)
- Межгосударственный стандарт
- Стандарт организации (упрощенный)
- Технический регламент
- Руководство

---

## Пример 1: Государственный стандарт (полный)

**Файл:** `config_gost_full.yaml`  
**Описание:** Полный формат документа со всеми обязательными и рекомендуемыми элементами.

```yaml
document:
  general:
    margins:
      left: 20mm      # ГОСТ: левое поле
      right: 10mm     # ГОСТ: правое поле
      top: 20mm       # ГОСТ: верхнее поле
      bottom: 20mm    # ГОСТ: нижнее поле
    
    fonts:
      main:
        family: Arial     # Основной шрифт
        size: 12pt
        bold: false
      
      # Стили заголовков
      headerNum: 3        # 3 уровня заголовков
      header1:
        family: Arial
        size: 14pt
        bold: true
      header2:
        family: Arial
        size: 12pt
        bold: true
      header3:
        family: Arial
        size: 10pt
        bold: true
      
      # Специальные стили
      appendices:
        family: Arial
        size: 12pt
      notes:
        family: Arial
        size: 10pt
    
    spacing:
      line: 1.5                    # Основной интервал
      exceptions:
        - style: preface
          line: 1.5
        - style: title_page
          line: 1.5
        - style: appendix_title
          line: 1.5
    
    # Параграф (красная строка)
    paragraph:
      first_line_indent: 12.5mm
  
  structure:
    # Титульный лист
    title_page:
      enabled: true
      template_path: "doc_editor/templates/title_page_template.docx"
      image_path: "doc_editor/templates/logo.png"
      line_spacing: 1.5
      elements:
        - agency_name: "ФЕДЕРАЛЬНОЕ АГЕНСТВО\nПО ТЕХНИЧЕСКОМУ РЕГУЛИРОВАНИЮ И МЕТРОЛОГИИ"
        - standart_type: "ГОСТ Р"
        - designation: "(проект, первая редакция)"
        - title: "Название государственного стандарта"
        - status: "Настоящий проект стандарта не подлежит применению до его утверждения"
        - publisher_info: "Стандартинформ"
        - city: "Москва"
        - current_year: "202_"
      appendix: "А"
    
    # Предисловие (преамбула)
    preface:
      enabled: true
      numbering: roman          # I, II, III...
      label_style: alpha        # а), б), в)...
      content_placeholders:
        - development_info      # Сведения об организации-разработчике
        - approval_info         # Сведения об одобрении проекта
        - replacement_info      # Сведения о замене
        - patent_notice         # Оговорка об авторском праве
    
    # Содержание (оглавление)
    table_of_contents:
      enabled: true
      title: "Содержание"
      page_numbers: true
      include_appendices: true
      max_depth: 3
    
    # Введение (опционально)
    introduction:
      enabled: false
      title: "Введение"
    
    # Разделы основного текста
    sections:
      enabled: true
      max_depth: 3
      auto_numbering: true
      numbering: arabic       # 1, 2, 3...
      section_format:
        - level: 1
          style: Heading 1
          space_before: 12pt
          space_after: 6pt
        - level: 2
          style: Heading 2
          space_before: 10pt
          space_after: 4pt
        - level: 3
          style: Heading 3
          space_before: 8pt
          space_after: 2pt
    
    # Таблицы
    tables:
      enabled: true
      caption_position: top    # Подпись таблицы над таблицей
      auto_numbering: true
      numbering_format: "Таблица {number}"
    
    # Рисунки
    images:
      enabled: true
      caption_position: bottom  # Подпись рисунка под рисунком
      auto_numbering: true
      numbering_format: "Рис. {number}"
    
    # Формулы
    formulas:
      enabled: true
      auto_numbering: true
      numbering_position: right  # Номер с правой стороны
      numbering_format: "({number})"
    
    # Списки (маркированные и нумерованные)
    lists:
      enabled: true
      ordered_prefix: "—"      # Маркер для маркированных списков
      bullet_style: dash       # dash, circle, square
    
    # Библиография
    bibliography:
      enabled: true
      title: "Библиография"
      sections:
        - name: "нормативные_ссылки"
          title: "Нормативные ссылки"
          types:
            - interstate_standards      # Межгосударственные стандарты
            - national_standards        # Государственные стандарты
            - classifiers               # Классификаторы
            - codes_of_practice         # Своды правил
        - name: "informative_references"
          title: "Информационные ссылки"
          types:
            - technical_reports
            - research_papers
            - other_sources
    
    # Приложения
    appendices:
      enabled: true
      labeling_type: cyrillic  # cyrillic (А, Б, В...) или latin (A, B...)
      numbering: А, Б, В, Г, Д, Е, Ж, З, И, К, Л, М, Н, О, П, Р, С, Т, У, Ф, Х, Ц, Ч, Ш, Щ, Э, Ю, Я
      mandatory_label: "(обязательное)"
      optional_label: "(рекомендуемое)"
      reference_format: "Приложение {letter}"
    
    # Примечания
    notes:
      enabled: true
      title: "Примечания"
      numbering: arabic
      style: footnotes  # или endnotes
  
  # Нумерация страниц и колонтитулы
  numbering:
    pages:
      style: arabic              # Арабские цифры
      start_from: 1              # Начало нумерации со стр. 1
      special_sections:
        preface:
          style: roman           # Римские цифры для предисловия
          start_from: I
        appendix:
          style: arabic          # Арабские для приложений (продолжение)
          restart: false         # Продолжение общей нумерации
    
    # Колонтитулы
    headers:
      enabled: true
      different_first_page: true  # На титульнике нет колонтитулов
      
      # Верхний колонтитул (нечетные страницы)
      right_parts:
        - text: "ГОСТ Р"
          bold: true
        - text: "\n(проект, первая редакция)"
          bold: false
      
      # Верхний колонтитул (четные страницы)
      left: "Обозначение стандарта (без международных кодов)"
      
      # Нижний колонтитул
      footer_enabled: true
      page_numbers: true
      page_numbers_position: center  # center, left, right
```

---

## Пример 2: Межгосударственный стандарт (упрощенный)

**Файл:** `config_gost_interstate.yaml`

```yaml
document:
  general:
    margins:
      left: 20mm
      right: 10mm
      top: 20mm
      bottom: 20mm
    
    fonts:
      main:
        family: Arial
        size: 12pt
      headerNum: 2
      header1:
        family: Arial
        size: 14pt
        bold: true
      header2:
        family: Arial
        size: 12pt
        bold: true
    
    spacing:
      line: 1.5
  
  structure:
    title_page:
      enabled: true
      template_path: "doc_editor/templates/title_page_template.docx"
      elements:
        - agency_name: "МЕЖГОСУДАРСТВЕННЫЙ СОВЕТ ПО СТАНДАРТИЗАЦИИ"
        - standart_type: "ГОСТ"
        - title: "Название межгосударственного стандарта"
    
    preface:
      enabled: true
      numbering: roman
    
    table_of_contents:
      enabled: true
      max_depth: 2
    
    sections:
      enabled: true
      max_depth: 2
      auto_numbering: true
    
    bibliography:
      enabled: true
    
    appendices:
      enabled: true
  
  numbering:
    headers:
      enabled: true
      right: "ГОСТ (проект)"
      page_numbers: true
```

---

## Пример 3: Стандарт организации (СТО)

**Файл:** `config_sto_simple.yaml`

```yaml
document:
  general:
    margins:
      left: 20mm
      right: 10mm
      top: 20mm
      bottom: 20mm
    
    fonts:
      main:
        family: Arial
        size: 12pt
      headerNum: 2
      header1: {family: Arial, size: 13pt, bold: true}
      header2: {family: Arial, size: 12pt, bold: true}
    
    spacing:
      line: 1.5
  
  structure:
    title_page:
      enabled: true
      template_path: "doc_editor/templates/title_page_sto.docx"
      elements:
        - company_name: "ООО Компания"
        - standart_type: "СТО"
        - title: "Название стандарта организации"
    
    preface:
      enabled: false  # Не всегда обязателен
    
    table_of_contents:
      enabled: true
      max_depth: 2
    
    sections:
      enabled: true
      max_depth: 2
    
    bibliography:
      enabled: false  # Может быть необязателен
    
    appendices:
      enabled: true
  
  numbering:
    headers:
      enabled: true
      right: "СТО"
      page_numbers: true
```

---

## Пример 4: Техрегламент (ТРТУ)

**Файл:** `config_techreg.yaml`

```yaml
document:
  general:
    margins:
      left: 20mm
      right: 10mm
      top: 20mm
      bottom: 20mm
    
    fonts:
      main: {family: Arial, size: 12pt}
      headerNum: 3
      header1: {family: Arial, size: 14pt, bold: true}
      header2: {family: Arial, size: 12pt, bold: true}
      header3: {family: Arial, size: 10pt, bold: true}
    
    spacing:
      line: 1.5
  
  structure:
    title_page:
      enabled: true
      template_path: "doc_editor/templates/title_page_techreg.docx"
      elements:
        - ministry: "МИНИСТЕРСТВО..."
        - doctype: "ТЕХНИЧЕСКИЙ РЕГЛАМЕНТ"
        - title: "Название технического регламента"
    
    preface:
      enabled: true
      numbering: roman
    
    table_of_contents:
      enabled: true
      max_depth: 3
    
    sections:
      enabled: true
      max_depth: 3
    
    bibliography:
      enabled: true
    
    appendices:
      enabled: true
  
  numbering:
    headers:
      enabled: true
      right: "ТР ТУ"
      page_numbers: true
```

---

## Пример 5: Методическое руководство

**Файл:** `config_manual.yaml`

```yaml
document:
  general:
    margins:
      left: 20mm
      right: 10mm
      top: 20mm
      bottom: 20mm
    
    fonts:
      main: {family: Times New Roman, size: 12pt}
      headerNum: 2
      header1: {family: Times New Roman, size: 14pt, bold: true}
      header2: {family: Times New Roman, size: 12pt, bold: true}
    
    spacing:
      line: 1.5
  
  structure:
    title_page:
      enabled: true
      elements:
        - organization: "ОРГАНИЗАЦИЯ"
        - doctype: "МЕТОДИЧЕСКОЕ РУКОВОДСТВО"
        - title: "Название руководства"
    
    preface:
      enabled: false
    
    table_of_contents:
      enabled: true
      max_depth: 2
    
    introduction:
      enabled: true
      title: "Введение"
    
    sections:
      enabled: true
      max_depth: 2
    
    bibliography:
      enabled: true
    
    appendices:
      enabled: false  # Может отсутствовать в руководствах
  
  numbering:
    headers:
      enabled: true
      right: "Методическое руководство"
      page_numbers: true
```

---

## Профили конфигурации (Шаблоны)

### Минимальный профиль (минимум требований ГОСТ)

```yaml
# config_profile_minimal.yaml
_profile: minimal

document:
  general:
    margins: {left: 20mm, right: 10mm, top: 20mm, bottom: 20mm}
    fonts:
      main: {family: Arial, size: 12pt}
    spacing: {line: 1.5}
  
  structure:
    title_page: {enabled: true}
    table_of_contents: {enabled: false}
    preface: {enabled: false}
    bibliography: {enabled: false}
    appendices: {enabled: false}
  
  numbering:
    headers: {enabled: false}
```

### Стандартный профиль (рекомендуемый набор)

```yaml
# config_profile_standard.yaml
_profile: standard

document:
  general:
    margins: {left: 20mm, right: 10mm, top: 20mm, bottom: 20mm}
    fonts:
      main: {family: Arial, size: 12pt}
      headerNum: 2
      header1: {family: Arial, size: 14pt, bold: true}
      header2: {family: Arial, size: 12pt, bold: true}
    spacing: {line: 1.5}
  
  structure:
    title_page: {enabled: true}
    table_of_contents: {enabled: true, max_depth: 2}
    preface: {enabled: true}
    bibliography: {enabled: true}
    appendices: {enabled: true}
  
  numbering:
    headers: {enabled: true, page_numbers: true}
```

### Полный профиль (максимум функциональности)

```yaml
# config_profile_full.yaml
_profile: full

# См. Пример 1
```

---

## Использование

### Способ 1: Прямое использование файла

```python
from doc_editor.editor import DocumentEditor

editor = DocumentEditor('input.docx')
editor.load_config('configs/config_gost_full.yaml')
editor.apply_config()
editor.save('output.docx')
```

### Способ 2: Использование через REST API

```bash
curl -X POST http://localhost:5000/api/process_document \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://example.com/input.docx",
    "config_profile": "gost_full"
  }'
```

### Способ 3: Программное расширение

```python
from doc_editor.editor import DocumentEditor

base_config = 'configs/config_profile_standard.yaml'
editor = DocumentEditor('input.docx')
editor.load_config(base_config)

# Переопределяем некоторые параметры
editor.config.general.fonts['main']['size'] = '11pt'
editor.config.structure.preface.enabled = False

editor.apply_config()
editor.save('output.docx')
```

---

## Рекомендации по выбору конфигурации

| Документ | Конфигурация | Комментарий |
|----------|--------------|-----------|
| ГОСТ Р 1.5-2004 (проект) | `config_gost_full.yaml` | Полное соответствие стандарту |
| ГОСТ (межгосударственный) | `config_gost_interstate.yaml` | Упрощенный формат |
| СТО (стандарт организации) | `config_sto_simple.yaml` | Адаптировано для компаний |
| Техрегламент | `config_techreg.yaml` | Максимальная формальность |
| Внутреннее руководство | `config_manual.yaml` | Гибкий формат |
| Быстрое форматирование | `config_profile_minimal.yaml` | Основные параметры |
| Универсальный документ | `config_profile_standard.yaml` | Сбалансированный выбор |

---

## Создание собственной конфигурации

1. **Выберите профиль:**
   ```bash
   cp config_profile_standard.yaml my_config.yaml
   ```

2. **Отредактируйте параметры:**
   - Измените названия, стили, поля
   - Добавьте/удалите разделы

3. **Протестируйте:**
   ```python
   editor = DocumentEditor('test.docx')
   editor.load_config('my_config.yaml')
   editor.apply_config()
   editor.save('test_output.docx')
   ```

4. **Сохраните как шаблон:**
   ```bash
   mkdir -p config_templates
   cp my_config.yaml config_templates/
   ```

---

## Дополнительные ресурсы

- 📄 ГОСТ Р 1.5-2004: https://docs.cntd.ru/document/gost-r-1-5-2004
- 📋 ARCHITECTURE.md: Детали реализации
- 🔧 PHASE1_DETAILED_PLAN.md: Текущие задачи
- 🆘 Возникли проблемы? Смотрите GOST_COMPLIANCE_ANALYSIS.md
