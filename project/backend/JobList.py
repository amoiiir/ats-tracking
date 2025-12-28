from pymongo import MongoClient
from datetime import datetime, date
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
    
    def _validate_status(self, status):
        """Validate job status against allowed values"""
        allowed_statuses = [
            "applied", "interviewing", "offered", "rejected"
        ]
        return status.lower() in allowed_statuses
    
    def _validate_url(self, url):
        """Basic URL validation"""
        if not url:
            return True
        url = url.strip()
        return url.startswith(('http://', 'https://')) or '.' in url

    def create_job(self, company, position, status, date_applied, salary, job_url, remarks):
        """Create job from user input"""
        try:
            # Validate required fields
            if not company or not company.strip():
                raise ValueError("Company name is required")
            if not position or not position.strip():
                raise ValueError("Position is required")
            if not status or not status.strip():
                raise ValueError("Status is required")
            if not self._validate_status(status):
                raise ValueError(f"Invalid status: {status}. Allowed: applied, interviewing, offer, rejected")
            
            # Validate job_url format
            if job_url and job_url.strip() and not self._validate_url(job_url):
                raise ValueError("Invalid URL format. Must start with http:// or https://")
            
            # Validate and convert date_applied
            if isinstance(date_applied, str):
                date_str = date_applied.strip()
                if not date_str:
                    raise ValueError("date_applied cannot be empty")
                try:
                    # Parse YYYY-MM-DD format only and convert to datetime
                    date_applied = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format only")
            elif isinstance(date_applied, date) and not isinstance(date_applied, datetime):
                # Convert date to datetime (set time to midnight)
                date_applied = datetime.combine(date_applied, datetime.min.time())
            elif isinstance(date_applied, datetime):
                # Already a datetime, keep as is
                pass
            else:
                raise ValueError("date_applied must be a date object or valid date string (YYYY-MM-DD)")
            
            # Validate salary (if provided)
            if salary is not None:
                if isinstance(salary, str):
                    try:
                        salary = float(salary)
                    except ValueError:
                        raise ValueError(f"Invalid salary: {salary}. Must be a number")
                elif not isinstance(salary, (int, float)):
                    raise ValueError("Salary must be a number")
                
                if salary < 0:
                    raise ValueError("Salary cannot be negative")
            
            # Create dictionary
            job_doc = {
                "company": company.strip(),
                "position": position.strip(),
                "status": status.strip().lower(),
                "date_applied": date_applied,
                "salary": salary if salary is not None else None,
                "job_url": job_url.strip() if job_url else None,
                "remarks": remarks.strip() if remarks else None
            }
            result = self.jobs_collection.insert_one(job_doc)
            return str(result.inserted_id)
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return None
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
            # Convert string job_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(job_id):
                job_object_id = ObjectId(job_id)
            else: 
                job_object_id = job_id
            
            # Check if job exists
            existing_job = self.jobs_collection.find_one({"_id": job_object_id})
            if not existing_job:
                raise ValueError(f"Job with ID {job_id} not found")
            
            update_fields = {}
            
            # Validate and add company
            if company is not None:
                company = company.strip() if isinstance(company, str) else company
                if not company:
                    raise ValueError("Company name cannot be empty")
                update_fields["company"] = company
            
            # Validate and add position
            if position is not None:
                position = position.strip() if isinstance(position, str) else position
                if not position:
                    raise ValueError("Position cannot be empty")
                update_fields["position"] = position
            
            # Validate and add status
            if status is not None:
                status = status.strip() if isinstance(status, str) else status
                if not status:
                    raise ValueError("Status cannot be empty")
                if not self._validate_status(status):
                    raise ValueError(f"Invalid status: {status}. Allowed: applied, interviewing, offer, rejected")
                update_fields["status"] = status.lower()
            
            # Validate and convert date_applied
            if date_applied is not None:
                if isinstance(date_applied, str):
                    date_str = date_applied.strip()
                    if not date_str:
                        raise ValueError("date_applied cannot be empty")
                    try:
                        # Parse YYYY-MM-DD format and convert to datetime
                        date_applied = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format only")
                elif isinstance(date_applied, date) and not isinstance(date_applied, datetime):
                    # Convert date to datetime (set time to midnight)
                    date_applied = datetime.combine(date_applied, datetime.min.time())
                elif isinstance(date_applied, datetime):
                    # Already a datetime, keep as is
                    pass
                else:
                    raise ValueError("date_applied must be a date/datetime object or valid date string (YYYY-MM-DD)")
                update_fields["date_applied"] = date_applied
            
            # Validate salary
            if salary is not None:
                if isinstance(salary, str):
                    salary = salary.strip()
                    if not salary:  # Empty string, set to None
                        update_fields["salary"] = None
                    else:
                        try:
                            salary = float(salary)
                            if salary < 0:
                                raise ValueError("Salary cannot be negative")
                            update_fields["salary"] = salary
                        except ValueError:
                            raise ValueError(f"Invalid salary: {salary}. Must be a number")
                elif isinstance(salary, (int, float)):
                    if salary < 0:
                        raise ValueError("Salary cannot be negative")
                    update_fields["salary"] = salary
                else:
                    raise ValueError("Salary must be a number or numeric string")
            
            # Validate and add job_url
            if job_url is not None:
                job_url = job_url.strip() if isinstance(job_url, str) else job_url
                if job_url and not self._validate_url(job_url):
                    raise ValueError("Invalid URL format. Must start with http:// or https://")
                update_fields["job_url"] = job_url if job_url else None
            
            # Add remarks
            if remarks is not None:
                remarks = remarks.strip() if isinstance(remarks, str) else remarks
                update_fields["remarks"] = remarks if remarks else None

            if not update_fields:
                print("No fields to update.")
                return None

            # Update the document
            result = self.jobs_collection.update_one(
                {"_id": job_object_id},
                {"$set": update_fields}
            )
            
            # Return the updated document
            if result.modified_count > 0:
                updated_job = self.jobs_collection.find_one({"_id": job_object_id})
                updated_job["_id"] = str(updated_job["_id"])
                return updated_job
            else:
                # No changes made, but job exists
                existing_job["_id"] = str(existing_job["_id"])
                return existing_job
                
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return None
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