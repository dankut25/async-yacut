"""View-функции для сайта yacut."""

from flask import flash, redirect, render_template, request

from . import app
from .error_handlers import ErrorInDBSave, ErrorInURLNaming
from .forms import FileUploadForm, URLForm
from .models import URLMap
from .utils import async_upload_files_to_yadisc, get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index():
    """Функция для укорачивания ссылок."""
    form = URLForm()
    url = None

    if form.validate_on_submit():
        try:
            url = get_unique_short_id(
                form.original_link.data, form.custom_id.data
            )
        except ErrorInURLNaming:
            flash('Предложенный вариант короткой ссылки уже существует.')
        except ErrorInDBSave:
            flash('Ошибка сохранения записи в БД.')

    return render_template('index.html', form=form, url=url)


@app.route('/<short_id>')
def link_redirect(short_id):
    """Перенаправление с короткой ссылки на основной путь."""
    link = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(link.original)


@app.route('/files', methods=['GET', 'POST'])
async def upload_files_view():
    """Функция для страницы загрузки файлов на Яндекс диск.

    Принимает файлы из формы, которые нужно загрузить на Яндекс диск.
    Загружает их на диск и возвращает словарь для страницы с именем файла,
    короткой ссылкой для скачивания и пустым полем ошибка.
    Если в процессе загрузки произойдет ошибка, то поле url
    в словаре будет пустым, а в ключе error указан этап, на котором
    произошла ошибка.
    """
    form = FileUploadForm()
    files = []
    host_url = 'http://localhost'
    if request.method == 'POST':
        files_data = (
            form.files.data if form.validate_on_submit() else
            request.files.getlist('files')
        )
        if files_data:
            files = await async_upload_files_to_yadisc(files_data, host_url)

    return render_template('upload_files.html', form=form, files=files)
