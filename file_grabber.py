import pandas as pd
import os


def get_all_users():
    directory_path = input("Enter the absolute path to your Excel files: ")
    combined_df = pd.DataFrame()

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_excel(file_path, usecols=["E-Mail Address"])  # change this header name as needed
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    if combined_df.columns[0] == 'C':
        combined_df.sort_values(by='C', inplace=True)
    else:
        combined_df.columns = ['C']  # Assign a header if not present
        combined_df.sort_values(by='C', inplace=True)
    output_path = os.path.join('ENTER_YOUR_OUTPUT_PATH_HERE', 'all_users.txt')
    combined_df.to_csv(output_path, sep='\t', index=False, header=False)

    return output_path, f"All data has been combined and written to {output_path}"


output_path, message = get_all_users()
print(message)
