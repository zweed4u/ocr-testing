import PIL
import numpy
import subprocess
import pytesseract
import cv2
#from matplotlib import pyplot

# TODO: constructor stuff for image opening, class vars, os file check if on disk assertion, introduce config for image file, full path dir support
# binarization, denoising/noise reduction, 
class OCR_reading():
    MEDIA_FORMATS = ['gif', 'jpg', 'png']
    def __init__(self, image_file_name, needs_conversion=True, **kwargs):

        if needs_conversion:
            if 'tiff' != image_file_name[-4:].lower():
                print("Converting {} to TIFF...".format(image_file_name))
                #convert media to tiff with imagemagick
                if image_file_name[-3:].lower() in self.MEDIA_FORMATS:
                    command = "convert {} -auto-level -compress none {}.tiff".format(image_file_name, image_file_name.split(".")[0])
                #pdfs may need to be explicitly flattened
                elif 'pdf' in image_file_name.split(".")[-1].lower():
                    command = "convert {} -background white -flatten {}.tiff".format(image_file_name, image_file_name.split(".")[0])
                subprocess.call(command, shell=True)
                image_file_name = '{}.tiff'.format(image_file_name.split(".")[0])
            print("{} already in tiff format - skipping conversion...".format(image_file_name))

        self.image_file_name = image_file_name
        self.opened_image = PIL.Image.open(image_file_name)
        self.width = self.opened_image.size[0]
        self.height = self.opened_image.size[1]
        self.properties = kwargs

    """ WIP
    def denoise(self, filter_strength=10, color_filter_strength=10, template_window_size=7, search_window_size=21):
        img = cv2.imread(self.image_file_name)
        dst = cv2.fastNlMeansDenoisingColored(self.image_file_name, None, filter_strength, color_filter_strength, template_window_size, search_window_size)
        pyplot.subplot(121),pyplot.imshow(img)
        pyplot.subplot(122),pyplot.imshow(dst)
        pyplot.show()
    """
    """ WIP
    def adaptive_gauss_threshold_binarization(self):
        img = cv2.imread(self.image_file_name, 0)
        img = cv2.medianBlur(img, 5)
        th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        pyplot.subplot(121),pyplot.imshow(img)
        pyplot.subplot(122),pyplot.imshow(th3)
        plt.show()
    """

    def screenshot_is_not_a_solid_color(self):
        """
        Determine if the screenshot on the device is not a solid color
        :return: True if the screenshot is not a single solid color, False otherwise
        """
        print("Checking that image is not a single solid color...")
        extrema = self.opened_image.convert("L").getextrema()
        print("Extrema: {}".format(extrema))
        if extrema[0] == extrema[1]: # solid color - elements in tuple are the same
            return False
        return True

    def resize_screenshot_media_file(self, new_scaled_base_width=4096):
        """
        Resize a media file using PIL while maintaining aspect ratio
        :param new_base_width: int - default 4096 - 4x 1024 which is default base of media download
        :return: str - the new image file name of the resized/scaled image
        """
        print("Resizing/saving {0} to have a width of {1} as resized_{0}...".format(self.image_file_name, new_scaled_base_width))
        basewidth = new_scaled_base_width
        width_percent = (basewidth / float(self.opened_image.size[0]))
        height_size = int((float(self.opened_image.size[1]) * float(width_percent)))
        image = self.opened_image.resize((basewidth, height_size), PIL.Image.ANTIALIAS)
        image.save('resized_{0}'.format(self.image_file_name))
        return 'resized_{0}'.format(self.image_file_name)

    def image_to_bw(self, threshold_value=95):
        """
        Convert to grey scale and then scale to black and white
        :return: str - the new image file name of the bw image
        """
        grey_transform = self.opened_image.convert('L')
        bw_mapping = grey_transform.point(lambda x: 0 if x < threshold_value else 255, '1')
        bw_mapping.save("bw_{0}".format(self.image_file_name))
        return "bw_{0}".format(self.image_file_name)

    @property
    def get_ocr_text(self):
        """
        Return the OCR rendered text from the image via pytesseract
        :return: str - the text parsed from the image
        """
        print("Rendering image OCR...")
        text_in_image = pytesseract.image_to_string(self.opened_image)
        return text_in_image

    @property
    def get_media_files_original_width(self):
        """
        Get the width in pixels of an image
        :return: int - the width in pixels
        """
        return self.width

    @property
    def get_media_files_original_height(self):
        """
        Get the height in pixels of an image
        :return: int - the height in pixels
        """
        return self.height

    def get_properties(self):
        """
        Get the additional keyword arguments passed into the object
        :return: dict
        """
        return self.properties

    def get_property(self, key):
        """
        Get a single value from the keyword arguments passed to the object given the key
        :return: any type - value of the key in from the kwargs dictionary, returns None if key cannot be found
        """
        return self.properties.get(key, None)

# Debugging/tests
print("Original image instantiation...")
my_image = OCR_reading("test.jpg")
print("{} x {}".format(my_image.get_media_files_original_width, my_image.get_media_files_original_height))
assert my_image.screenshot_is_not_a_solid_color(), "Error Message: Media file supplied is a solid color"
saved_resized_image_name = my_image.resize_screenshot_media_file(my_image.get_media_files_original_width*4)
print(my_image.get_ocr_text)
print()

print("Resized image instantiation...")
my_scaled_image = OCR_reading(saved_resized_image_name)
print("{} x {}".format(my_scaled_image.get_media_files_original_width, my_scaled_image.get_media_files_original_height))
assert my_scaled_image.screenshot_is_not_a_solid_color(), "Error Message: Media file supplied is a solid color"
bw_resized_image_name = my_scaled_image.image_to_bw()
print(my_scaled_image.get_ocr_text)
print()

print("Black and white resized image instantiation...")
my_bw_scaled_image = OCR_reading(bw_resized_image_name)
print("{} x {}".format(my_bw_scaled_image.get_media_files_original_width, my_bw_scaled_image.get_media_files_original_height))
assert my_bw_scaled_image.screenshot_is_not_a_solid_color(), "Error Message: Media file supplied is a solid color"
print(my_bw_scaled_image.get_ocr_text)
