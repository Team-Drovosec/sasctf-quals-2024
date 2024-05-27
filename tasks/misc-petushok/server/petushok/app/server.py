import os
import base64
import helper
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    logo = request.args.get('logo')
    if logo == None:
        return redirect('/?logo=petushok')

    safe_dir = os.getcwd() + os.sep

    if os.path.splitext(logo)[1]:
        files = [logo]
    else:
        files = [name for name in os.listdir(safe_dir) if os.path.splitext(name)[0] == logo]

    if files and os.path.isfile(files[0]) and os.path.commonprefix((os.path.realpath(files[0]), safe_dir)) == safe_dir:
        with open(files[0],"rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        debug_data = 'success'
    else:
        logo_data = ''
        debug_data = "list of available files:\n" + "\n".join(os.listdir(safe_dir))

    secret = request.args.get('secret', type=int, default=0)
    logo_desc = os.environ["CTF_FLAG"] if helper.check_secret(secret) else "Co-Co-Co"
    
    return render_template('index.html',
        logo_data = logo_data,
        logo_desc = logo_desc,
        debug_data = debug_data )

@app.route('/debug')
def debug():
    test = 2
    test *= 2
    assert test == 4
    test //= 2
    assert test == 2
    test += 2
    assert test == 4
    test -= 2
    assert test == 2
    test ^= 2
    assert test == 0
    test |= 2
    assert test == 2
    test &= 2
    assert test == 2
    return "<p>SUCCESS</p>"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
