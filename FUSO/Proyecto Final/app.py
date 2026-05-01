# app.py
# 
from flask import Flask, request, render_template, send_from_directory
from src.model import train_and_evaluate, get_dataset_statistics, perform_eda, generate_synthetic_dataset, \
    compare_execution
import os
import glob
from src.model import DATASETS
from src.model import MODELS
import time
from memory_profiler import memory_usage
import gc

main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')

app = Flask(__name__)
HTML_DIR = 'templates/html_files'  # Store the HTML MAPS


@app.route('/')
def index():
    """
    Display the list of available services.
    """
    services = {
        'Train and Evaluate': '/train',
        'Dataset Statistics': '/statistics/<dataset>',
        'Exploratory Data Analysis': '/eda/<dataset>',
        'Clean Images': '/clean_images',
        'Generate Synthetic Dataset': '/generate_synthetic',
        'Compare Execution': '/compare_execution',
        'Show HTML Files': '/show_html_files'
    }
    return render_template('index.html', services=services)


@app.route('/train', methods=['POST', 'GET'])
def train():
    if request.method == 'POST':
        dataset_name = request.form['dataset']
        model_name = request.form['model']
        tr_size = request.form['train_size']
        train_size = float(tr_size)
        ts_size = request.form['test_size']
        test_size = float(ts_size)

        result_name = dataset_name + "Tr" + tr_size + "Tst" + ts_size + ".png"
        accuracy, error = train_and_evaluate(dataset_name, model_name, train_size, test_size, result_name)

        img_url = '../static/' + result_name
        return render_template('result.html', accuracy=accuracy, error=error, img_url=img_url,
                               dataset=dataset_name, model=model_name, train_size=train_size, test_size=test_size)
    return render_template('train.html', datasets=DATASETS.keys(), models=MODELS.keys())


@app.route('/statistics/<dataset>', methods=['GET'])
def statistics(dataset):
    """
        Display statistics for a specified dataset.
        """
    if dataset is None or dataset not in DATASETS:
        error_message = "Error: A valid dataset is required to view statistics."
        return render_template('error.html', error_message=error_message)

    stats = get_dataset_statistics(dataset)
    return render_template('statistics.html', stats=stats.to_html(classes='table table-striped'))


@app.route('/eda/<dataset>', methods=['GET'])
def eda(dataset):
    """
    Perform exploratory data analysis for a specified dataset.
    """
    if dataset is None or dataset not in DATASETS:
        error_message = "Error: A valid dataset is required to perform EDA."
        return render_template('error.html', error_message=error_message)

    images = perform_eda(dataset)
    return render_template('eda.html', images=images)


@app.route('/clean_images', methods=['GET'])
def clean_images():
    """
    Clean the static directory by removing all PNG images.
    """

    files = glob.glob(os.path.join(main_path, 'static', '*.png'))
    for f in files:
        os.remove(f)
    return render_template('clean.html', num_files=len(files))


@app.route('/generate_synthetic', methods=['POST', 'GET'])
def generate_synthetic():
    """
    Generate a synthetic dataset and train models on it.
    """
    if request.method == 'POST':
        n_rows = int(request.form['n_rows'])
        n_cols = int(request.form['n_cols'])
        n_classes = int(request.form['n_classes'])
        train_size = float(request.form['train_size'])
        test_size = float(request.form['test_size'])
        model_name = request.form['model']

        start_time = time.time()

        accuracy, error, img_url = generate_synthetic_dataset(n_rows, n_cols, n_classes, model_name, train_size,
                                                              test_size)

        end_time = time.time()

        execution_time = end_time - start_time

        return render_template('synthetic_result.html', accuracy=accuracy, error=error,
                               execution_time=execution_time,
                               n_rows=n_rows, n_cols=n_cols, n_classes=n_classes, model=model_name,
                               train_size=train_size, test_size=test_size, img_url=img_url)
    return render_template('generate_synthetic.html', models=MODELS)


@app.route('/compare_execution', methods=['POST', 'GET'])
def compare_execution_route():
    """
    Compare execution times of sequential vs parallel processing.
    """
    sequential_time, parallel_time = compare_execution()
    return render_template('compare_execution_result.html', sequential_time=sequential_time,
                           parallel_time=parallel_time)


@app.route('/show_html_files', methods=['GET'])
def show_html_files():
    """
    List available HTML files for viewing.
    """
    files = glob.glob(os.path.join(main_path, HTML_DIR, '*.html'))

    print("Files")
    print(files)
    filenames = [os.path.basename(f) for f in files]
    return render_template('list_html_files.html', files=filenames)


@app.route('/view_html_file/<filename>', methods=['GET'])
def view_html_file(filename):
    """
    Display the selected HTML file.
    """
    return send_from_directory(HTML_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
