import numpy as np

# Create sample arrays with specified shapes
arrays = [
    np.random.rand(10, 10),
    np.random.rand(10),
    np.random.rand(10, 8),
    np.random.rand(8),
    np.random.rand(8, 4),
    np.random.rand(4)
]

# Reshape to one-dimensional arrays and back to their original shapes
reshaped_arrays = []

for array in arrays:
    # Reshape to 1D
    one_d_array = array.reshape(-1)
    
    # Reshape back to the original shape
    original_shape_array = one_d_array.reshape(array.shape)
    
    # Store the reshaped array for further use
    reshaped_arrays.append(original_shape_array)
    
    # Verify the reshaping process
    print("Original shape:", array.shape)
    print("Reshaped to 1D:", one_d_array.shape)
    print("Reshaped back to original shape:", original_shape_array.shape)
    print("Reshaped array matches original:", np.array_equal(array, original_shape_array))
    print()