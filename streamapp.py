import streamlit as st
import pandas as pd
import mariadb

# ---------------- DB CONNECTION ----------------
def get_connection():
    return mariadb.connect(
        user="root",  #login using your own pc root id
        password="password", #use your database password which you use on your pc
        host="localhost",
        port=3306,
        database="food_donation_db"
    )

# ---------------- QUERY DEFINITIONS ----------------
queries = {
    "Q1️⃣ Total number of food listings": "SELECT COUNT(*) AS total_listings FROM food_listings_data;",

    "Q2️⃣ Number of active listings by city":
        """SELECT p.City, COUNT(f.Food_ID) AS Active_Listings
            FROM food_listings_data f
            JOIN providers_data p ON f.Provider_ID = p.Provider_ID
            WHERE f.Expiry_Date >= DATE('now')   -- filtering active (not expired) food
            GROUP BY p.City
            ORDER BY Active_Listings ASC;""",

    "Q3️⃣ Top 5 food types listed most frequently":
    """SELECT Food_Type, COUNT(*) AS Listing_Count
            FROM food_listings_data
            GROUP BY Food_Type
            ORDER BY Listing_Count DESC
            LIMIT 5;""",

    "Q4️⃣ Count of listings expiring today":
    """SELECT COUNT(*) AS Expiring_Today
            FROM food_listings_data
            WHERE DATE(Expiry_Date) = CURDATE();""",

    "Q5️⃣ Provider-wise listing count":
    """SELECT p.Name AS Provider_Name,
       COUNT(f.Food_ID) AS Listing_Count
        FROM providers_data p
        JOIN food_listings_data f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Listing_Count ASC;""",

    "Q6️⃣ City-wise distribution of providers":
    """SELECT City, COUNT(*)
            FROM providers_data
            GROUP BY City;""",

    "Q7️⃣ Receiver capacity by city":
    """SELECT
            City,
            Type,
            COUNT(*) AS total_receivers
            FROM receivers_data
            GROUP BY City, Type
            ORDER BY City, total_receivers DESC;""",

    "Q8️⃣ Match listings with receivers": """
        SELECT
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
            ON f.Location = r.City;;
    """,

    "Q9️⃣ Total quantity of surplus food available by city":
    """SELECT p.City, SUM(f.Quantity) AS total_quantity
            FROM food_listings_data f
            JOIN providers_data p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.City;""",

    "Q🔟 Meal type distribution":
    """SELECT Meal_Type, COUNT(*)
            FROM food_listings_data
            GROUP BY Meal_Type""",

    "Q1️⃣1️⃣ List of expired food listings":
    """SELECT *
            FROM food_listings_data
            WHERE COALESCE(
                STR_TO_DATE(Expiry_Date, '%Y-%m-%d'),
                STR_TO_DATE(Expiry_Date, '%d-%m-%Y'),
                STR_TO_DATE(Expiry_Date, '%d/%m/%Y'),
                STR_TO_DATE(Expiry_Date, '%m/%d/%Y')
            ) < CURDATE();""",

    "Q1️⃣2️⃣ Listings per provider type":
    """SELECT p.Type AS Provider_Type,
        COUNT(*) AS Total_Listings
        FROM food_listings_data f
        JOIN providers_data p
        ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Type;""",

    "Q1️⃣3️⃣ Average quantity per food type":
    """SELECT Food_Type, AVG(Quantity) AS avg_quantity
            FROM food_listings_data
            GROUP BY Food_Type;""",

    "Q1️⃣4️⃣ Number of providers & receivers in each city": """
        SELECT p.City AS City,
       COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
       COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
        FROM providers_data p
        LEFT JOIN receivers_data r ON p.City = r.City
        GROUP BY p.City;
    """,

    "Q1️⃣5️⃣ Providers with active listings & contacts": """
        SELECT p.Provider_ID,
       p.Name AS Provider_Name,
       p.Contact,
       SUM(f.Quantity) AS Total_Quantity
        FROM providers_data p
        JOIN food_listings_data f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Provider_ID, p.Name, p.Contact
        ORDER BY Total_Quantity DESC
        LIMIT 5;
    """
}

# ---------------- APP LAYOUT ----------------
st.set_page_config(page_title="🍽️ Local Food Wastage Dashboard", layout="wide")
st.title("🍽️ Local Food Wastage Management Dashboard")
st.markdown("Use the filters below and select queries from the dropdown to analyze surplus food distribution and coordination. 🔍")

# ---------------- FILTERS ----------------
st.sidebar.header("🔽 Apply Filters")
city_filter = st.sidebar.text_input("🏙️ City")
provider_filter = st.sidebar.text_input("👨‍🍳 Provider_Name")
food_filter = st.sidebar.text_input("🍛 Food Type")
meal_filter = st.sidebar.text_input("🍽️ Meal Type")

# ---------------- QUERY DROPDOWN ----------------
query_choice = st.selectbox("📊 Select a Query to Run:", list(queries.keys()))

# ---------------- EXECUTE SELECTED QUERY ----------------
if st.button("▶️ Run Query"):
    query = queries[query_choice]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    # Get column names & data
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=columns)

    # ✅ Apply Filters (if provided)
    if city_filter:
        df = df[df["City"].astype(str).str.contains(city_filter, case=False, na=False)]
    if provider_filter and "Provider_Name" in df.columns:
        df = df[df["Provider_Name"].astype(str).str.contains(provider_filter, case=False, na=False)]
    if food_filter and "Food_Type" in df.columns:
        df = df[df["Food_Type"].astype(str).str.contains(food_filter, case=False, na=False)]
    if meal_filter and "Meal_Type" in df.columns:
        df = df[df["Meal_Type"].astype(str).str.contains(meal_filter, case=False, na=False)]

    # ✅ Show results
    st.subheader(f"📌 Results for: {query_choice}")
    # ✅ Increase font size and row height
    st.dataframe(
        df.style.set_properties(**{
            'font-size': '20pt',   # 🔥 Bigger font
            'text-align': 'left'   # 👈 Align text left
        }),
        use_container_width=True,
        height=600   # 🔥 increase vertical space
    )

    # ✅ Special case: Provider Contacts Query
    if query_choice == "Q1️⃣5️⃣ Providers with active listings & contacts":
        st.markdown("📞 **Provider Contact Details for Coordination:**")
        for _, row in df.iterrows():
            st.markdown(f"- 🏢 **{row['Name']}** ({row['City']}) → 📱 {row['Contact']}")
