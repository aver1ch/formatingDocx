from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import yaml
from typing import Dict, Any


class DocumentEditor:
    def __init__(self, doc_path: str):
        """Инициализация редактора документа"""
        self.doc = Document(doc_path)
        self.config = None

    def load_config(self, config_path: str) -> None:
        """Загрузка конфигурации из YAML файла"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def apply_config(self) -> None:
        """Применение конфигурации из словаря"""
        # self.config = config
        self._apply_all_rules()

    def _apply_margins(self) -> None:
        """Применение настроек полей с диагностикой"""
        print("\n[DEBUG] Applying margins...")  # Отладочный вывод
        if not self.config:
            print("[ERROR] Config not loaded!")
            return

        margins = self.config.get('document', {}).get('general', {}).get('margins')
        if not margins:
            print("[ERROR] No margins config found!")
            return

        print(f"[DEBUG] Margins config: {margins}")

        try:
            for i, section in enumerate(self.doc.sections):
                print(f"\nSection {i + 1} before:")
                print(f"Left: {section.left_margin.inches:.2f} in")
                print(f"Right: {section.right_margin.inches:.2f} in")

                section.left_margin = Inches(self._cm_to_inches(margins['left']))
                section.right_margin = Inches(self._cm_to_inches(margins['right']))
                section.top_margin = Inches(self._cm_to_inches(margins['top']))
                section.bottom_margin = Inches(self._cm_to_inches(margins['bottom']))

                print("\nAfter changes:")
                print(f"Left: {section.left_margin.inches:.2f} in")
                print(f"Right: {section.right_margin.inches:.2f} in")
        except Exception as e:
            print(f"[ERROR] Margin application failed: {str(e)}")
            raise

    def _apply_fonts(self) -> None:
        """Применение настроек шрифтов с диагностикой"""
        print("\n[DEBUG] Applying fonts...")
        if not self.config:
            print("[ERROR] Config not loaded!")
            return

        fonts = self.config.get('document', {}).get('general', {}).get('fonts', {})
        if not fonts:
            print("[ERROR] No fonts config found!")
            return

        main_font = fonts.get('main', {})
        print(f"[DEBUG] Font config: {main_font}")

        if not main_font:
            print("[ERROR] No main font config!")
            return

        try:
            for i, paragraph in enumerate(self.doc.paragraphs):  # Проверяем первые 5 параграфов
                print(f"\nParagraph {i + 1} before:")
                if paragraph.runs:
                    for run in paragraph.runs:
                        print(f"Font: {run.font.name}, Size: {run.font.size}")

                        if 'family' in main_font:
                            run.font.name = main_font['family']
                        if 'size' in main_font:
                            size_str = str(main_font['size']).lower()

                            if size_str.endswith('pt'):
                                # Если указано "14pt" - извлекаем число
                                size_pt = float(size_str.replace('pt', '').strip())
                            elif size_str.endswith('px'):
                                # Если указано пиксели - конвертируем в pt (примерно)
                                size_px = float(size_str.replace('px', '').strip())
                                size_pt = size_px * 0.75  # Примерное соотношение
                            else:
                                # Просто число - считаем что это pt
                                size_pt = float(size_str)

                            run.font.size = Pt(size_pt)

                        print("After changes:")
                        print(f"Font: {run.font.name}, Size: {run.font.size}")
        except Exception as e:
            print(f"[ERROR] Font application failed: {str(e)}")
            raise

    def _apply_all_rules(self) -> None:
        """Применение всех правил оформления"""
        self._apply_margins()
        self._apply_fonts()
        # Здесь можно добавить другие методы оформления

    @staticmethod
    def _cm_to_inches(value: str) -> float:
        """Конвертация сантиметров в дюймы (для Word)"""
        return float(value.replace('mm', '')) / 10 / 2.54

    def save(self, output_path: str) -> None:
        """Сохранение измененного документа"""
        self.doc.save(output_path)


# Функции для удобного использования без создания экземпляра класса
def format_document(input_path: str, config_path: str, output_path: str) -> None:
    """Форматирование документа по конфигу (удобная обертка)"""
    editor = DocumentEditor(input_path)
    editor.load_config(config_path)
    editor.apply_config()
    editor.save(output_path)


def format_document_with_config(input_path: str, config: Dict[str, Any], output_path: str) -> None:
    """Форматирование документа с готовым конфигом"""
    editor = DocumentEditor(input_path)
    editor.apply_config()
    editor.save(output_path)
