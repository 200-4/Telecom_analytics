#test_extraction.py
"""Test data extraction with watermarks"""
from src.extractor import DataExtractor
from src.watermark import WatermarkManager
import os

def main():
    print("\n" + "=" * 60)
    print("PART 1: INTERGRATION BASELINE TEST")
    print("=" * 60)

    #Initialize
    extractor = DataExtractor('telecom.db')
    watermark_mgr = WatermarkManager('telecom.db')

    #Show initial watermarks
    print("\n Before Extraction:")
    watermark_mgr.show_all_watermarks()

    #Extract data
    print("\n Extracting DATA ...")

    result_subscribers = extractor.extract_subscribers()
    result_cdr = extractor.extract_cdr()
    result_trans = extractor.extract_transactions()

    #Show updated watermarks
    print("\n After Extraction:")
    watermark_mgr.show_all_watermarks()

    #summary
    print("\n" + "=" * 60)
    print("SUMMARY OF EXTRACTION RESULTS")
    print("="*30)
    print(f"Subscribers Extracted: {result_subscribers['records_extracted']:,} ")
    print(f"CDR Records Extracted: {result_cdr['records_extracted']:,}")
    print(f"Transactions extracted: {result_trans['records_extracted']:,}")
    print(f"\n All extractions complete!")

if __name__ == "__main__":
    main()


    