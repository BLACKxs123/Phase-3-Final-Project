import psycopg2

# Database connection setup
def connect():
    return psycopg2.connect(
        host="localhost",
        database="address_management",
        user="fonte",
        password="QWERTY"  
    )

# Create an address
def add_address(street_address, city, state, postal_code, country, group_name):
    conn = connect()
    cur = conn.cursor()
    
    # Get the group ID
    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
    result = cur.fetchone()
    if result:
        group_id = result[0]
    else:
        print(f"Group '{group_name}' does not exist. Adding it now.")
        group_id = add_group(group_name)
    
    # Insert the address
    cur.execute("""
        INSERT INTO addresses (street_address, city, state, postal_code, country, group_id)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (street_address, city, state, postal_code, country, group_id))
    conn.commit()
    print(f"Address at {street_address} added successfully.")
    cur.close()
    conn.close()

# Add a new group
def add_group(name):
    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (name,))
        group_id = cur.fetchone()[0]
        conn.commit()
        print(f"Group '{name}' added with ID {group_id}.")
    except psycopg2.IntegrityError:
        conn.rollback()
        print(f"Group '{name}' already exists.")
        cur.execute("SELECT id FROM groups WHERE name = %s;", (name,))
        group_id = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
    return group_id

# Read all addresses
def list_addresses():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.street_address, a.city, a.state, a.postal_code, a.country, g.name as group_name
        FROM addresses a
        LEFT JOIN groups g ON a.group_id = g.id;
    """)
    rows = cur.fetchall()
    print("Addresses:")
    for row in rows:
        print(f"ID: {row[0]}, Address: {row[1]}, {row[2]}, {row[3]} - {row[4]}, {row[5]}, Group: {row[6]}")
    cur.close()
    conn.close()

# Update an address
def update_address(address_id, street_address=None, city=None, state=None, postal_code=None, country=None, group_name=None):
    conn = connect()
    cur = conn.cursor()
    
    # Update fields
    if street_address:
        cur.execute("UPDATE addresses SET street_address = %s WHERE id = %s", (street_address, address_id))
    if city:
        cur.execute("UPDATE addresses SET city = %s WHERE id = %s", (city, address_id))
    if state:
        cur.execute("UPDATE addresses SET state = %s WHERE id = %s", (state, address_id))
    if postal_code:
        cur.execute("UPDATE addresses SET postal_code = %s WHERE id = %s", (postal_code, address_id))
    if country:
        cur.execute("UPDATE addresses SET country = %s WHERE id = %s", (country, address_id))
    if group_name:
        # Get the group ID
        cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
        result = cur.fetchone()
        if result:
            group_id = result[0]
        else:
            print(f"Group '{group_name}' does not exist. Adding it now.")
            group_id = add_group(group_name)
        cur.execute("UPDATE addresses SET group_id = %s WHERE id = %s", (group_id, address_id))
    
    conn.commit()
    print(f"Address {address_id} updated successfully.")
    cur.close()
    conn.close()

# Delete an address
def delete_address(address_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM addresses WHERE id = %s", (address_id,))
    conn.commit()
    print(f"Address {address_id} deleted successfully.")
    cur.close()
    conn.close()

# Search addresses by group
def search_addresses_by_group(group_name):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.street_address, a.city, a.state, a.postal_code, a.country
        FROM addresses a
        LEFT JOIN groups g ON a.group_id = g.id
        WHERE g.name = %s;
    """, (group_name,))
    rows = cur.fetchall()
    print(f"Addresses in group '{group_name}':")
    for row in rows:
        print(f"ID: {row[0]}, Address: {row[1]}, {row[2]}, {row[3]} - {row[4]}, {row[5]}")
    cur.close()
    conn.close()

# CLI Menu
def main():
    while True:
        print("""
        Address Management System
        1. Add Address
        2. List All Addresses
        3. Update Address
        4. Delete Address
        5. Search Addresses by Group
        6. Exit
        """)
        choice = input("Choose an option: ")
        
        if choice == '1':
            street_address = input("Enter street address: ")
            city = input("Enter city: ")
            state = input("Enter state: ")
            postal_code = input("Enter postal code: ")
            country = input("Enter country: ")
            group_name = input("Enter group name: ")
            add_address(street_address, city, state, postal_code, country, group_name)
        elif choice == '2':
            list_addresses()
        elif choice == '3':
            address_id = int(input("Enter address ID to update: "))
            street_address = input("Enter new street address (leave blank to skip): ")
            city = input("Enter new city (leave blank to skip): ")
            state = input("Enter new state (leave blank to skip): ")
            postal_code = input("Enter new postal code (leave blank to skip): ")
            country = input("Enter new country (leave blank to skip): ")
            group_name = input("Enter new group name (leave blank to skip): ")
            update_address(address_id, street_address, city, state, postal_code, country, group_name)
        elif choice == '4':
            address_id = int(input("Enter address ID to delete: "))
            delete_address(address_id)
        elif choice == '5':
            group_name = input("Enter group name to search: ")
            search_addresses_by_group(group_name)
        elif choice == '6':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
