from flask import Flask, request, jsonify
import database

app = Flask(__name__)

@app.route('/game_end', methods=['POST'])
def game_end():
    try:
        # Call the main function from database.py
        database.main()
        return jsonify({"message": "Game end processed successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3502)
