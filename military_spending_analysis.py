import requests
import pandas as pd
import matplotlib.pyplot as plt

# List of countries that directly border Russia
russian_border_countries = [
    "RUS",  # Russia itself
    "NOR",  # Norway
    "FIN",  # Finland
    "EST",  # Estonia
    "LVA",  # Latvia
    "LTU",  # Lithuania
    "BLR",  # Belarus
    "UKR",  # Ukraine
    "GEO",  # Georgia
    "AZE",  # Azerbaijan
    "KAZ",  # Kazakhstan
    "CHN",  # China
    "MNG",  # Mongolia
    "PRK",  # North Korea
]

# Create an empty list to store all data
military_funding_list = []

# Loop through each country
for country_code in russian_border_countries:
    # API URL for each country
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/MS.MIL.XPND.GD.ZS?format=json"
    
    # Make the request
    response = requests.get(url)
    data = response.json()
    
    # Check if data exists and has the expected structure
    if len(data) > 1 and data[1]:  # API returns a list, and relevant data is in data[1]
        for entry in data[1]:
            country = entry['country']['value']
            year = int(entry['date'])
            expenditure = entry['value']  # Might be None if missing

            # Only append data from 2010 onwards
            if year >= 2010:
                military_funding_list.append({"Country": country, "Year": year, "Expenditure": expenditure})

# Convert to Pandas DataFrame
df = pd.DataFrame(military_funding_list)

# Display the first few rows
print("\nFirst few rows of data:")
print(df.head())

# Get latest year data and top countries
latest_year = df["Year"].max()
df_latest = df[df["Year"] == latest_year]
top_countries = df_latest.sort_values(by="Expenditure", ascending=False).head(10)

print(f"\nTop countries by military expenditure in {latest_year}")
print(top_countries)

# Create a plot for multiple countries over time
plt.figure(figsize=(15, 8))

# Plot data for each country
for country in df["Country"].unique():
    country_data = df[df["Country"] == country]
    if country == "Ukraine":
        # Make Ukraine's line thicker, yellow, and on top
        plt.plot(country_data["Year"], country_data["Expenditure"], marker='o', 
                linestyle="-", label=country, color='yellow', linewidth=3, zorder=10)
    else:
        plt.plot(country_data["Year"], country_data["Expenditure"], marker="o", 
                linestyle="-", label=country, alpha=0.7)

# Add vertical lines for significant events
events = {
    2014: ('Crimea Invasion', 'red'),
    2015: ('Syria Intervention', 'orange'),
    2019: ('Zelensky Election', 'blue'),
    2020: ('Nagorno-Karabakh War', 'purple'),
    2021: ('Russian Buildup', 'brown'),
    2022: ('Ukraine Invasion', 'darkred')
}

# Add vertical lines and text for events
max_expenditure = df["Expenditure"].max()
for i, (year, (event_name, color)) in enumerate(events.items()):
    plt.axvline(x=year, color=color, linestyle='--', alpha=0.5, label=event_name)
    y_position = max_expenditure * (1 - i*0.05)  # Stagger text positions
    plt.text(year, y_position, f'{event_name}', rotation=90, verticalalignment='bottom')

# Customize the plot
plt.xlabel("Year")
plt.ylabel("Military Expenditure (% of GDP)")
plt.title("Military Expenditure Since 2010 - Russia and Border Countries")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.xlim(2010, latest_year)

plt.tight_layout()
plt.show()

# Function to calculate average expenditure changes around an event
def analyze_event_impact(df, event_year, event_name, window=2):
    print(f"\nImpact of {event_name} ({event_year}):")
    for country in df["Country"].unique():
        before = df[(df["Country"] == country) & 
                   (df["Year"] >= event_year - window) & 
                   (df["Year"] < event_year)]["Expenditure"].mean()
        after = df[(df["Country"] == country) & 
                  (df["Year"] > event_year) & 
                  (df["Year"] <= event_year + window)]["Expenditure"].mean()
        
        if pd.notna(before) and pd.notna(after):
            change = after - before
            print(f"\n{country}:")
            print(f"  {window} years before: {before:.2f}%")
            print(f"  {window} years after:  {after:.2f}%")
            print(f"  Change:           {change:+.2f}%")
            if abs(change) >= 0.5:  # Only show significant changes
                if change > 0:
                    print(f"  ⚠️ Significant increase after {event_name}")
                else:
                    print(f"  📉 Significant decrease after {event_name}")

# Analyze impact of each major event
for year, (event_name, _) in events.items():
    if year <= latest_year - 2:  # Only analyze events with enough subsequent data
        analyze_event_impact(df, year, event_name)

