use pyo3::prelude::*;
use image::{DynamicImage, ImageBuffer, Rgb};
use imageproc::edges::canny;

#[derive(Debug)]
enum ImageEffect {
    EdgeDetect,
    Blur,
    Sharpen,
    Grayscale,
    Sepia,
    Invert
}

impl ImageEffect {
    fn from_str(s: &str) -> Option<Self> {
        match s {
            "edge_detect" => Some(Self::EdgeDetect),
            "blur" => Some(Self::Blur),
            "sharpen" => Some(Self::Sharpen),
            "grayscale" => Some(Self::Grayscale),
            "sepia" => Some(Self::Sepia),
            "invert" => Some(Self::Invert),
            _ => None
        }
    }
}

/// Process an image using various effects
#[pyfunction]
fn process_image(
    py: Python,
    input_path: String,
    effect_type: String,
    output_path: String,
    progress_callback: PyObject,
) -> PyResult<String> {
    // Load the image
    let img = image::open(&input_path).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Failed to load image: {}", e))
    })?;

    let effect = ImageEffect::from_str(&effect_type)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Unknown effect type"))?;

    let processed = match effect {
        ImageEffect::EdgeDetect => apply_edge_detection(py, img, &progress_callback)?,
        ImageEffect::Blur => apply_blur(py, img, &progress_callback)?,
        ImageEffect::Sharpen => apply_sharpen(py, img, &progress_callback)?,
        ImageEffect::Grayscale => apply_grayscale(py, img, &progress_callback)?,
        ImageEffect::Sepia => apply_sepia(py, img, &progress_callback)?,
        ImageEffect::Invert => apply_invert(py, img, &progress_callback)?,
    };

    // Save the processed image to the specified output path
    processed.save(&output_path).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Failed to save image: {}", e))
    })?;

    Ok(output_path)
}

fn apply_edge_detection(
    py: Python,
    image: DynamicImage,
    progress_callback: &PyObject,
) -> PyResult<DynamicImage> {
    let gray_image = image.to_luma8();
    
    // Apply Canny edge detection with more pronounced parameters
    let edges = canny(&gray_image, 25.0, 75.0);  // Adjusted thresholds for more visible edges
    
    // Convert to RGB for better visibility
    let mut rgb_image = ImageBuffer::new(edges.width(), edges.height());
    for (x, y, pixel) in edges.enumerate_pixels() {
        let val = pixel.0[0];
        rgb_image.put_pixel(x, y, Rgb([255 - val, 255 - val, 255 - val]));  // Invert colors for better visibility
    }
    
    // Update progress
    progress_callback.call1(py, (100,))?;
    
    Ok(DynamicImage::ImageRgb8(rgb_image))
}

fn apply_blur(py: Python, image: DynamicImage, progress_callback: &PyObject) -> PyResult<DynamicImage> {
    let gaussian = imageproc::filter::gaussian_blur_f32(&image.to_rgb8(), 2.0);
    progress_callback.call1(py, (100,))?;
    Ok(DynamicImage::ImageRgb8(gaussian))
}

fn apply_sharpen(py: Python, image: DynamicImage, progress_callback: &PyObject) -> PyResult<DynamicImage> {
    let sharpened = image.unsharpen(1.0, 5);
    progress_callback.call1(py, (100,))?;
    Ok(sharpened)
}

fn apply_grayscale(py: Python, image: DynamicImage, progress_callback: &PyObject) -> PyResult<DynamicImage> {
    let grayscale = image.grayscale();
    progress_callback.call1(py, (100,))?;
    Ok(grayscale)
}

fn apply_sepia(py: Python, image: DynamicImage, progress_callback: &PyObject) -> PyResult<DynamicImage> {
    let rgb = image.to_rgb8();
    let mut sepia = ImageBuffer::new(rgb.width(), rgb.height());
    
    for (x, y, pixel) in rgb.enumerate_pixels() {
        let r = pixel[0] as f32;
        let g = pixel[1] as f32;
        let b = pixel[2] as f32;
        
        let sr = (0.393 * r + 0.769 * g + 0.189 * b).min(255.0) as u8;
        let sg = (0.349 * r + 0.686 * g + 0.168 * b).min(255.0) as u8;
        let sb = (0.272 * r + 0.534 * g + 0.131 * b).min(255.0) as u8;
        
        sepia.put_pixel(x, y, Rgb([sr, sg, sb]));
    }
    
    progress_callback.call1(py, (100,))?;
    Ok(DynamicImage::ImageRgb8(sepia))
}

fn apply_invert(py: Python, image: DynamicImage, progress_callback: &PyObject) -> PyResult<DynamicImage> {
    let rgb = image.to_rgb8();
    let mut inverted = ImageBuffer::new(rgb.width(), rgb.height());
    
    for (x, y, pixel) in rgb.enumerate_pixels() {
        inverted.put_pixel(x, y, Rgb([
            255 - pixel[0],
            255 - pixel[1],
            255 - pixel[2]
        ]));
    }
    
    progress_callback.call1(py, (100,))?;
    Ok(DynamicImage::ImageRgb8(inverted))
}

#[pymodule]
fn image_processor_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_image, m)?)?;
    Ok(())
} 