from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
from solver import solve_mpm

# Creating Data-Frames:
task_df = pd.DataFrame({'Task': ['Start', 'Finish'],
                        'Duration': [0, 0]})

connection_df = pd.DataFrame({'From': [],
                              'To': [],
                              'Type': [],
                              'Duration': []})

# Creating the Flask App with the routes
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def make_tasks():
    global task_df

    if request.method == 'POST':
        # Adding new row to the task_df data frame.
        if request.form['Submit'] == 'Submit':
            new_task = request.form['Task']
            new_duration = request.form['Duration']
            new_row = {'Task': new_task, 'Duration': float(new_duration)}
            task_df = task_df.append(new_row, ignore_index=True)


        # Or going to the connections page.
        elif request.form['Submit'] == 'Connections':
            return redirect(url_for('make_connections'))

        elif request.form['Submit'] == 'Delete':
            del_row = int(request.form['Del'])
            task_df = task_df.drop(del_row)

        elif request.form['Submit'] == 'Reset':
            return redirect(url_for('reset_data'))

    all_rows = task_df.index

    return render_template('tasks.html',
                           tasks=[task_df.to_html(classes='data', header="true")],
                           all_rows=all_rows)


@app.route('/connections', methods=['POST', 'GET'])
def make_connections():
    global task_df, connection_df
    if request.method == 'POST':
        # Adding new row to the connection_df data frame.
        if request.form['Submit'] == 'Submit':
            connection_from = request.form['ConnFrom']
            connection_to = request.form['ConnTo']
            connection_type = request.form['ConnType']
            connection_duration = request.form['ConnDuration']
            new_row = {'From': connection_from, 'To': connection_to,
                       'Type': connection_type, 'Duration': float(connection_duration)}
            connection_df = connection_df.append(new_row, ignore_index=True)

        # Or going to the results page.
        elif request.form['Submit'] == 'Calculate':
            return redirect(url_for('results'))

        elif request.form['Submit'] == 'Delete':
            del_row = int(request.form['Del'])
            connection_df = connection_df.drop(del_row)

        elif request.form['Submit'] == 'Reset':
            return redirect(url_for('reset_data'))

    all_rows = connection_df.index

    return render_template('connections.html',
                           all_tasks=task_df['Task'].values,
                           all_rows=all_rows,
                           tasks=[task_df.to_html(classes='data', header="true")],
                           conns=[connection_df.to_html(classes='data', header="true")]
                           )


@app.route('/results', methods=['POST', 'GET'])
def results():
    global task_df, connection_df

    if request.method == 'POST':
        if request.form['Submit'] == 'Reset':
            return redirect(url_for('reset_data'))

    if len(connection_df) > 0:
        tasks = []
        for index, rows in task_df.iterrows():
            row = (rows.Task, rows.Duration)
            tasks.append(row)

        dependencies = []
        for index, rows in connection_df.iterrows():
            row = (rows.From, rows.To, rows.Type, rows.Duration)
            dependencies.append(row)

        result_df = task_df.copy()


        result_df = solve_mpm(tasks, dependencies, result_df)


        return render_template('results.html',
                               tasks=[task_df.to_html(classes='data', header="true")],
                               conns=[connection_df.to_html(classes='data', header="true")],
                               results=[result_df.to_html(classes='data', header="true")])
    else:
        return ('Please define connections first.')


@app.route('/reset')
def reset_data():
    global task_df, connection_df
    task_df = pd.DataFrame({'Task': ['Start', 'Finish'],
                            'Duration': [0, 0]})

    connection_df = pd.DataFrame({'From': [],
                                  'To': [],
                                  'Type': [],
                                  'Duration': []})

    return redirect(url_for('make_tasks'))


if __name__ == '__main__':
    app.run()
