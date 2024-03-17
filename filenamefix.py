import os

# Define the path to the folder containing the images
folder_path = r'C:\Users\Nicholas Surmon\Documents\TestPythonAIs\scraper\images\main categories\Mens cargo pants'

# Loop through each file in the folder
for filename in os.listdir(folder_path):
    # Check if the filename contains the problematic character sequence
    if 'â€™' in filename:
        # Define the new filename by replacing the problematic sequence with an empty string
        new_filename = filename.replace('â€™', '')
        # Define the full path to the original and new file
        original_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)
        # Rename the file
        os.rename(original_file_path, new_file_path)
        print(f'Renamed "{filename}" to "{new_filename}"')

print('Finished processing files.')
