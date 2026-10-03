import database

if __name__ == "__main__":
    database.seed_demo_data(force=True)
    print("Database seeded successfully!")
