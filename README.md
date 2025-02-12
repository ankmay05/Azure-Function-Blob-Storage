This Azure Function application allows users to:

Upload photos to Azure Blob Storage.
Automatically watermark images using an Azure Blob Trigger.
Download images from Azure Blob Storage.
Features
✅ Upload an image via HTTP POST request.
✅ Automatically apply a watermark (INDIA) using a Blob Trigger.
✅ Store watermarked images in a separate Azure Blob container.
✅ Download images via HTTP GET request.

Getting Started :

Prerequisites
Python 3.8+
Azure Function Core Tools
Azure Blob Storage
An Azure Storage Account
Installation & Setup
Clone the repository



sh
Copy
Edit
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
Install dependencies

sh
Copy
Edit
pip install -r requirements.txt
Configure Azure Storage
Rename local.settings.json.example to local.settings.json and update it with your Azure Storage Connection String:

json
Copy
Edit
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your_connection_string>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "photoswater_STORAGE": "<your_connection_string>"
  }
}
Run the function locally

sh
Copy
Edit
func start
Usage
Upload Photo
Endpoint: POST /api/uploadphoto
Usage (cURL Example):
sh
Copy
Edit
curl -X POST -F "file=@yourimage.png" http://localhost:7071/api/uploadphoto
Response:
nginx
Copy
Edit
Photo yourimage.png uploaded successfully!
Download Photo
Endpoint: GET /api/downloadphoto?file=<filename>
Usage:
sh
Copy
Edit
curl -X GET "http://localhost:7071/api/downloadphoto?file=yourimage.png" -o downloaded_image.png
Response: Returns the requested image.
How the Watermarking Works
When an image is uploaded to userimage/, the Blob Trigger is activated.
The function:
Reads the uploaded image.
Applies a watermark (INDIA).
Saves the watermarked image in another container.
Deploying to Azure
Login to Azure

sh
Copy
Edit
az login
Create an Azure Function App

sh
Copy
Edit
az functionapp create --resource-group <resource-group-name> --consumption-plan-location <location> --runtime python --functions-version 4 --name <function-app-name> --storage-account <storage-account-name>
Deploy

sh
Copy
Edit
func azure functionapp publish <function-app-name>
Contributing
If you'd like to contribute, feel free to open an issue or submit a pull request! 🚀

License
This project is licensed under the MIT License.

