from flask import Flask, render_template, request
from graph import build_graph_from_log_matrix
from reding_from_file import get_log_matrix_from_file

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def show_image():
    file_name = request.form['file_name']
    file_path = "./resources/"+file_name

    log_matrix = get_log_matrix_from_file(file_path)
    build_graph_from_log_matrix(log_matrix)

    #print(file_path)
    return render_template('index.html', file_name='simple_process_model.png')

if __name__ == "__main__":
    app.run()