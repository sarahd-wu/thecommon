from flask import Flask, request, render_template, send_file
from backend import main
from utils import get_resource_path

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/download')
def download():
    final_path = get_resource_path("output.csv")
    return send_file(final_path, as_attachment=True)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        def parse_list(field):
            return [item.strip() for item in request.form.get(field, '').split(',') if item.strip()]
        
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        payload = {
            "name": request.form.get("name", ""),
            "classstart": request.form.get("classstart", ""),
            "classend": request.form.get("classend", ""),
            "major": parse_list("major"),
            "industrykeyword": request.form.get("industrykeyword", ""),
            "industrykeywordadv": parse_list("industrykeywordadv"),
            "addresscity": request.form.get("addresscity", ""),
            "addressstate": parse_list("addressstate"),
            "addresscountry": parse_list("addresscountry"),
            "deceased": 'deceased' in request.form,
            "employername": request.form.get("employername", ""),
            "employmenttitle": request.form.get("employmenttitle", ""),
            "employmentcity": request.form.get("employmentcity", ""),
            "employmentstate": parse_list("employmentstate"),
            "employmentcountry": parse_list("employmentcountry"),
            "industry": request.form.get("industry", ""),
            "secondaryschool": request.form.get("secondaryschool", ""),
            "higheredprogram": request.form.get("higheredprogram", ""),
            "higheredinstitution": request.form.get("higheredinstitution", ""),
            "degreetype": parse_list("degreetype"),
            "affinities": parse_list("affinities"),
            "interestgroups": parse_list("interestgroups"),
            "extracurricularactivities": request.form.get("extracurricularactivities", ""),
            "fraternities": parse_list("fraternities"),
            "athletics": parse_list("athletics"),
            "dormbuilding": parse_list("dormbuilding")
        }
        main(payload, username, password)  # updates output.csv
        return render_template('result.html')
    
    except Exception as e:
        print("Error occurred:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
