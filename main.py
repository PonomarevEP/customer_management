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
with conn.cursor() as cur:
    if hello == "1":  # Создать таблицы
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
                
    elif hello == "2":  # Добавить клиента
        client_info = input("Введите данные о клиент в формате Имя, Фамилия, email:   ").split(", ")
        with conn.cursor() as cur:
            cur.execute(f"""
            INSERT INTO clients (f_name, l_name, email)
            VALUES ('{client_info[0]}', '{client_info[1]}', '{client_info[2]}')
            RETURNING id, f_name, l_name, email;      
            """) 
            
            conn.commit()                                    # Иван, Петров, DemonQ3@mail.ru | Игорь, Николаев, NikolIgor@mail.ru
            new_client = cur.fetchone()
            print(f"Добавлен новый клиент:\n"
                f"ID: {new_client[0]}, Имя: {new_client[1]}, Фамилия: {new_client[2]}, Email: {new_client[3]}")
            
    elif hello == "3":  # добавить телефон для существующего клиента
        client_info = input("Введите клиент ид и номер в формате id, номер:   ").split(", ")
        with conn.cursor() as cur:
            cur.execute(f"""
            INSERT INTO clients_phone (clients_id, phone)
            VALUES ({int(client_info[0])}, '{client_info[1]}')
            RETURNING id, clients_id, phone;      
            """) 
            
            conn.commit()                                   # 1, 89220152034  |  2, 89220152512                           
            new_phone = cur.fetchone()
            print(f"Добавлен новый телефон:\n"
                f"ID записи: {new_phone[0]}, Клиент ID: {new_phone[1]}, Телефон: {new_phone[2]}")
            
    elif hello == "4":  # изменить данные о клиенте
        update_client_info = input("Введите ID клиента и новые данные в формате ID, Имя, Фамилия, Email:   ").split(", ")
        with conn.cursor() as cur:
            cur.execute(f"""
            UPDATE clients
            SET f_name = '{update_client_info[1]}', l_name = '{update_client_info[2]}', email = '{update_client_info[3]}'
            WHERE id = {int(update_client_info[0])};
            """)
            
            conn.commit()                                     # 1, Дайнерис, Таргариен, 666@mail.ru 
            print(f"Клиент с ID {update_client_info[0]} обновлен.")
    elif hello == "5":  # удалить телефон для существующего клиента
        delete_phone = input("Введите ID клиента и номер телефона для удаления в формате ID, Номер:   ").split(", ")
        with conn.cursor() as cur:
            cur.execute(f"""
            DELETE FROM clients_phone
            WHERE clients_id = {int(delete_phone[0])} AND phone = '{delete_phone[1]}';
            """)
            
            conn.commit()                                      # 1, 89220152034
            print(f"Телефон {delete_phone[1]} удален для клиента с ID {delete_phone[0]}.")
    elif hello == "6": # удалить существующего клиента
        delete_client_id = int(input("Введите ID клиента для удаления: "))
        with conn.cursor() as cur:
            
            cur.execute(f"""
            DELETE FROM clients_phone
            WHERE clients_id = {delete_client_id};
            """)
            
            cur.execute(f"""
            DELETE FROM clients
            WHERE id = {delete_client_id};
            """)
            
            conn.commit()
            print(f"Клиент с ID {delete_client_id} удален.")

    elif hello == "7":  # найти клиента по его данным: имени, фамилии, email или телефону
        search_criteria = input("Введите критерий поиска (Имя, Фамилия, Email или Телефон):   ")
        with conn.cursor() as cur:
            cur.execute(f"""
            SELECT c.id, c.f_name, c.l_name, c.email, cp.phone
            FROM clients c
            LEFT JOIN clients_phone cp ON c.id = cp.clients_id
            WHERE c.f_name ILIKE '%{search_criteria}%'
            OR c.l_name ILIKE '%{search_criteria}%'
            OR c.email ILIKE '%{search_criteria}%'
            OR cp.phone ILIKE '%{search_criteria}%';
            """)
            
            results = cur.fetchall()
            if not results:
                print("Клиентов с такими данными не найдено.")
            else:
                for row in results:
                    print(f"ID: {row[0]}, Имя: {row[1]}, Фамилия: {row[2]}, Email: {row[3]}, Телефон: {row[4]}")
    else:  # Выход
        print("Выход")
    
    