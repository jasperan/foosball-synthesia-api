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
        SELECT PLAYERDISPLAYNAME, count(PLAYER) "goals"
        FROM EXDEMO.CURRENT_GAME_VEGAS_GOALS_V
        GROUP BY PLAYERDISPLAYNAME
        """
        return self.execute_query(query)

    def get_possession_percentage(self):
        query = """
        SELECT GAMEINSTANCEID,
               (PLAYER1_POSSESSION_PCT + PLAYER2_POSSESSION_PCT)*100 "Total Possession Pct",
               PLAYER1_POSSESSION_PCT * 100 "team1",
               PLAYER2_POSSESSION_PCT * 100 "team2"
        FROM EXDEMO.OAC_CURRENT_GAME_STATS
        """
        return self.execute_query(query)

    def get_possession_total(self):
        query = """
        SELECT GAMEINSTANCEID,
               PLAYER1_MATCH_DURATION_SECONDS + PLAYER2_MATCH_DURATION_SECONDS "possession_total"
        FROM EXDEMO.OAC_CURRENT_GAME_STATS
        """
        return self.execute_query(query)

    def get_match_duration(self):
        query = """
        SELECT GAMEINSTANCEID,
               match_duration_seconds "match_duration"
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

    def get_progressive_goals_per_team(self):
        query = """
        SELECT
            TRIM(GAMEDATATIMESTAMP) AS "GAMEDATATIMESTAMP",
            PLAYERDISPLAYNAME,
            count(PLAYER) "Total Goals Per Team"
        FROM EXDEMO.PROGRESSIVE_GAME_GOALS_VIEW
        where GAMEEVENTTYPEID = 63
        and TRIM(GAMEDATATIMESTAMP) = (select max(trim(GAMEDATATIMESTAMP)) from  EXDEMO.CURRENT_GAME_VEGAS_GOALS_V)
        group by PLAYERDISPLAYNAME, TRIM(GAMEDATATIMESTAMP)
        order by PLAYERDISPLAYNAME
        """
        return self.execute_query(query)

    def get_progressive_possession_percentage(self):
        query = """
        SELECT
            TRIM(GAMEDATATIMESTAMP) AS "GAMEDATATIMESTAMP",
            ROUND(AVG(PLAYER1_POSSESSION_PCT),2) AS PLAYER1_POSSESSION_PCT,
            ROUND(AVG(PLAYER2_POSSESSION_PCT),2) AS PLAYER2_POSSESSION_PCT
        FROM
            EXDEMO.OAC_PROGRESSIVE_GAME_STATS
        GROUP BY TRIM(GAMEDATATIMESTAMP)
        ORDER BY TRIM(GAMEDATATIMESTAMP)
        """
        return self.execute_query(query)

    def get_progressive_possession_total(self):
        query = """
        SELECT
            TRIM(GAMEDATATIMESTAMP) AS "GAMEDATATIMESTAMP",
            sum(PLAYER1_MATCH_DURATION_SECONDS) "Total Cummulate Possession by Player1 (in seconds)",
            ROUND(AVG(PLAYER1_MATCH_DURATION_SECONDS),2) "Average Possession by Player1 (in seconds)", 
            sum(PLAYER2_MATCH_DURATION_SECONDS) "Total Cummulate Possession by Player2 (in seconds)",
            ROUND(AVG(PLAYER2_MATCH_DURATION_SECONDS),2) "Average Possession by Player2 (in seconds)"
        FROM
            EXDEMO.OAC_PROGRESSIVE_GAME_STATS
        GROUP BY TRIM(GAMEDATATIMESTAMP)
        ORDER BY TRIM(GAMEDATATIMESTAMP)
        """
        return self.execute_query(query)

    def get_progressive_match_duration(self):
        query = """
        SELECT
            TRIM(GAMEDATATIMESTAMP) AS "GAMEDATATIMESTAMP",
            sum(match_duration_seconds) "Total Cummulative Match Time (in seconds)"
        FROM
            EXDEMO.OAC_PROGRESSIVE_GAME_STATS
        GROUP BY TRIM(GAMEDATATIMESTAMP)
        ORDER BY TRIM(GAMEDATATIMESTAMP)
        """
        return self.execute_query(query)

    def get_progressive_number_of_players_and_games_played(self):
        query = """
        SELECT
            TRIM(GAMEDATATIMESTAMP) AS "GAMEDATATIMESTAMP",
            sum(num_of_players) "Total Number of Players",
            sum(num_of_players)/2 "Total Number of Games" 
        FROM
            EXDEMO.OAC_PROGRESSIVE_GAME_STATS
        GROUP BY TRIM(GAMEDATATIMESTAMP)
        ORDER BY TRIM(GAMEDATATIMESTAMP)
        """
        return self.execute_query(query)




def main(game_instance_id, request_type):
    
    db = OracleDBInterface(db_username, db_password, db_dsn)
    db.connect()

    if request_type == 'match':
        # Example: Get goals per team
        (goals_per_team, possession_percentage, match_duration, number_of_players) = (str(), str(), str(), str())
        try:
            goals = db.get_goals_per_team()
            print("Goals per team:", goals)

            if len(goals) > 1:
                goals_per_team = 'Team {}: {}, Team {}: {}'.format(goals[0].get('PLAYERDISPLAYNAME'), goals[0].get('goals'),
                    goals[1].get('PLAYERDISPLAYNAME'), goals[1].get('goals'),
                )
            elif len(goals) == 1: # if only one team scored.
                goals_per_team = 'Team {}: {}, rival team: 0'.format(goals[0].get('PLAYERDISPLAYNAME'), goals[0].get('goals')
                )                                 
        except Exception as e:
            print("Exception in get_goals_per_team:", str(e))

        try:
            possession_percentage = db.get_possession_percentage()
            #print(possession_percentage)
            # Get possession percentage
            possession_percentage = 'Team 1: {} percent, Team 2: {} percent'.format(possession_percentage[0].get('team1'),
                possession_percentage[0].get('team2')
            )            
            print("Possession percentage:", possession_percentage)
        except Exception as e:
            print("Exception in get_possession_percentage:", str(e))

        # Get possession total
        #possession_total = db.get_possession_total()
        #print("Possession total:", possession_total)

        try:
            # Get match duration
            match_duration = db.get_match_duration()
            #print(match_duration)
            match_duration = match_duration[0].get('match_duration')
            print("Match duration:", match_duration)
        except Exception as e:
            print("Exception in get_match_duration:", str(e))

        try:
            # Get number of players
            number_of_players = db.get_number_of_players()
            #print(number_of_players)
            number_of_players = number_of_players[0]['NUM_OF_PLAYERS']
        except Exception as e:
            print("Exception in get_number_of_players:", str(e))

        #print(goals_per_team, possession_percentage, possession_total, match_duration, number_of_players_and_games_played)


        # Prepare the data to be sent
        data = {
            "goals_per_team": str(goals_per_team),
            "possession_percentage": str(possession_percentage),
            #"possession_total": str(possession_total),
            "match_duration": str(match_duration),
            "number_of_players": str(number_of_players),
            "game_instance_id": game_instance_id,
            "request_type": request_type,

        }

        print(data)

    elif request_type == 'progressive':
        progressive_goals_per_team = db.get_progressive_goals_per_team()
        print("Goals per team:", progressive_goals_per_team)

        # Get possession percentage
        progressive_possession_percentage = db.get_progressive_possession_percentage()
        print("Possession percentage:", progressive_possession_percentage)

        # Get possession total
        progressive_possession_total = db.get_progressive_possession_total()
        print("Possession total:", progressive_possession_total)

        # Get match duration
        progressive_match_duration = db.get_progressive_match_duration()
        print("Match duration:", progressive_match_duration)


        # Get number of players and games played
        number_of_players_and_games_played = db.get_progressive_number_of_players_and_games_played()


        data = {
            "goals_per_team": str(progressive_goals_per_team),
            "possession_percentage": str(progressive_possession_percentage),
            "possession_total": str(progressive_possession_total),
            "match_duration": str(progressive_match_duration),
            "number_of_players_and_games_played": str(number_of_players_and_games_played),
            "game_instance_id": game_instance_id,
            "request_type": request_type,
        }

    # Send GET request to localhost:3500/generate
    try:
        response = requests.get('http://localhost:3500/generate', params=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Data sent successfully. Response:", response.text)
    except (requests.RequestException, Exception) as e:
        print("Error sending data to OCI GenAI service:", e)

    db.disconnect()

    return 1


# Example usage
if __name__ == "__main__":
    main()
