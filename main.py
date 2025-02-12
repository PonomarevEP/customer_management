import psycopg2

class Connection:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.database,
                user=self.user,
                password=self.password
            )
            return self.conn
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")

hello = input(
 """    1 - Создать таблицы
    2 - Добавить клиента
    3 - добавить телефон для существующего клиента
    4 - Изменить данные о клиенте
    5 - Удалить телефон для существующего клиента
    6 - Удалить существующего клиента
    7 - Найти клиента по его данным: имени, фамилии, email или телефону
    -->    """)

db_config = {
    'database': 'customer_management',
    'user': 'postgres',
    'password': '0000'
    }

connection = Connection(**db_config)
conn = connection.connect()

def get_search_criteria():
    criteria = {
        "f_name": None,
        "l_name": None,
        "email": None,
        "phone": None
    }

    while True:
        search_field = input("Введите критерий поиска (f_name, l_name, email или phone) или нажмите Enter для завершения:   ")
        if not search_field:
            break

        search_value = input(f"Введите значение для поиска {search_field}:   ")
        criteria[search_field] = search_value

    return criteria

def create_db(conn):
    with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY, 
                f_name VARCHAR(255), 
                l_name VARCHAR(255),  
                email VARCHAR(255)
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS clients_phone (
                id SERIAL PRIMARY KEY, 
                clients_id INTEGER NOT NULL REFERENCES clients(id),
	            phone VARCHAR(255) NOT NULL
            );
            """)
                
            conn.commit()
            print("Таблицы 'clients' и 'clients_phone' успешно созданы.")

def add_client(conn, first_name, last_name, email):
        with conn.cursor() as cur:
            query = """
            INSERT INTO clients (f_name, l_name, email)
            VALUES (%s, %s, %s)
            RETURNING id, f_name, l_name, email;      
            """
            
            values = (first_name, last_name, email)
            cur.execute(query, values)
            conn.commit()  

            new_client = cur.fetchone()
            print(f"Добавлен новый клиент:\n"
                f"ID: {new_client[0]}, Имя: {new_client[1]}, Фамилия: {new_client[2]}, Email: {new_client[3]}")

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
            query = """
            INSERT INTO clients_phone (clients_id, phone)
            VALUES (%s, %s)
            RETURNING id, clients_id, phone;      
            """
            values = (client_id, phone)
            cur.execute(query, values) 
            conn.commit()                                                            
            
            new_phone = cur.fetchone()
            print(f"Добавлен новый телефон:\n"
                f"ID записи: {new_phone[0]}, Клиент ID: {new_phone[1]}, Телефон: {new_phone[2]}")

def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    update_fields = []
    values_to_update = {}

    if first_name is not None:
        update_fields.append("f_name = %(first_name)s")
        values_to_update["first_name"] = first_name

    if last_name is not None:
        update_fields.append("l_name = %(last_name)s")
        values_to_update["last_name"] = last_name

    if email is not None:
        update_fields.append("email = %(email)s")
        values_to_update["email"] = email

    if len(update_fields) == 0:
        print("Нет изменений для применения.")
        return

    with conn.cursor() as cur:
        sql_query = f"""
        UPDATE clients
        SET {', '.join(update_fields)}
        WHERE id = %(client_id)s;
        """

        values_to_update["client_id"] = int(client_id)

        cur.execute(sql_query, values_to_update)
        conn.commit()

    print(f"Клиент с ID {client_id} обновлен.")

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
            query = """
            DELETE FROM clients_phone
            WHERE clients_id = %s AND phone = %s;
            """

            values = (int(client_id), phone)
            cur.execute(query, values)
            conn.commit()

            print(f"Телефон {phone} удален для клиента с ID {client_id}.")

def delete_client(conn, client_id):
     with conn.cursor() as cur:  
            cur.execute("""
            DELETE FROM clients_phone
            WHERE clients_id = %(client_id)s;
            """, {'client_id': client_id})

            cur.execute("""
            DELETE FROM clients
            WHERE id = %(client_id)s;
            """, {'client_id': client_id})
            
            conn.commit()
            print(f"Клиент с ID {client_id} удален.")

def find_client(conn, criteria):
    with conn.cursor() as cur:
        where_clauses = []
        values_to_search = {}

        for key, value in criteria.items():
            if value is not None:
                where_clauses.append(f"c.{key} ILIKE %(value_{key})s")
                values_to_search[f"value_{key}"] = f"%{value}%"

        if len(where_clauses) == 0:
            print("Нет критериев для поиска.")
            return

        sql_query = f"""
        SELECT c.id, c.f_name, c.l_name, c.email, cp.phone
        FROM clients c
        LEFT JOIN clients_phone cp ON c.id = cp.clients_id
        WHERE {" OR ".join(where_clauses)};
        """

        cur.execute(sql_query, values_to_search)

        results = cur.fetchall()
        if not results:
            print("Клиентов с такими данными не найдено.")
        else:
            for row in results:
                print(f"ID: {row[0]}, Имя: {row[1]}, Фамилия: {row[2]}, Email: {row[3]}, Телефон: {row[4]}")

with conn.cursor() as cur:
    if hello == "1":  
        create_db(conn)            
    elif hello == "2":  
        client_info = input("Введите данные о клиент в формате Имя, Фамилия, email:   ").split(", ")
        add_client(conn, client_info[0], client_info[1], client_info[2])        
    elif hello == "3":  
        client_info = input("Введите клиент ид и номер в формате id, номер:   ").split(", ")
        add_phone(conn, int(client_info[0]), client_info[1])
    elif hello == "4":  
        fields = ["first_name", "last_name", "email"]
        print("Выберите поля для обновления:")
        for i, field in enumerate(fields):
            print(f"{i+1}. {field}")

        choice = input("Введите номера полей через пробел (например, '1 3' для first_name и email): ")
        selected_fields = [fields[int(num)-1] for num in choice.split()]

        client_id = input("Введите ID клиента: ")
        values = {}
        for field in selected_fields:
            value = input(f"Введите новое значение для {field}: ")
            values[field.lower()] = value

        change_client(conn, int(client_id), **values)
    elif hello == "5":  
        phone = input("Введите ID клиента и номер телефона для удаления в формате ID, Номер:   ").split(", ")
        delete_phone(conn, int(phone[0]), phone[1])
    elif hello == "6": 
        delete_client_id = int(input("Введите ID клиента для удаления: "))
        delete_client(conn, delete_client_id)
    elif hello == "7":  
        criteria = get_search_criteria()
        find_client(conn, criteria)
    else:  
        print("Выход")

conn.close()
    
    