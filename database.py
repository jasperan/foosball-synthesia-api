import yaml
import oracledb
# Import required library for making HTTP requests
import requests


with open('config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)

db_username = config_data['db_username']
db_password = config_data['db_password']
db_dsn = config_data['db_dsn']

# Initialize the Oracle Client library
oracledb.init_oracle_client()

class OracleDBInterface:
    def __init__(self, username, password, dsn):
        self.username = username
        self.password = password
        self.dsn = dsn
        self.connection = None

    def connect(self):
        try:
            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn,            )
            print("Successfully connected to foosball db")
        except oracledb.Error as error:
            print(f"Error connecting to foosball db: {error}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from foosball db")

    def execute_query(self, query):
        if not self.connection:
            print("Not connected to the db. Call connect() first.")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except oracledb.Error as error:
            print(f"Error executing query: {error}")
            return None

    def get_goals_per_team(self):
        query = """
        SELECT PLAYERDISPLAYNAME, count(PLAYER) "Number of Goals"
        FROM EXDEMO.CURRENT_GAME_VEGAS_GOALS_V
        GROUP BY PLAYERDISPLAYNAME
        """
        return self.execute_query(query)

    def get_possession_percentage(self):
        query = """
        SELECT GAMEINSTANCEID,
               (PLAYER1_POSSESSION_PCT + PLAYER2_POSSESSION_PCT)*100 "Total Possession Pct",
               PLAYER1_POSSESSION_PCT * 100 "Player1 Possession Pct",
               PLAYER2_POSSESSION_PCT * 100 "Player2 Possession Pct"
        FROM EXDEMO.OAC_CURRENT_GAME_STATS
        """
        return self.execute_query(query)

    def get_possession_total(self):
        query = """
        SELECT GAMEINSTANCEID,
               PLAYER1_MATCH_DURATION_SECONDS + PLAYER2_MATCH_DURATION_SECONDS "Possession total (in seconds)"
        FROM EXDEMO.OAC_CURRENT_GAME_STATS
        """
        return self.execute_query(query)

    def get_match_duration(self):
        query = """
        SELECT GAMEINSTANCEID,
               match_duration_seconds "Match duration (in seconds)"
        FROM EXDEMO.OAC_CURRENT_GAME_STATS
        """
        return self.execute_query(query)

    def get_number_of_players(self):
        query = """
        SELECT GAMEINSTANCEID,
               num_of_players
        FROM EXDEMO.OAC_CURRENT_GAME_STATS
        """
        return self.execute_query(query)

# Example usage
if __name__ == "__main__":
    
    db = OracleDBInterface(db_username, db_password, db_dsn)
    db.connect()

    # Example: Get goals per team
    goals_per_team = db.get_goals_per_team()
    print("Goals per team:", goals_per_team)
    # Get possession percentage
    possession_percentage = db.get_possession_percentage()
    print("Possession percentage:", possession_percentage)

    # Get possession total
    possession_total = db.get_possession_total()
    print("Possession total:", possession_total)

    # Get match duration
    match_duration = db.get_match_duration()
    print("Match duration:", match_duration)

    # Get number of players
    number_of_players = db.get_number_of_players()

    #print(goals_per_team, possession_percentage, possession_total, match_duration, number_of_players)


    # Prepare the data to be sent
    data = {
        "goals_per_team": str(goals_per_team),
        "possession_percentage": str(possession_percentage),
        "possession_total": str(possession_total),
        "match_duration": str(match_duration),
        "number_of_players": str(number_of_players)
    }

    #print(data)

    # Send GET request to localhost:3500
    try:
        response = requests.get('http://localhost:3500/generate', params=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Data sent successfully. Response:", response.text)
    except (requests.RequestException, Exception) as e:
        print("Error sending data to OCI GenAI service:", e)

    db.disconnect()