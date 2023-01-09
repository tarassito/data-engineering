import threading
import time

import psycopg2


def init_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )


def reset_counter():
    conn = init_connection()

    cursor = conn.cursor()
    cursor.execute("UPDATE user_counter SET counter = 1, version = 1 WHERE user_id = 1")
    conn.commit()


def lost_update():
    conn = init_connection()

    cursor = conn.cursor()
    for i in range(100):
        cursor.execute('SELECT counter FROM user_counter WHERE user_id = 1')
        counter = cursor.fetchone()[0]
        cursor.execute(f"UPDATE user_counter SET counter = {counter + 1} where user_id = 1")
        conn.commit()

    cursor.close()
    conn.close()


def in_place_update():
    conn = init_connection()

    cursor = conn.cursor()
    for i in range(100):
        cursor.execute("UPDATE user_counter SET counter = counter + 1 where user_id = 1")
        conn.commit()

    cursor.close()
    conn.close()


def row_level_locking():
    conn = init_connection()

    cursor = conn.cursor()
    for i in range(100):
        cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE")
        counter = cursor.fetchone()[0]
        cursor.execute(f"UPDATE user_counter SET counter = {counter + 1} where user_id = 1")
        conn.commit()

    cursor.close()
    conn.close()


def optimistic_control():
    conn = init_connection()

    cursor = conn.cursor()
    for i in range(100):
        while True:
            cursor.execute('SELECT counter, version FROM user_counter WHERE user_id = 1')
            counter, version = cursor.fetchone()
            cursor.execute(f"UPDATE user_counter SET counter = {counter + 1}, version = {version + 1} "
                           f"WHERE user_id = 1 and version = {version}")
            conn.commit()
            count = cursor.rowcount
            if count > 0:
                break

    cursor.close()
    conn.close()


def run(func):
    threads = [threading.Thread(target=func) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_time = time.time()
    reset_counter()
    run(lost_update)
    print("--- %0.2f seconds for lost update ---" % (time.time() - start_time))

    start_time = time.time()
    reset_counter()
    run(in_place_update)
    print("--- %0.2f seconds for update in place ---" % (time.time() - start_time))

    start_time = time.time()
    reset_counter()
    run(row_level_locking)
    print("--- %0.2f seconds for row level locking ---" % (time.time() - start_time))

    start_time = time.time()
    reset_counter()
    run(optimistic_control)
    print("--- %0.2f seconds for optimistic concurrency control ---" % (time.time() - start_time))
