#!/usr/bin/env python3
"""
Script to check and fix the player_teams_association table structure
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.sql import text
from db.database import async_session

async def check_table_structure():
    """Check the current table structure and constraints"""
    print("🔍 Checking player_teams_association table structure...")
    
    async with async_session() as session:
        try:
            # Get table information
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'player_teams_association' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print("\n📋 Table columns:")
            for col in columns:
                print(f"   {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
            # Get constraint information
            result = await session.execute(text("""
                SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = 'player_teams_association'
                ORDER BY tc.constraint_type, kcu.ordinal_position;
            """))
            
            constraints = result.fetchall()
            print("\n🔒 Table constraints:")
            for constraint in constraints:
                print(f"   {constraint[1]}: {constraint[0]} on {constraint[2]}")
                
        except Exception as e:
            print(f"❌ Error checking table structure: {e}")

async def fix_table_structure():
    """Drop and recreate the table with correct structure"""
    print("\n🔧 Fixing table structure...")
    
    async with async_session() as session:
        try:
            # Drop the table
            await session.execute(text("DROP TABLE IF EXISTS player_teams_association CASCADE;"))
            print("   ✅ Dropped existing table")
            
            # Create the table with correct structure
            await session.execute(text("""
                CREATE TABLE player_teams_association (
                    players_teams_id SERIAL PRIMARY KEY,
                    player_id INTEGER NOT NULL REFERENCES players(player_id),
                    team_id INTEGER NOT NULL REFERENCES teams(team_id),
                    season VARCHAR NOT NULL,
                    UNIQUE(player_id, team_id, season)
                );
            """))
            print("   ✅ Created table with correct structure")
            
            await session.commit()
            print("   ✅ Changes committed")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error fixing table structure: {e}")

async def main():
    """Main function"""
    print("🏀 NBA Database - Table Structure Check & Fix")
    print("=" * 50)
    
    await check_table_structure()
    
    print("\n" + "=" * 50)
    response = input("Do you want to fix the table structure? (y/N): ")
    
    if response.lower() == 'y':
        await fix_table_structure()
        print("\n🔍 Checking structure after fix...")
        await check_table_structure()
    else:
        print("❌ Table structure not modified")

if __name__ == "__main__":
    asyncio.run(main())