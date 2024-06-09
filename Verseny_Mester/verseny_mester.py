from flask import Flask, render_template, request, redirect, url_for, session
import data
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
@app.route('/home')
def home():
    # Töröljük a szükséges session adatokat a kezdőoldal betöltésekor
    session.pop('chosen_sport', None)
    session.pop('formats', None)
    session.pop('chosen_format', None)
    session.pop('tournament_name', None)
    session.pop('names', None)
    session.pop('results', None)
    
    return render_template('choose_sport.html', title='Sportágak', sports=data.sports)

@app.route('/choosing_sport', methods=['POST'])
def choosing_sport():
    chosen_sport = request.form.get('sport')
    session['chosen_sport'] = chosen_sport
    
    if chosen_sport in ['Röplabda', 'Kézilabda', 'Kosárlabda', 'Labdarúgás']:
        session['formats'] = data.formats_team
    elif chosen_sport in ['Úszás', 'Atlétika']:
        session['formats'] = data.formats_individual
    
    return redirect(url_for('choose_format'))

@app.route('/choose_format')
def choose_format():
    formats = session.get('formats', [])
    chosen_sport = session.get('chosen_sport', '')
    return render_template('choose_format.html', title='Formátumok', formats=formats, chosen_sport=chosen_sport)

@app.route('/choosing_format', methods=['POST'])
def choosing_format():
    chosen_format = request.form.get('format')
    session['chosen_format'] = chosen_format
    return redirect(url_for('enter_tournament_name'))

@app.route('/enter_tournament_name', methods=['GET', 'POST'])
def enter_tournament_name():
    if request.method == 'POST':
        tournament_name = request.form.get('tournament_name')
        session['tournament_name'] = tournament_name
        return redirect(url_for('enter_name'))
    return render_template('enter_tournament_name.html', title='Verseny név megadása')

@app.route('/enter_name', methods=['GET', 'POST'])
def enter_name():
    if request.method == 'POST':
        name = request.form.get('name')
        if 'names' not in session:
            session['names'] = []
        names = session['names']
        names.append(name)
        session['names'] = names

    chosen_sport = session.get('chosen_sport', '')
    names = session.get('names', [])
    return render_template('enter_name.html', title='Név megadása', chosen_sport=chosen_sport, names=names)

@app.route('/review')
def review():
    chosen_sport = session.get('chosen_sport', '')
    chosen_format = session.get('chosen_format', '')
    tournament_name = session.get('tournament_name', '')
    names = session.get('names', [])
    return render_template('review.html', title='Áttekintés', chosen_sport=chosen_sport, chosen_format=chosen_format, tournament_name=tournament_name, names=names)

@app.route('/enter_results', methods=['GET', 'POST'])
def enter_results():
    chosen_format = session.get('chosen_format', '')

    if chosen_format == 'Egyenes kieséses':
        if request.method == 'POST':
            results = []
            for i in range(0, len(request.form) // 2):
                result_1 = request.form.get(f'results_{i}_1')
                result_2 = request.form.get(f'results_{i}_2')
                results.append((result_1, result_2))
            session['results'] = results
            return redirect(url_for('home'))
        
        names = session.get('names', [])
        random.shuffle(names)
        chosen_sport = session.get('chosen_sport', '')
        tournament_name = session.get('tournament_name', '')
        pairs = [(names[i], names[i + 1]) for i in range(0, len(names) - 1, 2)]
        if len(names) % 2 == 1:
            eronyero = names[-1]
        else:
            eronyero = None
        return render_template('enter_results.html', title='Eredmények felvétele', pairs=pairs, eronyero=eronyero, chosen_sport=chosen_sport, tournament_name=tournament_name)
    
    elif chosen_format == 'Időfutamos':
        if request.method == 'POST':
            results = []
            for i in range(len(request.form)):
                result = request.form.get(f'result_{i}')
                name = session['names'][i]
                results.append((name, result))
            results.sort(key=lambda x: float(x[1]))  # Idő alapján rendezés
            session['results'] = results
            return redirect(url_for('show_results'))

        names = session.get('names', [])
        chosen_sport = session.get('chosen_sport', '')
        tournament_name = session.get('tournament_name', '')
        return render_template('enter_results_time.html', title='Időfutamos eredmények felvétele', names=names, chosen_sport=chosen_sport, tournament_name=tournament_name)
    
    return redirect(url_for('home'))

@app.route('/show_results')
def show_results():
    results = session.get('results', [])
    results_with_rank = [(index + 1, result[0], result[1]) for index, result in enumerate(results)]
    return render_template('show_results.html', title='Eredmények', results=results_with_rank)




@app.route('/contact')
def contact():
    return render_template('contact.html', title='Kapcsolatok')


if __name__ == '__main__':
    app.run(debug=True)

