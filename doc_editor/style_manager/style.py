from docx import Document
from docx.shared import Pt, Cm
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from typing import Dict, Any
import re


class StyleManager:
    def __init__(self, doc: Document, config: Dict[str, Any]):
        """
        Инициализация менеджера стилей.

        :param doc: Объект документа docx
        :param config: Конфигурация из YAML (полный словарь)
        """
        self.doc = doc
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Проверка наличия обязательных полей в конфиге"""
        required_paths = [
            'document.general.fonts.main',
            'document.general.spacing.line'
        ]
        for path in required_paths:
            keys = path.split('.')
            current = self.config
            for key in keys:
                if key not in current:
                    raise ValueError(f"Missing config key: {path}")
                current = current[key]

    def apply_all_styles(self) -> None:
        """Применение всех стилей из конфигурации"""
        self._setup_base_styles()
        self._setup_heading_styles()
        self._setup_special_styles()
        self._apply_line_spacing()

    def _setup_base_styles(self) -> None:
        """Настройка основных стилей документа"""
        fonts_cfg = self.config['document']['general']['fonts']

        # Основной стиль текста
        main_style = self._get_or_create_style(
            style_name='Custom_Main',
            style_type=WD_STYLE_TYPE.PARAGRAPH,
            base_style='Normal'
        )
        self._apply_font_settings(main_style, fonts_cfg['main'])

        # Стиль для приложений
        if 'appendices' in fonts_cfg:
            appendix_style = self._get_or_create_style(
                style_name='Custom_Appendix',
                style_type=WD_STYLE_TYPE.PARAGRAPH,
                base_style='Normal'
            )
            self._apply_font_settings(appendix_style, fonts_cfg['appendices'])

        # Стиль для примечаний
        if 'notes' in fonts_cfg:
            notes_style = self._get_or_create_style(
                style_name='Custom_Notes',
                style_type=WD_STYLE_TYPE.PARAGRAPH,
                base_style='Normal'
            )
            self._apply_font_settings(notes_style, fonts_cfg['notes'])

    def _setup_heading_styles(self) -> None:
        """Настройка стилей заголовков согласно иерархии"""
        hierarchy = self.config['document']['structure']['sections']['hierarchy']
        fonts_cfg = self.config['document']['general']['fonts']

        for level, section_type in enumerate(hierarchy, start=1):
            style_name = f'Heading {level}'
            heading_style = self._get_or_create_style(
                style_name=style_name,
                style_type=WD_STYLE_TYPE.PARAGRAPH,
                base_style=None
            )

            # Применяем настройки основного шрифта с возможным увеличением размера
            font_settings = fonts_cfg['main'].copy()
            if 'size' in font_settings:
                size_pt = self._parse_size(font_settings['size'])
                font_settings['size'] = f"{size_pt + (6 - level)}pt"  # Уменьшаем размер для подуровней

            self._apply_font_settings(heading_style, font_settings)

            # Настройка отступов для заголовков
            paragraph_format = heading_style.paragraph_format
            paragraph_format.space_before = Pt(12)
            paragraph_format.space_after = Pt(6)
            paragraph_format.keep_with_next = True  # Заголовок не отрывается от следующего абзаца

    def _setup_special_styles(self) -> None:
        """Настройка специальных стилей (титульная страница, колонтитулы)"""
        # Стиль для элементов титульной страницы
        title_style = self._get_or_create_style(
            style_name='Custom_Title',
            style_type=WD_STYLE_TYPE.PARAGRAPH,
            base_style='Normal'
        )
        title_style.font.name = self.config['document']['general']['fonts']['main']['family']
        title_style.font.size = Pt(14)
        title_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Стиль для колонтитулов
        header_style = self._get_or_create_style(
            style_name='Custom_Header',
            style_type=WD_STYLE_TYPE.PARAGRAPH,
            base_style='Normal'
        )
        header_style.font.size = Pt(10)
        header_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    def _apply_line_spacing(self) -> None:
        """Применение межстрочных интервалов"""
        spacing_cfg = self.config['document']['general']['spacing']
        line_spacing = float(spacing_cfg['line'])

        # Применяем ко всем стилям параграфов
        for style in self.doc.styles:
            if style.type == WD_STYLE_TYPE.PARAGRAPH:
                style.paragraph_format.line_spacing = line_spacing

        # Обработка исключений
        if 'exceptions' in spacing_cfg:
            for exception in spacing_cfg['exceptions']:
                if 'first_edition' in exception and exception['first_edition'] == 'single':
                    first_edition_style = self._get_or_create_style(
                        style_name='Custom_FirstEdition',
                        style_type=WD_STYLE_TYPE.PARAGRAPH,
                        base_style='Normal'
                    )
                    first_edition_style.paragraph_format.line_spacing = 1.0

    def _get_or_create_style(self, style_name: str, style_type: int, base_style: str = None):
        """Получает или создает стиль с указанными параметрами"""
        try:
            style = self.doc.styles[style_name]
        except KeyError:
            style = self.doc.styles.add_style(style_name, style_type)
            if base_style:
                style.base_style = self.doc.styles[base_style]
        return style

    def _apply_font_settings(self, style, font_cfg: Dict[str, str]) -> None:
        """Применяет настройки шрифта к стилю"""
        if 'family' in font_cfg:
            style.font.name = font_cfg['family']
        if 'size' in font_cfg:
            size_pt = self._parse_size(font_cfg['size'])
            style.font.size = Pt(size_pt)
        if 'bold' in font_cfg:
            style.font.bold = font_cfg['bold']
        if 'italic' in font_cfg:
            style.font.italic = font_cfg['italic']

    @staticmethod
    def _parse_size(size_str: str) -> float:
        """Парсит строку с размером (поддерживает pt, px, mm)"""
        size_str = size_str.lower().strip()

        if size_str.endswith('pt'):
            return float(size_str[:-2])
        elif size_str.endswith('px'):
            return float(size_str[:-2]) * 0.75  # Примерное преобразование px в pt
        elif size_str.endswith('mm'):
            return Cm(float(size_str[:-2])).pt
        else:
            # Если нет суффикса, считаем что это pt
            return float(size_str)

    def apply_to_existing_document(self) -> None:
        """Применяет стили ко всем существующим параграфам документа"""
        # Сопоставление оригинальных стилей с кастомными
        style_mapping = {
            'Normal': 'Custom_Main',
            'Heading 1': 'Heading 1',
            'Heading 2': 'Heading 2',
            # Добавьте другие сопоставления по необходимости
        }

        for paragraph in self.doc.paragraphs:
            original_style = paragraph.style.name
            if original_style in style_mapping:
                paragraph.style = self.doc.styles[style_mapping[original_style]]

            ''' # Принудительное применение шрифта (если стиль не сработал)
            if 'Custom_Main' in self.doc.styles:
                for run in paragraph.runs:
                    run.font.name = self.config['document']['general']['fonts']['main']['family']'''