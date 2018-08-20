# Opensource_Sentinel2_download_processing_chain
Automization of Sentinel-2 data download and pre-processing, and adaptation of a semi-automatized image processing chain to Sentinel 2 data.

You will find on this repository the two main consecutive scripts:
- one which allows you to download Sentinel-2 data from the Copernicus Hub and to pre-process the images (download_preprocessing_sentinel2.py)
- the other, an adaptation of a Very High Resolution processing chain, which will process the resulting image of the first step (high resolution data). (geobia_chain.ipynb)

The last one helps the user have a better understanding of class separability. (ClassSeparability.ipynb)
