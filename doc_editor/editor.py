# doc_editor/editor.py
from docx import Document
from docx.shared import Pt, Inches, Mm, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import yaml
import logging
from typing import Dict, Any, Optional
from doc_editor.style_manager.style import StyleManager
from doc_editor.doc_builder.builder import DocumentStructureBuilder

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentFormattingError(Exception):
    """Базовое исключение для ошибок форматирования документа"""
    pass


class DocumentEditor:
    def __init__(self, doc_path: str):
        try:
            self.doc = Document(doc_path)
            self.config = None
            self.style_manager = None
            self.structure_builder = None
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
            self.logger.info(f"Документ загружен: {doc_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки документа {doc_path}: {e}")
            raise DocumentFormattingError(f"Не удалось загрузить документ: {e}")

    def load_config(self, config_path: str) -> None:
        """Загрузка конфигурации из YAML файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            self._validate_config()
            
            self.style_manager = StyleManager(self.doc, self.config)
            self.structure_builder = DocumentStructureBuilder(self.doc, self.config)
            
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
        """Валидация обязательных полей конфигурации"""
        required_paths = [
            ['document', 'general', 'margins'],
            ['document', 'general', 'fonts'],
            ['document', 'general', 'spacing']
        ]
        
        for path in required_paths:
            current = self.config
            for key in path:
                if not isinstance(current, dict) or key not in current:
                    raise DocumentFormattingError(f"Отсутствует обязательное поле: {'.'.join(path)}")
                current = current[key]

    def apply_margins(self) -> None:
        """Применение настроек полей документа"""
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
        """Парсинг размеров из строки (поддерживает mm, cm, pt, in)"""
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
                # По умолчанию считаем в пунктах
                return Pt(float(value))
                
        except (ValueError, TypeError) as e:
            self.logger.error(f"Ошибка парсинга размера '{value}': {e}")
            raise DocumentFormattingError(f"Некорректный формат размера '{value}': {e}")


    def apply_config(self) -> None:
        """Применение всей конфигурации к документу"""
        if not self.config:
            raise ValueError("Конфигурация не загружена")

        try:
            self.logger.info("Начало применения конфигурации к документу")
            
            # Применяем базовые настройки форматирования
            self.apply_margins()
            # self.apply_fonts()
            # self.apply_spacing()
            
            # Применяем стили через StyleManager
            self.style_manager.apply_all_styles()
            
            # Строим структуру документа
            self.structure_builder.build_document_structure()
            
            # Применяем стили к существующему содержимому
            self.style_manager.apply_to_existing_document()
            
            self.logger.info("Конфигурация успешно применена к документу")
            
        except Exception as e:
            self.logger.error(f"Ошибка применения конфигурации: {e}")
            raise DocumentFormattingError(f"Ошибка применения конфигурации: {e}")

    def save(self, output_path: str) -> None:
        """Сохранение документа"""
        try:
            self.doc.save(output_path)
            self.logger.info(f"Документ сохранен: {output_path}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения документа {output_path}: {e}")
            raise DocumentFormattingError(f"Ошибка сохранения документа: {e}")
