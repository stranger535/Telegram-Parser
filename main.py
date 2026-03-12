import pandas as pd
import asyncio
import time
import random
from datetime import timedelta
from tqdm import tqdm
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError

# Input credentials
api_id =   # Your API ID 
api_hash = ''
phone = '+.......'

async def main():
    print("Starting Telegram user data extraction...")
    start_time = time.time()
    
    async with TelegramClient(phone, api_id, api_hash) as client:
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (ID: {me.id})")

        chat = 'https://t.me/Your chat HERE'
        print(f"Fetching participants from {chat}...")
        
        
        data_item = []
        total_count = 0
        
        # Progress bar 
        pbar = tqdm(desc="Fetching users", unit="user")
        
        try:
            
            participants_iter = client.iter_participants(chat, limit=None)  
            
            batch_size = 200  # batches for progress display
            batch = []
            
            async for participant in participants_iter:
                batch.append(participant)
                
                
                if len(batch) >= batch_size:
                    
                    for item in batch:
                        data_item.append([item.first_name, item.last_name, item.id, item.username])
                    
                    # counters and progress
                    total_count += len(batch)
                    pbar.update(len(batch))
                    
                    # Clear batch
                    batch = []
                    
                    # Random delay between batches (2-5 seconds)
                    try:
                        delay = random.uniform(2, 5)
                        await asyncio.sleep(delay)
                    except FloodWaitError as e:
                        # rate limiting
                        wait_time = e.seconds
                        pbar.write(f"Rate limited! Waiting for {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
            
            
            if batch:
                for item in batch:
                    data_item.append([item.first_name, item.last_name, item.id, item.username])
                
                total_count += len(batch)
                pbar.update(len(batch))
        
        finally:
            pbar.close()
            
        print(f"Successfully retrieved {total_count} users.")
        
        # Create pandas DataFrame
        print("Creating DataFrame...")
        df = pd.DataFrame(data_item, columns=['first_name', 'last_name', 'id', 'username'])
        
        # Save to txt file
        print("Saving to text file...")
        with open('telegram_users.txt', 'w', encoding='utf-8') as file:
            for user in data_item:
                if user[3]:  # If username exists
                    file.write(f"@{user[3]}\n")
                
                file.write(f"ID: {user[2]}\n")
                
                if user[0]:  # If first name exists
                    file.write(f"First: {user[0]}\n")
                    
                if user[1]:  # If last name exists
                    file.write(f"Last: {user[1]}\n")
                    
                file.write("\n")  # Empty line
        
        # Save to CSV
        print("Saving to CSV database...")
        df.to_csv('client_database.csv', index=False)
        
        # Calculate and display
        end_time = time.time()
        duration = end_time - start_time
        formatted_duration = str(timedelta(seconds=int(duration)))
        
        print("\n" + "="*50)
        print(f"SUMMARY:")
        print(f"Total users processed: {total_count}")
        print(f"Time elapsed: {formatted_duration}")
        print(f"Data saved to:")
        print(f"  - telegram_users.txt")
        print(f"  - client_database.csv")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(main())