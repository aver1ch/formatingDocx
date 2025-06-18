from docx import Document
from docx.shared import Pt, Inches, Mm, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.section import WD_SECTION_START 
import yaml
import logging
from typing import Dict, Any, Optional

# Предполагается, что эти модули существуют
try:
    from doc_editor.style_manager.style import StyleManager
    from doc_editor.doc_builder.title import TitlePageManager
except ImportError as e:
    logging.error(f"Ошибка импорта модулей: {e}")
    raise

# Настройка локального логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class DocumentFormattingError(Exception):
    """Базовое исключение для ошибок форматирования документа."""
    pass


class DocumentEditor:
    def __init__(self, doc_path: str):
        if not isinstance(doc_path, str):
            logger.error(f"doc_path must be a string, got {type(doc_path)}")
            raise TypeError("doc_path must be a string")
        try:
            self.doc = Document(doc_path)
            self.doc_path = doc_path
            self.output_path = None
            self.config = None
            self.style_manager = None
            self.structure_builder = None
            self.logger = logger
            self.logger.info(f"Документ загружен: {doc_path}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки документа {doc_path}: {e}")
            raise DocumentFormattingError(f"Не удалось загрузать документ: {e}")

    def load_config(self, config_path: str) -> None:
        """
        Загрузка конфигурации из YAML файла.
        
        Args:
            config_path: Путь к файлу конфигурации.
            
        Raises:
            DocumentFormattingError: Если файл не найден или некорректен.
        """
        if not isinstance(config_path, str):
            self.logger.error(f"config_path must be a string, got {type(config_path)}")
            raise TypeError("config_path must be a string")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self._validate_config()
            self.style_manager = StyleManager(self.doc, self.config)
            self.structure_builder = TitlePageManager(self.config)
            self.logger.info(f"Конфигурация загружена: {config_path}")
        except FileNotFoundError:
            self.logger.error(f"Файл конфигурации не найден: {config_path}")
            raise DocumentFormattingError(f"Файл конфигурации не найден: {config_path}")
        except yaml.YAMLError as e:
            self.logger.error(f"Ошибка парсинга YAML: {e}")
            raise DocumentFormattingError(f"Некорректный формат YAML: {e}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            raise DocumentFormattingError(f"Ошибка загрузки конфигурации: {e}")

    def _validate_config(self) -> None:
        """
        Валидация обязательных полей конфигурации.
        
        Raises:
            DocumentFormattingError: Если отсутствуют обязательные поля.
        """
        required_paths = [
            ['document', 'general', 'margins'],
            ['document', 'general', 'fonts'],
            ['document', 'general', 'spacing'],
            ['document', 'structure']
        ]
        for path in required_paths:
            current = self.config
            for key in path:
                if not isinstance(current, dict) or key not in current:
                    self.logger.error(f"Отсутствует обязательное поле: {'.'.join(path)}")
                    raise DocumentFormattingError(f"Отсутствует обязательное поле: {'.'.join(path)}")
                current = current[key]

    def apply_margins(self) -> None:
        """
        Применение настроек полей документа.
        
        Raises:
            DocumentFormattingError: Если настройки некорректны.
        """
        try:
            margins_config = self.config['document']['general']['margins']
            self.logger.info("Применение настроек полей документа")
            for i, section in enumerate(self.doc.sections):
                section.left_margin = self._parse_measurement(margins_config['left'])
                section.right_margin = self._parse_measurement(margins_config['right'])
                section.top_margin = self._parse_measurement(margins_config['top'])
                section.bottom_margin = self._parse_measurement(margins_config['bottom'])
                self.logger.debug(f"Поля установлены для секции {i+1}: "
                                f"левое={margins_config['left']}, правое={margins_config['right']}, "
                                f"верхнее={margins_config['top']}, нижнее={margins_config['bottom']}")
            self.logger.info(f"Поля успешно применены к {len(self.doc.sections)} секциям")
        except KeyError as e:
            self.logger.error(f"Отсутствует параметр полей: {e}")
            raise DocumentFormattingError(f"Отсутствует параметр полей в конфигурации: {e}")
        except Exception as e:
            self.logger.error(f"Ошибка применения полей: {e}")
            raise DocumentFormattingError(f"Ошибка применения полей: {e}")

    def _parse_measurement(self, value: str) -> object:
        """
        Парсинг размеров из строки (поддерживает mm, cm, pt, in).
        
        Args:
            value: Значение размера (строка или число).
            
        Returns:
            Объект размера (Pt, Mm, Cm, Inches).
            
        Raises:
            DocumentFormattingError: Если формат некорректен.
        """
        try:
            if isinstance(value, (int, float)):
                return Pt(float(value))
            value = str(value).strip().lower()
            if value.endswith('mm'):
                return Mm(float(value[:-2]))
            elif value.endswith('cm'):
                return Cm(float(value[:-2]))
            elif value.endswith('pt'):
                return Pt(float(value[:-2]))
            elif value.endswith('in') or value.endswith('"'):
                return Inches(float(value[:-2] if value.endswith('in') else value[:-1]))
            else:
                return Pt(float(value))
        except (ValueError, TypeError) as e:
            self.logger.error(f"Ошибка парсинга размера '{value}': {e}")
            raise DocumentFormattingError(f"Некорректный формат размера '{value}': {e}")

    def build_document_structure(self) -> None:
        """
        Строит структуру документа.
        
        Raises:
            DocumentFormattingError: Если структура не может быть построена.
        """
        try:
            self.doc.save(self.doc_path)
            self.structure_builder.add_title_page(self.doc_path, "doc_with_title.docx")
            self.doc = Document("doc_with_title.docx")
            self.doc_path = "doc_with_title.docx"
            self.logger.info("Структура документа успешно построена")
        except Exception as e:
            self.logger.error(f"Ошибка построения структуры документа: {e}")
            raise DocumentFormattingError(f"Ошибка построения структуры: {e}")

    def apply_config(self) -> None:
        """
        Применение всей конфигурации к документу.
        
        Raises:
            ValueError: Если конфигурация не загружена.
            DocumentFormattingError: Если применение конфигурации не удалось.
        """
        if not self.config:
            self.logger.error("Конфигурация не загружена")
            raise ValueError("Конфигурация не загружена")
        try:
            self.logger.info("Начало применения конфигурации к документу")

            self.apply_margins()
            self.build_document_structure()
            self.apply_margins()
            self.logger.info("Конфигурация успешно применена к документу")
        except Exception as e:
            self.logger.error(f"Ошибка применения конфигурации: {e}")
            raise DocumentFormattingError(f"Ошибка применения конфигурации: {e}")

    def save(self, output_path: str) -> None:
        """
        Сохранение документа.
        
        Args:
            output_path: Путь для сохранения файла.
            
        Raises:
            DocumentFormattingError: Если сохранение не удалось.
        """
        if not isinstance(output_path, str):
            self.logger.error(f"output_path must be a string, got {type(output_path)}")
            raise TypeError("output_path must be a string")
        try:
            self.doc.save(output_path)
            self.logger.info(f"Документ сохранен: {output_path}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения документа {output_path}: {e}")
            raise DocumentFormattingError(f"Ошибка сохранения документа: {e}")