from flask import Flask, request, jsonify
import database

app = Flask(__name__)

progressive_requests = 0

@app.route('/game_end', methods=['POST'])
def game_end():
    try:
        global progressive_requests
        # Extract game_instance from the request data
        data = request.json

        print(data)

        game_instance = data.get('gameinstanceid')
        game_timestamp = data.get('gamedatatimestamp')

        print('[{}] Game Instance ID obtained from /game_end request: {}'.format(game_timestamp, game_instance))
        
        if game_instance is None or not isinstance(game_instance, int):
            return jsonify({"error": "Invalid or missing game_instance"}), 400
        
        # Call the main function from database.py
        database.main(game_instance, 'match') # always call with match type, only once every 4 times for progressive.

        #if progressive_requests > 3:
        #    progressive_requests = 0
        #    database.main(game_instance, 'progressive')
        
        progressive_requests += 1  
      
        return jsonify({"message": "Game end processed successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3502)
