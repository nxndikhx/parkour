import pandas as pd
import numpy as np

# Load the dataset
file_path = "updated_parking_slots_dataset.csv"  # Update with your actual path
df = pd.read_csv(file_path)

# Define dimension ranges for parking slots based on common car sizes
dimension_ranges = {
    "Length": (3.5, 4.8),  # in meters
    "Width": (1.6, 1.8),
    "Height": (1.5, 1.7)
}

# Set seed for reproducibility
np.random.seed(42)

# Add random dimensions to each slot within the given range
df["Max_Length"] = np.round(np.random.uniform(*dimension_ranges["Length"], size=len(df)), 2)
df["Max_Width"] = np.round(np.random.uniform(*dimension_ranges["Width"], size=len(df)), 2)
df["Max_Height"] = np.round(np.random.uniform(*dimension_ranges["Height"], size=len(df)), 2)

# Save the updated dataset
df.to_csv("updated_parking_slots_with_dimensions.csv", index=False)
print("✅ Dimensions added and file saved as 'updated_parking_slots_with_dimensions.csv'")