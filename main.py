from flask import Flask, request, jsonify, send_file
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import yaml
import requests
import os
import uuid
import tempfile
from urllib.parse import urlparse

app = Flask(__name__)


class DocumentEditor:
    def __init__(self, doc_path, config):
        self.doc = Document(doc_path)
        self.config = config

    def apply_margins(self):
        margins = self.config['document']['general']['margins']
        sections = self.doc.sections
        for section in sections:
            section.left_margin = Inches(float(margins['left'].replace('cm', '')) / 2.54)
            section.right_margin = Inches(float(margins['right'].replace('cm', '')) / 2.54)
            section.top_margin = Inches(float(margins['top'].replace('cm', '')) / 2.54)
            section.bottom_margin = Inches(float(margins['bottom'].replace('cm', '')) / 2.54)

    def apply_fonts(self):
        fonts = self.config['document']['general']['fonts']
        # Применяем основной шрифт ко всему документу
        main_font = fonts['main']
        for paragraph in self.doc.paragraphs:
            for run in paragraph.runs:
                run.font.name = main_font['family']
                run.font.size = Pt(float(main_font['size']))

    def apply_spacing(self):
        spacing = self.config['document']['general']['spacing']
        line_spacing = float(spacing['line'])
        for paragraph in self.doc.paragraphs:
            paragraph.paragraph_format.line_spacing = line_spacing

    def process_title_page(self):
        title_page = self.config['document']['structure']['title_page']
        # Здесь должна быть логика обработки титульной страницы
        # Например, добавление элементов из конфига
        for element in title_page['elements']:
            for key, value in element.items():
                # Поиск и замена или добавление элементов
                pass

    def process_numbering(self):
        numbering = self.config['document']['numbering']
        # Обработка нумерации страниц
        if 'pages' in numbering:
            # Логика настройки нумерации страниц
            pass

        # Обработка колонтитулов
        if 'headers' in numbering:
            for section in self.doc.sections:
                header = section.header
                if numbering['headers']['left']:
                    paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
                    paragraph.text = numbering['headers']['left']
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

                if numbering['headers']['right']:
                    paragraph = header.paragraphs[1] if len(header.paragraphs) > 1 else header.add_paragraph()
                    paragraph.text = numbering['headers']['right']
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    def apply_all_rules(self):
        self.apply_margins()
        self.apply_fonts()
        self.apply_spacing()
        self.process_title_page()
        self.process_numbering()
        # Здесь можно добавить обработку других разделов конфига


def download_file(url, save_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@app.route('/api/process_document', methods=['POST'])
def process_document():
    # Получаем данные из запроса
    data = request.json
    if not data or 'document_url' not in data or 'config' not in data:
        return jsonify({'error': 'Missing document_url or config in request'}), 400

    document_url = data['document_url']
    config_data = data['config']

    # Валидация URL
    #if not is_valid_url(document_url):
     #   return jsonify({'error': 'Invalid document URL'}), 400

    # Парсинг конфига
    try:
        config = yaml.safe_load(config_data)
    except yaml.YAMLError as e:
        return jsonify({'error': f'Invalid YAML config: {str(e)}'}), 400

    # Создаем временные файлы
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Скачиваем документ
            input_path = os.path.join(temp_dir, 'input.docx')
            download_file(document_url, input_path)

            # Обрабатываем документ
            output_path = os.path.join(temp_dir, 'output.docx')
            editor = DocumentEditor(input_path, config)
            editor.apply_all_rules()
            editor.doc.save(output_path)

            # Отправляем результат
            return send_file(
                output_path,
                as_attachment=True,
                download_name='formatted_document.docx',
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Failed to download document: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Document processing failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)