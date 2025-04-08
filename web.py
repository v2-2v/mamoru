from flask import Flask, request

app = Flask(__name__)

@app.route('/user', methods=['GET'])
def get_user():
    user_id = request.args.get('id')
    user_name = request.args.get('name')
    
    if user_id and user_name:
        return f"User ID: {user_id}, Name: {user_name}"
    else:
        return "Missing 'id' or 'name' parameter", 400

if __name__ == '__main__':
    app.run(debug=True,port=800)
