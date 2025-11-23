#!/usr/bin/env python3
"""Migrate existing work items to new category/action_type system."""
import sqlite3
import sys

# Map old work_type to new (category, action_type)
TYPE_MAP = {
    'new_service': ('service', 'new'),
    'config_change': ('platform_feature', 'change'),
    'new_vm': ('service', 'new'),
    'troubleshooting': ('platform_feature', 'fix'),
}

def migrate():
    db_path = 'calcifer-app/data/calcifer.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add new columns if they don't exist
    try:
        cursor.execute("ALTER TABLE work_items ADD COLUMN category TEXT")
        cursor.execute("ALTER TABLE work_items ADD COLUMN action_type TEXT")
        print("✅ Added new columns")
    except sqlite3.OperationalError:
        print("ℹ️  Columns already exist")
    
    # Migrate existing data
    cursor.execute("SELECT id, work_type FROM work_items WHERE category IS NULL")
    rows = cursor.fetchall()
    
    for row_id, old_type in rows:
        if old_type in TYPE_MAP:
            category, action = TYPE_MAP[old_type]
            cursor.execute(
                "UPDATE work_items SET category = ?, action_type = ? WHERE id = ?",
                (category, action, row_id)
            )
            print(f"✅ Migrated work item {row_id}: {old_type} → {category}/{action}")
        else:
            # Default fallback
            cursor.execute(
                "UPDATE work_items SET category = ?, action_type = ? WHERE id = ?",
                ('platform_feature', 'change', row_id)
            )
            print(f"⚠️  Migrated work item {row_id}: {old_type} → platform_feature/change (default)")
    
    conn.commit()
    conn.close()
    print("\n🔥 Migration complete!")

if __name__ == '__main__':
    migrate()