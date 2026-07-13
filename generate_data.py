import os
import csv
import random
from datetime import datetime, timedelta

# Create the data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# List of tuples: (product_name, price, seasonal_category)
PRODUCT_TEMPLATES = [
    # Grains, Flours & Rice
    ("Aashirvaad Atta Shudh Chakki 5kg", 260.00, "none"),
    ("Fortune Chakki Fresh Atta 10kg", 490.00, "none"),
    ("Pillsbury Chakki Fresh Atta 5kg", 255.00, "none"),
    ("Daawat Rozana Super Basmati Rice 5kg", 399.00, "none"),
    ("India Gate Feast Rozana Basmati Rice 5kg", 380.00, "none"),
    ("India Gate Basmati Rice Premium 1kg", 110.00, "none"),
    ("D-Mart Premia Kolam Rice 10kg", 650.00, "none"),
    ("D-Mart Premia Jeera Rice 1kg", 120.00, "none"),
    ("Fortune Sona Masoori Rice 5kg", 340.00, "none"),
    ("D-Mart Premia Maida 1kg", 45.00, "none"),
    ("D-Mart Premia Besan 1kg", 90.00, "none"),
    ("D-Mart Premia Rava (Suji) 1kg", 60.00, "none"),
    ("MTR Rava Idli Mix 500g", 110.00, "none"),
    ("MTR Dosa Mix 500g", 120.00, "none"),
    ("Gits Gulab Jamun Mix 200g", 115.00, "weekend"),
    ("Aashirvaad Rava Idli Mix 500g", 115.00, "none"),
    ("D-Mart Premia Thick Poha 1kg", 55.00, "none"),
    ("D-Mart Premia Sabudana 500g", 50.00, "none"),
    
    # Sugar, Salt & Staples
    ("Tata Salt Lite 1kg", 28.00, "none"),
    ("Tata Salt Rock Salt 1kg", 75.00, "none"),
    ("D-Mart Premia Sugar 1kg", 48.00, "none"),
    ("D-Mart Premia Sugar 5kg", 235.00, "none"),
    ("D-Mart Premia Jaggery Powder 1kg", 80.00, "none"),
    
    # Dals & Pulses
    ("D-Mart Premia Toor Dal 1kg", 170.00, "none"),
    ("D-Mart Premia Chana Dal 1kg", 95.00, "none"),
    ("D-Mart Premia Moong Dal Chilka 1kg", 130.00, "none"),
    ("D-Mart Premia Moong Dal Yellow 1kg", 145.00, "none"),
    ("D-Mart Premia Masoor Dal Lall 1kg", 110.00, "none"),
    ("D-Mart Premia Urad Dal White split 1kg", 150.00, "none"),
    ("D-Mart Premia Urad Dal Black whole 1kg", 140.00, "none"),
    ("D-Mart Premia Kabuli Chana 1kg", 160.00, "none"),
    ("D-Mart Premia Kala Chana 1kg", 85.00, "none"),
    ("D-Mart Premia Rajma Chitra 1kg", 155.00, "none"),
    ("D-Mart Premia Green Moong Whole 1kg", 125.00, "none"),
    ("D-Mart Premia Black Eyed Lobia 1kg", 115.00, "none"),
    ("D-Mart Premia Matki (Moth Beans) 1kg", 120.00, "none"),
    ("D-Mart Premia Masoor Whole 1kg", 105.00, "none"),
    ("D-Mart Premia Chawli (Black Eyed) 1kg", 110.00, "none"),
    
    # Oils & Ghee
    ("Amul Pure Cow Ghee 1L", 680.00, "none"),
    ("Gowardhan Cow Ghee 1L", 710.00, "none"),
    ("Fortune Mustard Oil 1L", 175.00, "none"),
    ("Fortune Sunflower Refined Oil 1L", 145.00, "none"),
    ("Fortune Kachi Ghani Mustard Oil 1L", 180.00, "none"),
    ("Fortune Rice Bran Health Oil 1L", 165.00, "none"),
    ("Saffola Gold Pro Healthy Oil 5L", 850.00, "none"),
    ("Saffola Active Oil 1L", 170.00, "none"),
    ("Dhara Groundnut Oil 1L", 195.00, "none"),
    ("Dhara Soyabean Refined Oil 1L", 135.00, "none"),
    ("Gemini Vanaspati Ghee 1L", 120.00, "none"),
    ("Parachute Pure Coconut Oil 500ml", 190.00, "none"),
    
    # Spices & Powder
    ("Everest Turmeric Powder 200g", 55.00, "none"),
    ("Everest Kashmiri Lalchili Powder 200g", 120.00, "none"),
    ("Everest Coriander Powder 200g", 65.00, "none"),
    ("Everest Garam Masala 100g", 85.00, "none"),
    ("Everest Tikhalal Chilli Powder 200g", 115.00, "none"),
    ("MDH Kitchen King Masala 100g", 88.00, "none"),
    ("MDH Chana Masala 100g", 78.00, "none"),
    ("MDH Pav Bhaji Masala 100g", 78.00, "none"),
    ("MDH Sambhar Masala 100g", 78.00, "none"),
    ("MDH Chunky Chat Masala 100g", 78.00, "none"),
    ("Catch Black Pepper Powder 100g", 75.00, "none"),
    ("Patanjali Bandhani Hing 25g", 45.00, "none"),
    ("D-Mart Premia Cumin Seeds (Jeera) 200g", 140.00, "none"),
    ("D-Mart Premia Mustard Seeds (Rai) 200g", 40.00, "none"),
    ("D-Mart Premia Fenugreek Seeds (Methi) 200g", 45.00, "none"),
    ("D-Mart Premia Fennel Seeds (Saunf) 200g", 70.00, "none"),
    ("D-Mart Premia Coriander Seeds (Dhana) 200g", 50.00, "none"),
    ("D-Mart Premia Sesame Seeds White (Til) 200g", 90.00, "none"),
    ("D-Mart Premia Ajwain 100g", 45.00, "none"),
    ("D-Mart Premia Green Cardamom (Elaichi) 50g", 180.00, "none"),
    ("D-Mart Premia Cloves (Laung) 50g", 95.00, "none"),
    ("D-Mart Premia Cinnamon Sticks (Dalchini) 100g", 85.00, "none"),
    ("D-Mart Premia Black Cardamom 50g", 110.00, "none"),
    ("D-Mart Premia Star Anise 50g", 80.00, "none"),
    
    # Dairy & Breakfast
    ("Amul Taaza Toned Milk 1L", 56.00, "none"),
    ("Amul Gold Full Cream Milk 1L", 66.00, "none"),
    ("Amul Masti Spiced Buttermilk 200ml", 20.00, "temp"),
    ("Amul Pure Butter 500g", 275.00, "none"),
    ("Mother Dairy Fresh Paneer 200g", 90.00, "none"),
    ("Mother Dairy Classic Dahi 400g", 50.00, "temp"),
    ("Amul Cheese Slices 200g", 145.00, "none"),
    ("Amul Cheese Block 200g", 135.00, "none"),
    ("Amul Cheese Spread Garlic 200g", 120.00, "none"),
    ("Britannia Brown Bread 400g", 50.00, "none"),
    ("Wibs White Bread 400g", 45.00, "none"),
    ("Kellogg's Corn Flakes Original 475g", 220.00, "none"),
    ("Quaker Instant Oats 1kg", 190.00, "none"),
    ("Saffola Masala Oats Classic 500g", 160.00, "none"),
    ("Bagrry's Fruit & Fibre Muesli 400g", 310.00, "none"),
    
    # Indian Snacks & Namkeen
    ("Haldiram's Alu Bhujia 400g", 110.00, "weekend"),
    ("Haldiram's Bhujia Sev 400g", 110.00, "weekend"),
    ("Haldiram's Moong Dal Namkeen 400g", 120.00, "weekend"),
    ("Haldiram's Panchrattan Mixture 400g", 130.00, "weekend"),
    ("Haldiram's Khatta Meetha Mixture 400g", 110.00, "weekend"),
    ("Haldiram's Cornflakes Mixture 400g", 120.00, "weekend"),
    ("Bikaji Bikaneri Bhujia 400g", 105.00, "weekend"),
    ("Balaji Wafers Simply Salted 100g", 40.00, "weekend"),
    ("Balaji Wafers Masala Masti 100g", 40.00, "weekend"),
    ("Kurkure Masala Munch 90g", 20.00, "none"),
    ("Kurkure Green Chutney Rajasthani 90g", 20.00, "none"),
    ("Lay's Classic Salted Potato Chips 90g", 20.00, "none"),
    ("Lay's India's Magic Masala Chips 90g", 20.00, "none"),
    ("Lay's American Style Onion Cream 90g", 20.00, "none"),
    ("Bingo Mad Angles Achari Masti 80g", 20.00, "none"),
    
    # Biscuits & Cookies
    ("Parle-G Gold Biscuits 250g", 20.00, "none"),
    ("Britannia Good Day Cashew Biscuits 200g", 35.00, "none"),
    ("Britannia Marie Gold Biscuits 250g", 30.00, "none"),
    ("Sunfeast Dark Fantasy Choco Fills 300g", 120.00, "weekend"),
    ("Oreo Vanilla Creme Biscuits 120g", 35.00, "none"),
    ("Britannia Bourbon Cream Biscuits 150g", 30.00, "none"),
    ("Britannia 50-50 Maska Chaska 120g", 30.00, "none"),
    ("Britannia NutriChoice Digestive 250g", 65.00, "none"),
    ("Parle Monaco Salted Biscuits 120g", 25.00, "none"),
    ("Parle Hide & Seek Chocolate Chips 120g", 50.00, "none"),
    
    # Sweets & Chocolates
    ("Haldiram's Gulab Jamun Tin 1kg", 240.00, "weekend"),
    ("Haldiram's Rasgulla Tin 1kg", 240.00, "weekend"),
    ("Haldiram's Soan Papdi 500g", 140.00, "weekend"),
    ("Cadbury Dairy Milk Silk Chocolate 150g", 175.00, "weekend"),
    ("Cadbury Dairy Milk Family Pack 100g", 100.00, "weekend"),
    ("KitKat 4-Finger Chocolate Bar", 40.00, "none"),
    ("5 Star Chocolate Bar 20g", 20.00, "none"),
    ("Snickers Peanut Chocolate Bar 50g", 50.00, "none"),
    ("Perk Chocolate Wafer Bar 15g", 10.00, "none"),
    ("Munch Chocolate Wafer Bar 15g", 10.00, "none"),
    
    # Tea, Coffee & Health Drinks
    ("Tata Tea Premium Leaf Tea 1kg", 420.00, "none"),
    ("Brooke Bond Red Label Tea 1kg", 460.00, "none"),
    ("Tata Tea Gold Leaf Tea 500g", 240.00, "none"),
    ("Brooke Bond Taj Mahal Tea 500g", 320.00, "none"),
    ("Wagh Bakri Premium Leaf Tea 1kg", 450.00, "none"),
    ("Nescafe Classic Instant Coffee 100g", 310.00, "none"),
    ("Bru Green Label Coffee 500g", 180.00, "none"),
    ("Bru Instant Coffee Jar 100g", 290.00, "none"),
    ("Bournvita Chocolate Nutrition Drink 1kg", 430.00, "none"),
    ("Horlicks Classic Malt Jar 1kg", 410.00, "none"),
    ("Boost Health Drink Refill 500g", 280.00, "none"),
    ("Complan Chocolate Health Drink 500g", 295.00, "none"),
    
    # Soft Drinks & Juices
    ("Coca Cola Soft Drink 2L", 95.00, "temp"),
    ("Thums Up Soft Drink 2L", 95.00, "temp"),
    ("Sprite Soft Drink 2L", 95.00, "temp"),
    ("Limca Lime Lemon Drink 2L", 95.00, "temp"),
    ("Fanta Orange Soft Drink 2L", 95.00, "temp"),
    ("Pepsi Soft Drink 2L", 90.00, "temp"),
    ("Frooti Mango Drink 1.2L", 75.00, "temp"),
    ("Maaza Mango Drink 1.2L", 75.00, "temp"),
    ("Real Fruit Power Mixed Fruit Juice 1L", 120.00, "temp"),
    ("Tropicana 100% Orange Juice 1L", 125.00, "temp"),
    ("Bisleri Mineral Water Bottle 1L", 20.00, "temp"),
    ("Kinley Water Bottle 1L", 20.00, "temp"),
    
    # Packaged Foods & Noodles
    ("Maggi 2-Minute Masala Noodles 12-Pack", 168.00, "none"),
    ("Yippee Magic Masala Noodles 6-Pack", 85.00, "none"),
    ("Ching's Secret Hakka Noodles 150g", 40.00, "none"),
    ("Ching's Dark Soy Sauce 200g", 55.00, "none"),
    ("Ching's Green Chilli Sauce 200g", 50.00, "none"),
    ("Ching's Schezwan Chutney 250g", 85.00, "none"),
    ("Kissan Fresh Tomato Ketchup 1kg", 150.00, "none"),
    ("Knorr Classic Tomato Soup 50g", 35.00, "none"),
    ("Knorr Sweet Corn Veg Soup 50g", 35.00, "none"),
    ("Kissan Mixed Fruit Jam 700g", 220.00, "none"),
    ("Amul Crunchy Peanut Butter 400g", 175.00, "none"),
    ("Dabur Apis Himalaya Honey 500g", 215.00, "none"),
    
    # Cleaning & Laundry Care
    ("Surf Excel Easy Wash Detergent 1kg", 140.00, "none"),
    ("Ariel Complete Front Load 1kg", 210.00, "none"),
    ("Tide Plus Double Power Jasmine 1kg", 110.00, "none"),
    ("Rin Laundry Detergent Bar (4-Pack)", 40.00, "none"),
    ("Vim Lemon Dishwash Liquid Gel 500ml", 115.00, "none"),
    ("Vim Dishwash Bar 300g", 30.00, "none"),
    ("Pril Lime Liquid Dishwash 425ml", 105.00, "none"),
    ("Exo Dishshine Bar 300g", 30.00, "none"),
    ("Lizol Floor Cleaner Citrus 1L", 215.00, "none"),
    ("Harpic Toilet Cleaner Original 1L", 195.00, "none"),
    ("Colin Glass & Surface Cleaner 500ml", 105.00, "none"),
    ("Comfort After Wash Fabric Conditioner 860ml", 235.00, "none"),
    ("Hit Flying Insect Killer Spray Red 400ml", 220.00, "none"),
    ("Dettol Antiseptic Liquid Bottle 500ml", 210.00, "none"),
    ("Godrej Aer Pocket Bathroom Air Fragrance", 60.00, "none"),
    ("Odonil Bathroom Air Freshener Hanger", 55.00, "none"),
    
    # Personal Care & Toiletries
    ("Dettol Liquid Handwash Original Refill 1.5L", 230.00, "none"),
    ("Dettol Bathing Soap (125g x 3)", 165.00, "none"),
    ("Lifebuoy Total 10 Soap (125g x 3)", 135.00, "none"),
    ("Dove Cream Beauty Bathing Bar (125g x 3)", 240.00, "none"),
    ("Lux Velvet Touch Soap (100g x 3)", 110.00, "none"),
    ("Pears Pure & Gentle Soap (125g x 3)", 225.00, "none"),
    ("Santoor Sandal & Turmeric Soap (125g x 3)", 140.00, "none"),
    ("Colgate Strong Teeth Toothpaste 300g", 155.00, "none"),
    ("Close-Up Red Hot Gel Toothpaste 300g", 160.00, "none"),
    ("Sensodyne Fresh Mint Sensitivity Toothpaste 100g", 150.00, "none"),
    ("Dabur Red Toothpaste 200g", 115.00, "none"),
    ("Colgate ZigZag Medium Toothbrush (Buy 2 Get 1)", 70.00, "none"),
    ("Clinic Plus Strong & Long Shampoo 650ml", 325.00, "none"),
    ("Head & Shoulders Anti-Dandruff Cool Menthol 650ml", 550.00, "none"),
    ("Dove Intense Repair Shampoo 650ml", 480.00, "none"),
    ("Pantene Hair Fall Control Shampoo 650ml", 450.00, "none"),
    ("Parachute Advansed Coconut Hair Oil 250ml", 105.00, "none"),
    ("Bajaj Almond Drops Hair Oil 200ml", 125.00, "none"),
    ("Dabur Amla Hair Oil 275ml", 115.00, "none"),
    ("Vaseline Intensive Care Cocoa Glow Body Lotion 400ml", 360.00, "none"),
    ("Nivea Soft Light Moisturising Cream 200ml", 290.00, "none"),
    ("Ponds Dreamflower Talcum Powder 400g", 295.00, "none"),
    ("Gillette Guard Safety Razor", 25.00, "none"),
    ("Gillette Guard Razor Blades (5-Pack)", 35.00, "none"),
    ("Dettol Lather Shaving Cream 70g", 65.00, "none"),
    
    # Puja Essentials
    ("Cycle Three In One Agarbatti (Incense) 100 Sticks", 70.00, "none"),
    ("Mangaldeep Sandalwood Agarbatti 80 Sticks", 60.00, "none"),
    ("D-Mart Premia Camphor (Kapur) Tablets 50g", 55.00, "none"),
    ("D-Mart Premia Puja Ghee Diya Wicks (100 pcs)", 80.00, "none"),
    ("Homelite Safety Matchbox (10-Pack bundle)", 20.00, "none"),
    
    # Dry Fruits
    ("D-Mart Premia Almonds (Badam) 500g", 450.00, "none"),
    ("D-Mart Premia Cashews (Kaju) 500g", 490.00, "none"),
    ("D-Mart Premia Raisins (Kishmish) 250g", 110.00, "none"),
    ("D-Mart Premia Pistachios (Pista) 250g", 310.00, "none"),
    ("D-Mart Premia Walnuts (Akhrot) 250g", 350.00, "none"),
    
    # Additional items to cross 200 (Total: 228)
    ("Cadbury Bournville Rich Cocoa Chocolate 80g", 90.00, "weekend"),
    ("Real Fruit Power Guava Juice 1L", 120.00, "temp"),
    ("Del Monte Sweet Corn Tin 400g", 95.00, "none"),
    ("Compact Umbrellas Indian Monsoon Edition", 299.00, "rainy"),
    ("Aashirvaad Mustard Seeds (Rai) 100g", 25.00, "none"),
    ("Tata Tea Agni Dust Tea 1kg", 280.00, "none"),
    ("Dabur Hajmola Anardana Tablets 120 tab", 55.00, "none"),
    ("Dabur Hajmola Regular Tablets 120 tab", 50.00, "none"),
    ("Everest Kasuri Methi 50g", 45.00, "none"),
    ("Vicco Vajradanti Toothpaste 200g", 140.00, "none"),
    ("Patanjali Dant Kanti Toothpaste 200g", 95.00, "none"),
    ("Paper Boat Aam Panna Drink 250ml", 35.00, "temp"),
    ("Paper Boat Anar Drink 250ml", 40.00, "temp"),
    ("Pass Pass Mouth Freshener 100g", 50.00, "none"),
    ("Dettol Cool Bathing Soap (125g x 3)", 170.00, "temp"),
    ("Amul Lassi Rose Flavour 200ml", 25.00, "temp"),
    ("MTR Vermicelli 500g", 55.00, "none"),
    ("Act II Popcorn Golden Sizzle 90g", 45.00, "weekend"),
    ("Kwality Walls Vanilla Tub 700ml", 140.00, "temp"),
    ("Amul Vanilla Gold Ice Cream 1L", 190.00, "temp"),
    ("Maggi Hot & Sweet Chilli Tomato Sauce 1kg", 170.00, "none"),
    ("Lipton Green Tea Honey Lemon 25 Bags", 155.00, "none"),
    ("Tata Salt SuperLite 1kg", 32.00, "none"),
    ("D-Mart Premia Premium Cashew W180 250g", 390.00, "none"),
    ("Aashirvaad Salt 1kg", 24.00, "none"),
    ("Patanjali Aloe Vera Gel 150ml", 110.00, "none")
]

# Set fixed seed for consistent generations
random.seed(42)

PRODUCTS = {}
for name, price, seasonal in PRODUCT_TEMPLATES:
    # Assign parameters dynamically
    # Essentials (Atta, Sugar, Salt, Milk, Poha, Water, Noodles) get slightly higher base sales
    is_essential = any(k in name.lower() for k in ["atta", "sugar", "salt", "milk", "poha", "water", "noodles", "bread"])
    if is_essential:
        base_daily_sales = random.choice([3, 4, 5])
    else:
        base_daily_sales = random.choice([1, 2])
        
    current_stock = random.choice([55, 70, 85, 90, 105, 120])
    reorder_level = random.choice([20, 25, 30])
    
    PRODUCTS[name] = {
        "base_daily_sales": base_daily_sales,
        "price": price,
        "current_stock": current_stock,
        "reorder_level": reorder_level,
        "seasonal": seasonal
    }

START_DATE = datetime.now() - timedelta(days=90)
END_DATE = datetime.now()

# Helper to simulate weather/temp
def get_weather_factors(date):
    random.seed(date.timetuple().tm_yday)
    is_rainy = random.random() < 0.15
    day_of_year = date.timetuple().tm_yday
    base_temp = 25 + 10 * random.random() - 5 * abs(day_of_year - 200) / 180
    return is_rainy, round(base_temp, 1)

def generate_transactions():
    transactions_file = os.path.join("data", "transactions.csv")
    current_date = START_DATE
    
    # We use a secondary seed to ensure consistent transactions
    random.seed(12345)
    
    with open(transactions_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "product_name", "quantity_sold", "unit_price", "is_rainy", "temperature"])
        
        while current_date <= END_DATE:
            is_rainy, temp = get_weather_factors(current_date)
            is_weekend = current_date.weekday() >= 5
            
            for prod_name, info in PRODUCTS.items():
                multiplier = 1.0
                
                if info["seasonal"] == "weekend" and is_weekend:
                    multiplier = 1.6 + random.random() * 0.4
                elif info["seasonal"] == "rainy" and is_rainy:
                    multiplier = 6.0 + random.random() * 3.0  # Big umbrella sales on rain days
                elif info["seasonal"] == "temp":
                    if temp > 28:
                        multiplier = 1.5 + (temp - 28) * 0.15
                    else:
                        multiplier = 0.8 + random.random() * 0.3
                
                noise = random.normalvariate(0, 0.15)
                daily_sales = max(0, int(info["base_daily_sales"] * multiplier * (1 + noise)))
                
                if daily_sales > 0:
                    num_transactions = max(1, int(daily_sales / random.choice([1, 2])))
                    remaining = daily_sales
                    
                    for i in range(num_transactions):
                        if remaining <= 0:
                            break
                        if i == num_transactions - 1:
                            qty = remaining
                        else:
                            qty = random.randint(1, max(1, int(remaining / 2)))
                        remaining -= qty
                        
                        hour = random.randint(8, 19)
                        minute = random.randint(0, 59)
                        second = random.randint(0, 59)
                        tx_time = current_date.replace(hour=hour, minute=minute, second=second)
                        
                        writer.writerow([
                            tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                            prod_name,
                            qty,
                            info["price"],
                            1 if is_rainy else 0,
                            temp
                        ])
            
            current_date += timedelta(days=1)
            
    print(f"Generated transaction history in {transactions_file}")

def generate_inventory():
    inventory_file = os.path.join("data", "inventory.csv")
    with open(inventory_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_name", "current_stock", "unit_price", "reorder_level"])
        
        for prod_name, info in PRODUCTS.items():
            writer.writerow([
                prod_name,
                info["current_stock"],
                info["price"],
                info["reorder_level"]
            ])
            
    print(f"Generated inventory records in {inventory_file}")

if __name__ == "__main__":
    generate_transactions()
    generate_inventory()
