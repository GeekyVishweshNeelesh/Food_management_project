import mariadb
import sys

# --- CONNECT TO DATABASE ---
def get_connection():
    try:
        conn = mariadb.connect(
            user="vishwesh",       # change with your DB username
            password="password",  # change with your DB password
            host="localhost",
            port=3306,
            database="food_donation_db"
        )
        return conn
    except mariadb.Error as e:
        print(f"❌ Error connecting to MariaDB: {e}")
        sys.exit(1)

# --- QUERIES DICTIONARY ---
queries = {
    1: ("SELECT COUNT(*) FROM food_listings_data;",
        "📦 Total number of food listings"),

    2: ("""SELECT p.City, COUNT(f.Food_ID) AS Active_Listings
            FROM food_listings_data f
            JOIN providers_data p ON f.Provider_ID = p.Provider_ID
            WHERE f.Expiry_Date >= DATE('now')   -- filtering active (not expired) food
            GROUP BY p.City
            ORDER BY Active_Listings DESC""",
        "🌆 Number of active listings by city"),

    3: ("""SELECT Food_Type, COUNT(*) AS Listing_Count
            FROM food_listings_data
            GROUP BY Food_Type
            ORDER BY Listing_Count DESC
            LIMIT 5;""",
        "🍲 Top 5 most frequently listed food types"),

    4: ("""SELECT COUNT(*) AS Expiring_Today
            FROM food_listings_data
            WHERE DATE(Expiry_Date) = CURDATE();""",
        "⏰ Listings expiring today"),

    5: ("""SELECT p.Name AS Provider_Name,
       COUNT(f.Food_ID) AS Listing_Count
        FROM providers_data p
        JOIN food_listings_data f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Listing_Count ASC;
        """,
        "👨‍🍳 Provider-wise listing count"),

    6: ("""SELECT City, COUNT(*)
            FROM providers_data
            GROUP BY City;""",
        "🏙️ City-wise distribution of providers"),

    7: ("""SELECT
            City,
            Type,
            COUNT(*) AS total_receivers
            FROM receivers_data
            GROUP BY City, Type
            ORDER BY City, total_receivers DESC;""",
        "🛠️ Receiver capacity by city"),

    8: ("""SELECT
            f.Food_ID,
            f.Food_Name,
            f.Food_Type,
            f.Meal_Type,
            f.Quantity,
            f.Location,
            r.Receiver_ID,
            r.Name AS Receiver_Name,
            r.Type AS Receiver_Type,
            r.City AS Receiver_City,
            r.Contact AS Receiver_Contact
        FROM food_listings_data f
        JOIN receivers_data r
            ON f.Location = r.City;""",
        "🤝 Match listings with receivers (food type & city)"),

    9: ("""SELECT p.City, SUM(f.Quantity) AS total_quantity
            FROM food_listings_data f
            JOIN providers_data p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.City;""",
        "📊 Total quantity of surplus food by city"),

    10: ("""SELECT Meal_Type, COUNT(*)
            FROM food_listings_data
            GROUP BY Meal_Type;""",
         "🍴 Meal type distribution"),

    11: ("""SELECT *
            FROM food_listings_data
            WHERE COALESCE(
                STR_TO_DATE(Expiry_Date, '%Y-%m-%d'),
                STR_TO_DATE(Expiry_Date, '%d-%m-%Y'),
                STR_TO_DATE(Expiry_Date, '%d/%m/%Y'),
                STR_TO_DATE(Expiry_Date, '%m/%d/%Y')
            ) < CURDATE();""",
         "⚠️ Expired food listings"),

    12: ("""SELECT p.Type AS Provider_Type,
        COUNT(*) AS Total_Listings
        FROM food_listings_data f
        JOIN providers_data p
        ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Type;""",
         "🏪 Listings per provider type"),

    13: ("""SELECT Food_Type, AVG(Quantity) AS avg_quantity
            FROM food_listings_data
            GROUP BY Food_Type;""",
         "📐 Average quantity per food type"),

    14: ("""SELECT p.City AS City,
       COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
       COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
        FROM providers_data p
        LEFT JOIN receivers_data r ON p.City = r.City
        GROUP BY p.City;""",
         "📍 Providers & Receivers per city"),

    15: ("""SELECT p.Provider_ID,
       p.Name AS Provider_Name,
       p.Contact,
       SUM(f.Quantity) AS Total_Quantity
        FROM providers_data p
        JOIN food_listings_data f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Provider_ID, p.Name, p.Contact
        ORDER BY Total_Quantity DESC
        LIMIT 5;


        """,
         "📞 Q15: Show the Top 5 Food Providers 🍴 who have contributed the highest total quantity of surplus food 📦, along with their contact details.")
}

# --- RUN SINGLE QUERY ---
def run_query(cursor, query_num):
    if query_num not in queries:
        print("❌ Invalid query number! Please choose between 1 and 15.")
        return

    query, desc = queries[query_num]
    cursor.execute(query)
    results = cursor.fetchall()

    print(f"\n🔎 {desc}")
    for row in results:
        print("➡️", row)

# --- MAIN ---
if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        print("\n✨ Food Donation Query Menu ✨")
        print("Choose a query number (1-15) or 0 to exit 🚪")

        try:
            choice = int(input("👉 Enter query number: "))
        except ValueError:
            print("❌ Please enter a valid number!")
            continue

        if choice == 0:
            print("👋 Exiting... Goodbye!")
            break

        run_query(cursor, choice)

    cursor.close()
    conn.close()
