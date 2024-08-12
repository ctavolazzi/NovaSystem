import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('solar_business.db')
cursor = conn.cursor()

# Updated test queries
test_queries = [
    ("How many customers bought batteries in the last year?",
     """
     SELECT COUNT(DISTINCT customer_id) 
     FROM purchases 
     WHERE product_type = 'Battery' 
     AND purchase_date >= date('2023-07-01', '-1 year')
     """),
    
    ("How many customers do we have who are still waiting on installation?",
     """
     SELECT COUNT(*) 
     FROM installations 
     WHERE completed_date IS NULL
     """),
    
    ("Which customers could we target for an ad campaign to upgrade their solar?",
     """
     SELECT c.customer_id, c.name, c.email, p.purchase_date
     FROM customers c
     JOIN purchases p ON c.customer_id = p.customer_id
     WHERE p.product_type = 'Solar Panel System'
     AND p.purchase_date <= date('2023-07-01', '-2 year')
     AND c.customer_id NOT IN (
         SELECT customer_id 
         FROM purchases 
         WHERE product_type = 'Battery'
     )
     """)
]

print("Running updated test queries:")
for description, query in test_queries:
    print(f"\n{description}")
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(row)

# Close the connection
conn.close()