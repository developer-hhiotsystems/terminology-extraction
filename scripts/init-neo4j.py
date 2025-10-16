#!/usr/bin/env python
"""Initialize Neo4j database with schema and indexes"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

def main():
    print("\n" + "="*70)
    print("  Neo4j Database Initialization")
    print("="*70 + "\n")

    # Import configuration
    try:
        from config import config
    except ImportError:
        print("[ERROR] Could not import config. Make sure you're in the project root.\n")
        sys.exit(1)

    # Test Neo4j connection
    print("Configuration:")
    print(f"  URI: {config.NEO4J_URI}")
    print(f"  User: {config.NEO4J_USER}")
    print("")

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("[ERROR] neo4j package not installed")
        print("Run: pip install neo4j\n")
        sys.exit(1)

    print("Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )

        # Verify connection
        driver.verify_connectivity()
        print("[OK] Connected to Neo4j successfully\n")

    except Exception as e:
        print(f"[ERROR] Could not connect to Neo4j: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if Neo4j is running:")
        print("     - Docker: docker ps | grep neo4j")
        print("     - Desktop: Check Neo4j Desktop application")
        print("  2. Verify connection details in .env file")
        print("  3. Check if port 7687 is accessible")
        print("  4. Try: curl http://localhost:7474\n")
        sys.exit(1)

    # Initialize schema
    print("Initializing database schema...\n")

    with driver.session() as session:

        # Create constraints (unique identifiers)
        print("Creating constraints...")
        constraints = [
            "CREATE CONSTRAINT term_id IF NOT EXISTS FOR (t:Term) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT entry_id IF NOT EXISTS FOR (e:Entry) REQUIRE e.entry_id IS UNIQUE",
            "CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE"
        ]

        for constraint in constraints:
            try:
                session.run(constraint)
                print(f"  [OK] {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
            except Exception as e:
                print(f"  [WARN] {str(e).split('(')[0]}")

        print("")

        # Create indexes for performance
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX term_text IF NOT EXISTS FOR (t:Term) ON (t.text)",
            "CREATE INDEX term_language IF NOT EXISTS FOR (t:Term) ON (t.language)",
            "CREATE INDEX entry_source IF NOT EXISTS FOR (e:Entry) ON (e.source_file)",
            "CREATE INDEX domain_category IF NOT EXISTS FOR (d:Domain) ON (d.category)"
        ]

        for index in indexes:
            try:
                session.run(index)
                print(f"  [OK] {index.split('FOR')[1].split('ON')[0].strip()}")
            except Exception as e:
                print(f"  [WARN] {str(e).split('(')[0]}")

        print("")

        # Get database statistics
        print("Database Statistics:")
        print("-" * 70)

        # Count nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()["count"]
        print(f"  Total Nodes: {node_count}")

        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()["count"]
        print(f"  Total Relationships: {rel_count}")

        # Count by label
        result = session.run("CALL db.labels()")
        labels = [record["label"] for record in result]

        if labels:
            print("\n  Nodes by Label:")
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"    {label}: {count}")

        print("")

        # Show constraints
        result = session.run("SHOW CONSTRAINTS")
        constraints = list(result)
        if constraints:
            print(f"  Active Constraints: {len(constraints)}")

        # Show indexes
        result = session.run("SHOW INDEXES")
        indexes = list(result)
        if indexes:
            print(f"  Active Indexes: {len(indexes)}")

        print("")

    driver.close()

    print("[OK] Neo4j initialization completed successfully!")
    print("\nYou can now:")
    print("  1. Access Neo4j Browser: http://localhost:7474")
    print("  2. Run queries to explore the database")
    print("  3. Start the backend application\n")

if __name__ == "__main__":
    main()
