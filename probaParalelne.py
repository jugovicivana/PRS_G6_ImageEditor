import multiprocessing
from multiprocessing import Pool
from PIL import Image, ImageEnhance
import time

def change_saturation(image_path, factor):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def process_image_serially(image_paths, factor):
    results = []
    for image_path in image_paths:
        result = change_saturation(image_path, factor)
        results.append(result)
    return results

def process_image_parallel(image_paths, factor, num_processes):
    with Pool(num_processes) as pool:
        results = pool.starmap(change_saturation, [(image_path, factor) for image_path in image_paths])
    return results

if __name__ == "__main__":
    image_paths = ["poz.png", "joffir.jpg", "landscape.jpg"]  # Put the paths to your images here
    factor = 1.5  # Example factor for changing saturation
    num_processes = 4  # Number of processes to use

    # Serial processing
    start_time = time.time()
    serial_results = process_image_serially(image_paths, factor)
    serial_time = time.time() - start_time
    print(f"Serial processing time: {serial_time} seconds")

    # Parallel processing
    start_time = time.time()
    parallel_results = process_image_parallel(image_paths, factor, num_processes)
    parallel_time = time.time() - start_time
    print(f"Parallel processing time: {parallel_time} seconds")

    # Optionally save results
    for i, result in enumerate(serial_results):
        result.save(f"serial_result_{i}.jpg")
    for i, result in enumerate(parallel_results):
        result.save(f"parallel_result_{i}.jpg")
