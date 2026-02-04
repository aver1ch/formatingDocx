from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class FontConfig:
    """Конфигурация шрифта."""
    family: str
    size: str = "12pt"
    bold: bool = False
    italic: bool = False


@dataclass
class MarginsConfig:
    """Конфигурация полей документа."""
    left: str = "20mm"
    right: str = "10mm"
    top: str = "20mm"
    bottom: str = "20mm"


@dataclass
class SpacingConfig:
    """Конфигурация межстрочных интервалов."""
    line: float = 1.5
    exceptions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GeneralConfig:
    """Основные настройки документа."""
    margins: MarginsConfig
    fonts: Dict[str, Any]  # main, appendices, notes, headerNum, header1, header2, etc
    spacing: SpacingConfig


@dataclass
class TitlePageConfig:
    """Конфигурация титульного листа."""
    template: str = ""
    template_path: str = ""
    image_path: str = ""
    enabled: bool = True
    elements: List[Dict[str, str]] = field(default_factory=list)
    appendix: str = "А"


@dataclass
class HeadersConfig:
    """Конфигурация колонтитулов."""
    enabled: bool = False
    left: str = ""
    right: str = ""
    page_numbers: bool = False


@dataclass
class NumberingConfig:
    """Конфигурация нумерации."""
    headers: HeadersConfig = field(default_factory=HeadersConfig)
    pages: Optional[Dict[str, Any]] = None


@dataclass
class StructureConfig:
    """Конфигурация структуры документа."""
    title_page: TitlePageConfig = field(default_factory=TitlePageConfig)
    sections: Optional[Dict[str, Any]] = None
    numbering: NumberingConfig = field(default_factory=NumberingConfig)


@dataclass
class DocumentConfig:
    """Полная конфигурация документа."""
    general: GeneralConfig
    structure: StructureConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentConfig":
        """Создаёт объект конфига из словаря."""
        doc_data = data.get('document', {})
        
        # Парсим general
        general_data = doc_data.get('general', {})
        margins_data = general_data.get('margins', {})
        margins = MarginsConfig(**margins_data) if margins_data else MarginsConfig()
        
        fonts_data = general_data.get('fonts', {})
        spacing_data = general_data.get('spacing', {})
        spacing = SpacingConfig(**spacing_data) if spacing_data else SpacingConfig()
        
        general = GeneralConfig(
            margins=margins,
            fonts=fonts_data,
            spacing=spacing
        )
        
        # Парсим structure
        structure_data = doc_data.get('structure', {})
        title_page_data = structure_data.get('title_page', {})
        title_page = TitlePageConfig(**title_page_data) if title_page_data else TitlePageConfig()

        # Нумерация и заголовки находятся на уровне `document.numbering` в YAML
        numbering_data = doc_data.get('numbering', {})
        headers_data = numbering_data.get('headers', {})
        headers = HeadersConfig(**headers_data) if headers_data else HeadersConfig()
        numbering = NumberingConfig(
            headers=headers,
            pages=numbering_data.get('pages')
        )
        
        structure = StructureConfig(
            title_page=title_page,
            sections=structure_data.get('sections'),
            numbering=numbering
        )
        
        return cls(general=general, structure=structure)
