import azure.functions as func
import logging
import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont  # Added import


# Initialize Function App
app = func.FunctionApp()

# Azure Blob Storage connection string (Replace with your actual connection string)
AZURE_STORAGE_CONNECTION_STRING = "your_credentials"
CONTAINER_NAME = "name of your container"
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    blobs = container_client.list_blobs()
    for blob in blobs:
        print("Found blob:", blob.name)
    
    print("Blob Storage connection is working!")
except Exception as e:
    print("Error:", str(e))


@app.route(route="uploadphoto", methods=["POST"])
def upload_photo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing photo upload request")

    # Get file from request
    file = req.files.get("file")
    if not file:
        return func.HttpResponse("No file uploaded", status_code=400)

    try:
        # Create a Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file.filename)

        # Upload file to Blob Storage
        blob_client.upload_blob(file.read(), overwrite=True)


        return func.HttpResponse(f"Photo {file.filename} uploaded successfully!", status_code=200)

    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        return func.HttpResponse("Error uploading file", status_code=500)
    


    



WATERMARKED_CONTAINER = "your container"  # you can save your images in the same container if you want

@app.blob_trigger(arg_name="myblob", path="userimage/{name}" ,connection="AzureWebJobsStorage")
def watermark(myblob: func.InputStream):
    logging.info(f"Processing image: {myblob.name}, Size: {myblob.length} bytes")

    try:
        # Read the image from blob
        image_stream = BytesIO(myblob.read())  
        if image_stream.getbuffer().nbytes == 0:
            raise ValueError("Input image is empty. Processing failed.")

        image = Image.open(image_stream)
        logging.info("Image successfully loaded.")

        # Apply watermark
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()  # Avoid missing font issue
        text = "INDIA"
        draw.text((10, 10), text, fill=(0, 0, 0), font=font)

        # Save the watermarked image
        output_stream = BytesIO()
        image.save(output_stream, format="PNG")  # Ensure valid format
        output_stream.seek(0)  # Reset stream position

        # **Check if the output image is empty**
        if output_stream.getbuffer().nbytes == 0:
            raise ValueError("Generated image is empty. Processing failed.")

        # **Ensure minimum upload size** (Azure requires at least 1 byte)
        output_data = output_stream.getvalue()
        if len(output_data) == 0:
            raise ValueError("Watermarked image is empty, cannot upload.")

        # Upload to a different container
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        watermarked_blob_client = blob_service_client.get_blob_client(
            container=WATERMARKED_CONTAINER, 
            blob="watermarked_" + myblob.name
        )

        # **Ensure valid upload size for Azure**
        watermarked_blob_client.upload_blob(output_data, blob_type="BlockBlob", overwrite=True)
        logging.info(f"Watermarked image uploaded as watermarked_{myblob.name}")

    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")  


@app.route(route="downloadphoto", methods=["GET"])
def download_photo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing photo download request")

    # Get the filename from the query parameter
    file_name = req.params.get("file")
    if not file_name:
        return func.HttpResponse("File name is required", status_code=400)

    try:
        # Create a Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_name)

        # Download the blob
        stream = blob_client.download_blob()
        file_data = stream.readall()

        # Return the file as a response
        return func.HttpResponse(file_data, mimetype="image/png", status_code=200)

    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return func.HttpResponse("Error downloading file", status_code=500)

