import os.path
import io
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
"https://www.googleapis.com/auth/classroom.coursework.students", "https://www.googleapis.com/auth/classroom.courses.readonly", "https://www.googleapis.com/auth/classroom.rosters", "https://www.googleapis.com/auth/drive"]

def main():
  """Shows basic usage of the Classroom API.
  Prints the names of the first 10 courses the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("classroom", "v1", credentials=creds)

    # Call the Classroom API
    results = service.courses().list(pageSize=10).execute()
    courses = results.get("courses", [])

    if not courses:
      print("No courses found.")
      return
    # Prints the names of the first 10 courses.
    print("Courses:")
    for course in courses:
      print(course["name"])
      print(course["id"])

  except HttpError as error:
    print(f"An error occurred: {error}")

  print("------------xxx-----------")

  try:
    service = build("classroom", "v1", credentials=creds)

    courseid = "733445218873" #input("Enter The course ID: ")
    print("Course ID: " + courseid)
    results2 = service.courses().courseWork().list(courseId=courseid).execute() #service.courses().coursework().list().execute()
    courses2 = results2.get("courseWork", [])
    print("Course Work:")
    for course in courses2:
      print(course["title"])
      print(course["id"])

  except HttpError as error:
    print(f"An error occurred: {error}")

  print("------------xxx-----------")

  # try:
  #   service = build("classroom", "v1", credentials=creds)

  #   courseworkid = input("Enter The course work ID: ")
  #   print("Course work Id: " + courseworkid)
  #   results3 = service.courses().courseWork().studentSubmissions().list(courseId=courseid, courseWorkId=courseworkid).execute() #service.courses().coursework().list().execute()
  #   courses3 = results3.get("studentSubmissions", [])
  #   print("Students Submissions:")
  #   for course in courses3:
  #     studentdata = service.courses().students().get(courseId = courseid, userId = course["userId"]).execute()
  #     studentname = studentdata.get("profile", [])
  #     studentname2 = studentname.get("name", [])
  #     print(studentname2["fullName"])
  #     print(course["userId"])
  #     print(course["state"])
  # except HttpError as error:
  #   print(f"An error occurred: {error}")

  try:
    service = build("classroom", "v1", credentials=creds)
    service_Gdrive = build('drive', 'v3', credentials=creds)
    courseworkid = input("Enter The course work ID: ")
    
    print("Course work Id: " + courseworkid)
    results3 = service.courses().courseWork().studentSubmissions().list(courseId=courseid, courseWorkId=courseworkid).execute()

    #courses3 is collecting all data including student submission gdrive link, students id, and students file names for a course work
    courses3 = results3.get("studentSubmissions", [])

    studentdata = service.courses().students().list(courseId = courseid).execute()

    #studentdata2 is collecting only names of the students registered for the course
    studentdata2 = studentdata.get("students", [])

    #Here we are creating a folder for collecting all the files
    if not os.path.exists(courseworkid):
            os.makedirs(courseworkid)


    print("Students Submissions:")

    #Going Through each students work
    for course in courses3:
      print("")
      flag = 0
      #Finding Student Name
      for student in studentdata2:
        if student["userId"] == course["userId"]:
          flag = 1
          full_name = student["profile"]["name"]["fullName"]
          break 
        
      if flag == 0:
          studentMissing = service.courses().students().get(courseId = courseid , userId = course["userId"]).execute()
          full_name = studentMissing["profile"]["name"]["fullName"]
          
      print(f"Full Name: {full_name}")    
      print(course["userId"])
      print(course["state"])

      #checking is students have submitted the work
      if course["state"] == "TURNED_IN":
        attachments = course.get("assignmentSubmission", {}).get("attachments", [])

        #creating a folder path for a student to download their submissions
        folder_path = os.path.join(courseworkid, full_name)


        for attachment in attachments:
            drive_file = attachment.get("driveFile", {})
            file_id = drive_file.get("id")
            file_title = drive_file.get("title")
            if not os.path.exists(folder_path):
              os.makedirs(folder_path)
            # if file_id:
            #     print(f"Drive File ID: {file_id}")
            #     print(f"Title: {file_title}")
            try:
              # Get file metadata
              #file_metadata = service_Gdrive.files().get(fileId=file_id).execute()
              print(f"Downloading file: {file_title}")

              # Prepare file download
              request = service_Gdrive.files().get_media(fileId=file_id)
              file_path0 = os.path.join(os.getcwd(),folder_path)
              file_path = os.path.join(file_path0,file_title)
              temp_name = file_path + ".part"  # Temporary file name for the download process
              
              # Download file in chunks
              with open(temp_name, "wb") as temp_file:
                  downloader = MediaIoBaseDownload(temp_file, request)
                  done = False
                  while not done:
                      status, done = downloader.next_chunk()
                      if status:
                          print(f"Download progress: {int(status.progress() * 100)}%")
              
              # Rename the downloaded file to the intended name
              os.rename(temp_name, file_path)
              print(f"File downloaded successfully as: {file_path}")

            except Exception as e:
              print(f"An error occurred: {e}")
      else:
        print(f"Skipping {full_name} as no submissions present")
      

  except HttpError as error:
    print(f"An error occurred: {error}")


#   service_Gdrive = build('drive', 'v3', credentials=creds)
#   file_id = input("Enter File Id to Download: ")
#   filename = input("Enter Name of the file: ")
#   download_file(service_Gdrive, file_id, filename)

# def download_file(service, file_id, file_name):
#     """Download a file from Google Drive."""
#     try:
#         # Get file metadata
#         file_metadata = service.files().get(fileId=file_id).execute()
#         print(f"Downloading file: {file_metadata['name']}")

#         # Prepare file download
#         request = service.files().get_media(fileId=file_id)
#         file_path = os.path.join(os.getcwd(), file_metadata['name'])
#         temp_name = file_path + ".part"  # Temporary file name for the download process
        
#         # Download file in chunks
#         with open(temp_name, "wb") as temp_file:
#             downloader = MediaIoBaseDownload(temp_file, request)
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 if status:
#                     print(f"Download progress: {int(status.progress() * 100)}%")
        
#         # Rename the downloaded file to the intended name
#         os.rename(temp_name, file_path)
#         print(f"File downloaded successfully as: {file_path}")

#     except Exception as e:
#         print(f"An error occurred: {e}")


if __name__ == "__main__":
  main()