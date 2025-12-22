from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGODB_ATLAS_CLUSTER_URI")

class JobList:

    # Connection and creating indexes
    def __init__(self, db_name="job_list", connection_string=mongo_uri):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.jobs_collection = self.db.jobs
        self.init_database()

    def init_database(self):
        self.jobs_collection.create_index("job_id")

    def create_job(self, company, position, status, date_applied, salary, job_url, remarks):
        """Create job from user input"""
        try:
            # Create dictionary
            job_doc = {
                "company": company,
                "position": position,
                "status": status,
                "date_applied": date_applied,
                "salary": salary,
                "job_url": job_url,
                "remarks": remarks
            }
            result = self.jobs_collection.insert_one(job_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating jobs: {e}")
            return None
        
    def get_all_jobs(self):
        """Retrieve all jobs from the database"""
        try:
            jobs = list(self.jobs_collection.find())
            for job in jobs:
                job["_id"] = str(job["_id"])  # Convert ObjectId to string for easier handling
            return jobs
        except Exception as e:
            print(f"Error retrieving jobs: {e}")
            return []
        
    def update_job(self, job_id, company=None, position=None, status=None, date_applied=None, salary=None, job_url=None, remarks=None):
        """Update job listed"""
        try:
            update_fields = {}
            if company is not None:
                update_fields["company"] = company
            if position is not None:
                update_fields["position"] = position
            if status is not None:
                update_fields["status"] = status
            if date_applied is not None:
                update_fields["date_applied"] = date_applied
            if salary is not None:
                update_fields["salary"] = salary
            if job_url is not None:
                update_fields["job_url"] = job_url
            if remarks is not None:
                update_fields["remarks"] = remarks

            if not update_fields:
                print("No fields to update.")
                return None
            
            # convert string job_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(job_id):
                job_object_id = ObjectId(job_id)
            else: 
                job_object_id = job_id

            result = self.jobs_collection.update_one(
                {"_id": job_object_id},
                {"$set": update_fields}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating job: {e}")
            return None
        
    def delete_job(self, job_id):
        """Delete specific jobs"""
        try:
            # Convert string job_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(job_id):
                job_object_id = ObjectId(job_id)
            else: 
                job_object_id = job_id

            # Delete the job
            result = self.jobs_collection.delete_one({"_id": job_object_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Delete failed: {e}")
            return None
        
    def total_application(self):
        """Return total number of jobs in the database."""
        try:
            return self.jobs_collection.count_documents({})
        except Exception as e:
            print(f"Error counting jobs: {e}")
            return 0
        
    def close_connection(self):
        """Close the database connection."""
        self.client.close()

def display_menu():
    print("Job List Management")
    print("1. Create Job")
    print("2. View All Jobs")
    print("3. Update Job")
    print("4. Delete Job")
    print("5. Number of applications")
    print("6. Exit")

def main():
    """Main interactive CLI Function"""
    try:
        db = JobList()
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Make sure MongoDB is runningg on localhost:27017 or check your connection string.")
        return
    
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            print("--- Create new Job ---")
            company = input("Company: ")
            position = input("Position: ")
            status = input("Status: ")
            date_applied = input("Date Applied (YYYY-MM-DD): ")
            salary = input("Salary: ")
            job_url = input("Job URL: ")
            remarks = input("Remarks: ")

            try:
                job_id = db.create_job(company, position, status, date_applied, salary, job_url, remarks)
                if job_id:
                    print(f"Job created with ID: {job_id}")
                else:
                    print("Failed to create job.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '2':
            print("--- All Jobs ---")
            jobs = db.get_all_jobs()
            if jobs:
                for job in jobs:
                    print(job)
            else:
                print("No jobs found.")

        elif choice == '3':
            print("--- Update Job ---")
            job_id = input("Enter Job ID to update: ")
            print("Enter new values (leave blank to keep current value):")
            company = input("Company: ") or None
            position = input("Position: ") or None
            status = input("Status: ") or None
            date_applied = input("Date Applied (YYYY-MM-DD): ") or None
            salary = input("Salary: ") or None
            job_url = input("Job URL: ") or None
            remarks = input("Remarks: ") or None

            try:
                success = db.update_job(job_id, company, position, status, date_applied, salary, job_url, remarks)
                if success:
                    print("Job updated successfully.")
                else:
                    print("Failed to update job.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '4':
            print("--- Delete Job ---")
            job_id = input("Enter Job ID to delete: ")

            try:
                success = db.delete_job(job_id)
                if success:
                    print("Job deleted successfully.")
                else:
                    print("Failed to delete job.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '5':
            print("--- Total Applications ---")
            total = db.total_application()
            print(f"Total number of job applications: {total}")

        elif choice == '6':
            print("Exiting...")
            db.close_connection()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()